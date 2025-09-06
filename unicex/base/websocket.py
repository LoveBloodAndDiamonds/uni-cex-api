__all__ = [
    "BaseSyncWebsocket",
    "BaseAsyncWebsocket",
]

import logging
import threading
from collections.abc import Callable

from websocket import WebSocket, WebSocketApp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseSyncWebsocket:
    """Базовый класс синхронного вебсокета."""

    def __init__(
        self,
        callback: Callable,
        url: str,
        subscribe_messages: list[str] | None = None,
        ping_interval: int | float | None = None,
        pong_interval: int | float | None = None,
        ping_message: str | None = None,
        pong_message: str | None = None,
    ) -> None:
        """Инициализация вебсокета."""
        self._callback = callback
        self._subscribe_messages = subscribe_messages or []
        self._ping_interval = ping_interval
        self._pong_interval = pong_interval
        self._ping_message = ping_message
        self._pong_message = pong_message

        self._ws = WebSocketApp(
            url=url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._ws_thread: threading.Thread | None = None

    def start(self) -> None:
        """Запустить вебсокет в потоке."""
        logger.info("Starting websocket")
        ws_kwargs = self._generate_ws_kwargs()
        self._ws_thread = threading.Thread(
            target=self._ws.run_forever, kwargs=ws_kwargs, daemon=True
        )
        self._ws_thread.start()

    def _generate_ws_kwargs(self) -> dict:
        """Генерирует аргументы для запуска вебсокета."""
        ws_kwargs = {}
        if self._ping_interval:
            ws_kwargs["ping_interval"] = self._ping_interval
        if self._ping_message:
            ws_kwargs["ping_payload"] = self._ping_message
        return ws_kwargs

    def stop(self) -> None:
        """Останавливает вебсокет и поток."""
        logger.info("Stopping websocket")
        if self._ws:
            self._ws.close()  # отправляем "close frame"
        if self._ws_thread and self._ws_thread.is_alive():
            self._ws_thread.join(timeout=5)  # ждём завершения потока
            self._ws_thread = None

    def _on_open(self, ws: WebSocket) -> None:
        """Обработчик события открытия вебсокета."""
        logger.info("Websocket opened")
        for subscribe_message in self._subscribe_messages:
            ws.send_text(subscribe_message)

    def _on_message(self, _: WebSocket, message: str | dict) -> None:
        """Обработчик события получения сообщения."""
        self._callback(message)

    def _on_error(self, ws: WebSocket, error: Exception) -> None:
        """Обработчик события ошибки вебсокета."""
        logger.error(f"Websocket error: {error}")

    def _on_close(self, ws: WebSocket, status_code: int, reason: str) -> None:
        """Обработчик события закрытия вебсокета."""
        logger.info(f"Websocket closed with status code {status_code} and reason {reason}")

    def _on_ping(self, ws: WebSocket, message: str) -> None:
        """Обработчик события получения пинга."""
        logger.info(f"Websocket received ping: {message}")
        if self._pong_message:
            ws.pong(self._pong_message)
        else:
            ws.pong()


class BaseAsyncWebsocket:
    """Базовый класс асинхронного вебсокета."""

    pass
