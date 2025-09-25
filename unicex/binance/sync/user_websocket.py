__all__ = ["UserWebsocket"]

import threading
import time
from collections.abc import Callable
from typing import Any

from loguru import logger as _logger

from unicex._base import Websocket
from unicex.exceptions import NotSupported
from unicex.types import LoggerLike

from .._mixins import UserWebsocketMixin
from ..types import AccountType
from .client import Client


class UserWebsocket(UserWebsocketMixin):
    """Пользовательский вебсокет Binance с авто‑продлением listenKey.

    Поддержка типов аккаунта: "SPOT" и "FUTURES" (USDT‑M фьючерсы).
    """

    def __init__(
        self,
        callback: Callable[[Any], None],
        client: Client,
        type: AccountType,
        logger: LoggerLike | None = None,
        **kwargs: Any,  # Не дадим сломаться, если юзер передал ненужные аргументы
    ) -> None:
        """Инициализирует пользовательский вебсокет.

        Параметры:
            callback (`Callable`): Функция обратного вызова, которая принимает сообщение с вебсокета.
            client (`Client`): Авторизованный клиент Binance.
            type (`AccountType`): Тип аккаунта ("SPOT" | "FUTURES").
            logger (`LoggerLike | None`): Логгер для записи логов.
        """
        self._callback = callback
        self._client = client
        self._type = type

        self._listen_key: str | None = None
        self._ws: Websocket | None = None
        self._keepalive_thread: threading.Thread | None = None

        self._logger = logger or _logger

        self._running = False

    def start(self) -> None:
        """Запускает пользовательский стрим с автопродлением listenKey."""
        self._running = True
        self._listen_key = self._create_listen_key()
        self._start_ws(self._create_ws_url(self._type, self._listen_key))  # type: ignore

        # Фоновое продление ключа прослушивания
        self._keepalive_thread = threading.Thread(
            target=self._keepalive_loop, name="WebsocketKeepaliveThread", daemon=True
        )
        self._keepalive_thread.start()

    def stop(self) -> None:
        """Останавливает стрим и закрывает listenKey."""
        self._running = False

        # Останавливаем вебсокет
        try:
            if isinstance(self._ws, Websocket):
                self._ws.stop()
        except Exception as e:
            self._logger.error(f"Error stopping WebSocket: {e}")

        # Ожидаем завершения фонового продления ключа прослушивания
        if isinstance(self._keepalive_thread, threading.Thread):
            self._keepalive_thread.join()

        # Закрываем ключ прослушивания
        try:
            if self._listen_key:
                self._close_listen_key(self._listen_key)
        except Exception as e:
            self._logger.error(f"Error closing listenKey: {e}")
        finally:
            self._listen_key = None

        self._logger.info("User websocket stopped")

    def restart(self) -> None:
        """Перезапускает WebSocket для User Data Stream."""
        self.stop()
        self.start()

    def _start_ws(self, ws_url: str) -> None:
        """Запускает WebSocket для User Data Stream."""
        self._ws = Websocket(callback=self._callback, url=ws_url, no_message_reconnect_timeout=None)
        self._ws.start()
        self._logger.info(f"User websocket started: ...{ws_url[-5:]}")

    def _keepalive_loop(self) -> None:
        """Фоновый цикл продления listenKey и восстановления сессии при необходимости."""
        while self._running:
            try:
                if self._type == "FUTURES":
                    response = self._renew_listen_key()
                    listen_key = response.get("listenKey")
                    if not listen_key:
                        raise RuntimeError(f"Can not renew listenKey: {response}")

                    if listen_key != self._listen_key:
                        self._logger.info(
                            f"Listen key changed: {self._listen_key} -> {listen_key}. Restarting websocket"
                        )
                        return self.restart()

                elif self._type == "SPOT":
                    self._renew_listen_key()

                else:
                    raise NotSupported(f"Account type '{self._type}' not supported")

            except Exception as e:
                self._logger.error(f"Error while keeping alive: {e}")
                return self.restart()

            # Ждём до следующего продления
            for _ in range(self._RENEW_INTERVAL):
                if self._running:
                    return
                time.sleep(1)

    def _create_listen_key(self) -> str:
        """Создает новый listenKey для User Data Stream в зависимости от типа аккаунта."""
        if self._type == "FUTURES":
            resp = self._client.futures_listen_key()
        elif self._type == "SPOT":
            resp = self._client.listen_key()
        else:
            raise NotSupported(f"Account type '{self._type}' not supported")

        key = resp.get("listenKey")
        if not key:
            raise RuntimeError(f"Can not create listenKey: {resp}")
        return key

    def _renew_listen_key(self) -> dict:
        """Продлевает listenKey. Возвращает новый ключ, если сервер его выдал."""
        if not isinstance(self._listen_key, str):
            raise RuntimeError("listenKey is not a string")
        if self._type == "FUTURES":
            return self._client.futures_renew_listen_key()
        elif self._type == "SPOT":
            return self._client.renew_listen_key(self._listen_key)
        else:
            raise NotSupported(f"Account type '{self._type}' not supported")

    def _close_listen_key(self, listen_key: str) -> None:
        """Закрывает listenKey."""
        if self._type == "FUTURES":
            self._client.futures_close_listen_key()
        elif self._type == "SPOT":
            self._client.close_listen_key(listen_key)
        else:
            raise NotSupported(f"Account type '{self._type}' not supported")
