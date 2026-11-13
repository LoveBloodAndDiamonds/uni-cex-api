__all__ = ["UserWebsocket"]

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import orjson
from loguru import logger as _logger
from websockets.asyncio.client import ClientConnection

from unicex._base import Websocket
from unicex.exceptions import NotAuthorized, NotSupported
from unicex.types import LoggerLike
from unicex.utils import generate_hmac_sha256_signature

from .client import Client


class _SpotUserDataWebsocket(Websocket):
    """Вебсокет WebSocket API Binance, подписанный на User Data Stream через подпись.

    Подписка (`userDataStream.subscribe.signature`) формируется заново при каждом
    подключении, чтобы `timestamp` в подписи был свежим и после реконнекта.
    """

    def __init__(
        self,
        callback: Callable[[Any], Awaitable[None]],
        url: str,
        api_key: str,
        api_secret: str,
        event_filter: dict[str, list[str]] | None = None,
        recv_window: int = 5000,
        **kwargs: Any,
    ) -> None:
        """Инициализирует вебсокет пользовательских данных спота."""
        super().__init__(callback=callback, url=url, **kwargs)
        self._api_key = api_key
        self._api_secret = api_secret
        self._event_filter = event_filter
        self._recv_window = recv_window

    def _subscribe_message(self) -> str:
        """Формирует подписанное сообщение `userDataStream.subscribe.signature`."""
        params: dict[str, Any] = {
            "apiKey": self._api_key,
            "recvWindow": self._recv_window,
            "timestamp": int(time.time() * 1000),
        }
        if self._event_filter:
            # Ключи фильтра сортируются, JSON без пробелов — иначе подпись не совпадёт
            params["filter"] = orjson.loads(
                orjson.dumps(self._event_filter, option=orjson.OPT_SORT_KEYS)
            )
        payload = "&".join(
            f"{k}={orjson.dumps(v, option=orjson.OPT_SORT_KEYS).decode() if isinstance(v, dict) else v}"
            for k, v in sorted(params.items())
        )
        params["signature"] = generate_hmac_sha256_signature(self._api_secret, payload, "hex")
        return orjson.dumps(
            {
                "id": str(uuid.uuid4()),
                "method": "userDataStream.subscribe.signature",
                "params": params,
            }
        ).decode()

    async def _send_subscribe_messages(self, conn: ClientConnection) -> None:
        """Отправляет свежеподписанную подписку на User Data Stream."""
        await conn.send(self._subscribe_message())
        self._logger.debug("Sent userDataStream.subscribe.signature")


