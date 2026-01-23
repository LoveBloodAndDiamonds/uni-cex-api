__all__ = ["UserWebsocket"]

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger as _logger

from unicex._base import Websocket
from unicex.types import LoggerLike

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class UserWebsocket:
    """Пользовательский вебсокет Aster с авто-продлением listenKey.

    Работает только с фьючерсным пользовательским стримом.
    """

    _BASE_FUTURES_URL: str = "wss://fstream.asterdex.com"
    """Базовый URL для пользовательского вебсокета Aster."""

    _RENEW_INTERVAL: int = 30 * 60
    """Интервал продления listenKey (сек.)."""

    def __init__(
        self,
        callback: CallbackType,
        client: Client,
        logger: LoggerLike | None = None,
        **kwargs: Any,
    ) -> None:
        """Инициализирует пользовательский вебсокет Aster.

        - Параметры:
        callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
        client (`Client`): Авторизованный клиент Aster.
        logger (`LoggerLike | None`): Логгер для записи логов.
        kwargs (`dict[str, Any]`): Дополнительные параметры, которые будут переданы в `Websocket`.

        Возвращает:
            `None`: Ничего не возвращает.
        """
        self._callback = callback
        self._client = client
        self._logger = logger or _logger
        self._ws_kwargs = kwargs

        self._listen_key: str | None = None
        self._ws: Websocket | None = None
        self._keepalive_task: asyncio.Task | None = None

        self._running = False

    async def start(self) -> None:
        """Запускает пользовательский стрим с автопродлением listenKey."""
        if self._running:
            return

        self._running = True

        # Создаем listenKey, запускаем keepalive и вебсокет.
        try:
            self._listen_key = await self._create_listen_key()

            # Запускаем фоновое продление ключа до подключения.
            self._keepalive_task = asyncio.create_task(self._keepalive_loop())

            await self._start_ws(self._listen_key)
        except Exception:
            # Если старт не удался - сбрасываем состояние и чистим ресурсы.
            self._running = False
            await self._stop_keepalive_task()
            if self._listen_key:
                try:
                    await self._close_listen_key()
                except Exception as exc:
                    self._logger.error(f"Error closing listenKey: {exc}")
                finally:
                    self._listen_key = None
            raise

    async def stop(self) -> None:
        """Останавливает пользовательский стрим и закрывает listenKey."""
        self._running = False

        # Останавливаем вебсокет.
        try:
            if isinstance(self._ws, Websocket):
                await self._ws.stop()
        except Exception as exc:
            self._logger.error(f"Error stopping websocket: {exc}")
        finally:
            self._ws = None

        # Останавливаем фоновое продление ключа.
        await self._stop_keepalive_task()

        # Закрываем listenKey.
        try:
            if self._listen_key:
                await self._close_listen_key()
        except Exception as exc:
            self._logger.error(f"Error closing listenKey: {exc}")
        finally:
            self._listen_key = None

        self._logger.info("User websocket stopped")

    async def restart(self) -> None:
        """Перезапускает пользовательский вебсокет."""
        await self.stop()
        await self.start()

    async def _start_ws(self, listen_key: str) -> None:
        """Запускает WebSocket соединение."""
        ws_url = f"{self._BASE_FUTURES_URL}/ws/{listen_key}"
        self._ws_kwargs["no_message_reconnect_timeout"] = None
        self._ws = Websocket(
            callback=self._callback,
            url=ws_url,
            **self._ws_kwargs,
        )
        await self._ws.start()
        self._logger.info(f"User websocket started: ...{ws_url[-5:]}")

    async def _keepalive_loop(self) -> None:
        """Фоновый цикл продления listenKey."""
        while self._running:
            try:
                response = await self._renew_listen_key()
                listen_key = response.get("listenKey") if isinstance(response, dict) else None

                # Если сервер вернул новый listenKey - перезапускаем соединение.
                if listen_key and listen_key != self._listen_key:
                    self._logger.info(
                        f"Listen key changed: {self._listen_key} -> {listen_key}. Restarting websocket"
                    )
                    asyncio.create_task(self.restart())
                    return

            except Exception as exc:
                self._logger.error(f"Error while keeping alive: {exc}")
                asyncio.create_task(self.restart())
                return

            # Ждем до следующего продления с возможностью быстрого выхода.
            for _ in range(self._RENEW_INTERVAL):
                if not self._running:
                    return
                await asyncio.sleep(1)

    async def _stop_keepalive_task(self) -> None:
        """Останавливает фоновую задачу продления listenKey."""
        if not isinstance(self._keepalive_task, asyncio.Task):
            return

        current_task = asyncio.current_task()
        keepalive_task = self._keepalive_task
        self._keepalive_task = None
        keepalive_task.cancel()

        if keepalive_task is current_task:
            return

        try:
            await keepalive_task
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            self._logger.error(f"Error stopping keepalive task: {exc}")

    async def _create_listen_key(self) -> str:
        """Создает новый listenKey."""
        response = await self._client.futures_listen_key()
        key = response.get("listenKey") if isinstance(response, dict) else None
        if not key:
            raise RuntimeError(f"Can not create listenKey: {response}")
        return key

    async def _renew_listen_key(self) -> dict:
        """Продлевает listenKey."""
        response = await self._client.futures_renew_listen_key()
        return response if isinstance(response, dict) else {}

    async def _close_listen_key(self) -> None:
        """Закрывает listenKey."""
        await self._client.futures_close_listen_key()