class UserWebsocket:
    """Пользовательский вебсокет Binance.

    Поддержка типов аккаунта:
    - "SPOT" — через WebSocket API (`userDataStream.subscribe.signature`). Спотовый listenKey
      Binance удалил 2026-02-20.
    - "FUTURES" (USDT‑M фьючерсы) — через listenKey с авто‑продлением.

    В callback приходят события в том же формате, что и раньше через listenKey
    (`{"e": "executionReport", ...}`), без обёртки `{"subscriptionId": ..., "event": ...}`.
    """

    _BASE_SPOT_WS_API_URL: str = "wss://ws-api.binance.com:443/ws-api/v3"
    """URL WebSocket API спота (через него идёт User Data Stream)."""

    _BASE_FUTURES_PRIVATE_URL: str = "wss://fstream.binance.com/private"
    """Приватный endpoint фьючерсов (listenKey, пользовательские данные)."""

    _RENEW_INTERVAL: int = 30 * 60
    """Интервал продления listenKey (сек.)"""

    def __init__(
        self,
        callback: Callable[[Any], Awaitable[None]],
        client: Client,
        type: Literal["SPOT", "FUTURES"],
        logger: LoggerLike | None = None,
        event_filter: dict[str, list[str]] | None = None,
        **kwargs: Any,  # Не дадим сломаться, если юзер передал ненужные аргументы
    ) -> None:
        """Инициализирует пользовательский вебсокет для работы с биржей Binance.

        Параметры:
            callback (`Callable`): Асинхронная функция обратного вызова, которая принимает сообщение с вебсокета.
            client (`Client`): Авторизованный клиент Binance.
            type (`str`): Тип аккаунта ("SPOT" | "FUTURES").
            logger (`LoggerLike | None`): Логгер для записи логов.
            event_filter (`dict[str, list[str]] | None`): Только для "SPOT": фильтр событий
                (ключи `e`, `s`, `a`, `x`), например `{"e": ["executionReport"]}`.
        """
        self._callback = callback
        self._client = client
        self._type = type
        self._event_filter = event_filter

        self._listen_key: str | None = None
        self._ws: Websocket | None = None
        self._keepalive_task: asyncio.Task | None = None

        self._logger = logger or _logger

        self._running = False

    @classmethod
    def _create_ws_url(cls, type: Literal["SPOT", "FUTURES"], listen_key: str) -> str:
        """Создает URL для подключения к WebSocket по listenKey."""
        if type == "FUTURES":
            return f"{cls._BASE_FUTURES_PRIVATE_URL}/ws?listenKey={listen_key}"
        raise NotSupported(f"Account type '{type}' not supported")

    async def start(self) -> None:
        """Запускает пользовательский стрим (блокирует до остановки, как и `Websocket.start`)."""
        if self._running:
            return
        self._running = True

        if self._type == "SPOT":
            await self._start_spot_ws()
            return

        try:
            self._listen_key = await self._create_listen_key()
            # Продление запускается до подключения: `Websocket.start()` блокирует до остановки.
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())
            await self._start_ws(self._create_ws_url("FUTURES", self._listen_key))
        except Exception:
            self._running = False
            await self._stop_keepalive_task()
            await self._close_listen_key_safe()
            raise

    async def stop(self) -> None:
        """Останавливает стрим и закрывает listenKey."""
        self._running = False

        try:
            if isinstance(self._ws, Websocket):
                await self._ws.stop()
        except Exception as e:
            self._logger.error(f"Error stopping WebSocket: {e}")
        finally:
            self._ws = None

        await self._stop_keepalive_task()
        await self._close_listen_key_safe()

        self._logger.info("User websocket stopped")

    async def restart(self) -> None:
        """Перезапускает WebSocket для User Data Stream."""
        await self.stop()
        await self.start()

    async def _start_spot_ws(self) -> None:
        """Запускает User Data Stream спота через WebSocket API."""
        api_key = self._client._api_key  # type: ignore[attr-defined]
        api_secret = self._client._api_secret  # type: ignore[attr-defined]
        if not api_key or not api_secret:
            self._running = False
            raise NotAuthorized("Api key and api secret is required for user data stream")
        self._ws = _SpotUserDataWebsocket(
            callback=self._spot_callback,
            url=self._BASE_SPOT_WS_API_URL,
            api_key=api_key,
            api_secret=api_secret,
            event_filter=self._event_filter,
            no_message_reconnect_timeout=None,
            logger=self._logger,
        )
        await self._ws.start()

    async def _spot_callback(self, message: dict) -> None:
        """Разворачивает события WebSocket API и обрабатывает ответы на подписку."""
        event = message.get("event")
        if event is not None:
            await self._callback(event)
            return
        status = message.get("status")
        if status == 200:
            self._logger.info(f"User data stream subscribed: {message.get('result')}")
        elif status is not None:
            self._logger.error(f"User data stream subscription failed: {message}")

    async def _start_ws(self, ws_url: str) -> None:
        """Запускает WebSocket для User Data Stream по listenKey."""
        self._ws = Websocket(
            callback=self._callback,
            url=ws_url,
            no_message_reconnect_timeout=None,
            logger=self._logger,
        )
        self._logger.info(f"User websocket starting: ...{ws_url[-5:]}")
        await self._ws.start()

    async def _keepalive_loop(self) -> None:
        """Фоновый цикл продления listenKey; при смене ключа или ошибке — перезапуск."""
        while self._running:
            # Ждём до следующего продления с возможностью быстрого выхода
            for _ in range(self._RENEW_INTERVAL):
                if not self._running:
                    return
                await asyncio.sleep(1)

            try:
                response = await self._renew_listen_key()
                listen_key = response.get("listenKey") if isinstance(response, dict) else None
                if not listen_key:
                    raise RuntimeError(f"Can not renew listenKey: {response}")
                if listen_key != self._listen_key:
                    self._logger.info(
                        f"Listen key changed: {self._listen_key} -> {listen_key}. Restarting websocket"
                    )
                    asyncio.create_task(self.restart())
                    return
            except Exception as e:
                self._logger.error(f"Error while keeping alive: {e}")
                asyncio.create_task(self.restart())
                return

    async def _stop_keepalive_task(self) -> None:
        """Останавливает фоновую задачу продления listenKey."""
        if not isinstance(self._keepalive_task, asyncio.Task):
            return
        keepalive_task = self._keepalive_task
        self._keepalive_task = None
        keepalive_task.cancel()
        if keepalive_task is asyncio.current_task():
            return
        try:
            await keepalive_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self._logger.error(f"Error stopping keepalive task: {e}")

    async def _close_listen_key_safe(self) -> None:
        """Закрывает listenKey, если он был создан, не пробрасывая ошибки."""
        try:
            if self._listen_key:
                await self._close_listen_key(self._listen_key)
        except Exception as e:
            self._logger.error(f"Error closing listenKey: {e}")
        finally:
            self._listen_key = None

    async def _create_listen_key(self) -> str:
        """Создает новый listenKey для User Data Stream фьючерсов."""
        if self._type != "FUTURES":
            raise NotSupported(f"Account type '{self._type}' not supported")
        resp = await self._client.futures_listen_key()
        key = resp.get("listenKey") if isinstance(resp, dict) else None
        if not key:
            raise RuntimeError(f"Can not create listenKey: {resp}")
        return key

    async def _renew_listen_key(self) -> dict:
        """Продлевает listenKey фьючерсов. Возвращает ответ с актуальным ключом."""
        if self._type != "FUTURES":
            raise NotSupported(f"Account type '{self._type}' not supported")
        return await self._client.futures_renew_listen_key()

    async def _close_listen_key(self, listen_key: str) -> None:
        """Закрывает listenKey фьючерсов."""
        if self._type != "FUTURES":
            raise NotSupported(f"Account type '{self._type}' not supported")
        await self._client.futures_close_listen_key()
