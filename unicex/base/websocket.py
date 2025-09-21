__all__ = [
    "BaseWebsocket",
    "BaseAioWebsocket",
]

import json
import logging
import threading
import time
from collections.abc import Callable

from websocket import WebSocket, WebSocketApp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseWebsocket:
    """Базовый класс синхронного вебсокета."""

    def __init__(
        self,
        callback: Callable,
        url: str,
        subscription_messages: list[dict] | list[str] | None = None,
        ping_interval: int | float | None = 10,
        ping_message: str | None = None,
        pong_message: str | None = None,
        no_message_reconnect_timeout: int | float | None = 60,
    ) -> None:
        """Инициализация вебсокета.

        Параметры:
            callback (Callable): Функция обратного вызова для обработки сообщений.
            subscription_messages (list[dict] | list[str] | None): Список сообщений для подписки.
            ping_interval (int | float | None): Интервал отправки пинга (сек.).
            ping_message (str | None): Сообщение для пинга.
            pong_message (str | None): Сообщение для погна.
            no_message_reconnect_timeout (int | float | None): Время ожидания без сообщений для переподключения (сек.).
        """
        self._callback = callback
        self._subscription_messages = subscription_messages or []
        self._ping_interval = ping_interval
        self._ping_message = ping_message
        self._pong_message = pong_message
        self._no_message_reconnect_timeout = no_message_reconnect_timeout
        self._last_message_timestamp = time.monotonic()
        self._healthcheck_thread: threading.Thread | None = None
        self._ws_thread: threading.Thread | None = None
        self._ws = WebSocketApp(
            url=url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self._running = True

    def start(self) -> None:
        """Запустить вебсокет в потоке."""
        logger.info("Starting websocket")

        # Запускаем вебсокет
        self._ws_thread = threading.Thread(
            target=self._ws.run_forever,
            kwargs=self._generate_ws_kwargs(),
            daemon=True,
        )
        self._ws_thread.start()

        # Запускаем поток для проверки времени последнего сообщения
        self._healthcheck_thread = threading.Thread(
            target=self._healthcheck,
            daemon=True,
        )
        self._healthcheck_thread.start()

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
        self._running = False

        try:
            if isinstance(self._healthcheck_thread, threading.Thread):
                self._healthcheck_thread.join(timeout=1)
        except Exception as e:
            logger.error(f"Error stopping healthcheck thread: {e}")

        try:
            if self._ws:
                self._ws.close()  # отправляем "close frame"
        except Exception as e:
            logger.error(f"Error closing websocket: {e}")

        try:
            if self._ws_thread and self._ws_thread.is_alive():
                self._ws_thread.join(timeout=5)  # ждём завершения потока
                self._ws_thread = None
        except Exception as e:
            logger.error(f"Error stopping websocket thread: {e}")

    def _on_open(self, ws: WebSocket) -> None:
        """Обработчик события открытия вебсокета."""
        logger.info("Websocket opened")
        for subscription_message in self._subscription_messages:
            if isinstance(subscription_message, dict):
                subscription_message = json.dumps(subscription_message)  # noqa: PLW2901
            ws.send(subscription_message)

    def _on_message(self, _: WebSocket, message: str) -> None:
        """Обработчик события получения сообщения."""
        try:
            message = json.loads(message)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {message}, error: {e}")
            return
        self._last_message_timestamp = time.monotonic()
        self._callback(message)

    def _on_error(self, _: WebSocket, error: Exception) -> None:
        """Обработчик события ошибки вебсокета."""
        logger.error(f"Websocket error: {error}")

    def _on_close(self, _: WebSocket, status_code: int, reason: str) -> None:
        """Обработчик события закрытия вебсокета."""
        logger.info(f"Websocket closed with status code {status_code} and reason {reason}")

    def _on_ping(self, ws: WebSocket, message: str) -> None:
        """Обработчик события получения пинга."""
        logger.info(f"Websocket received ping: {message}")
        if self._pong_message:
            ws.pong(self._pong_message)
        else:
            ws.pong()

    def _healthcheck(self) -> None:
        """Проверка работоспособности вебсокета исходя из времени последнего сообщения."""
        if not self._no_message_reconnect_timeout:
            return

        while self._running:
            try:
                if (
                    time.monotonic() + self._no_message_reconnect_timeout
                    > self._last_message_timestamp
                ):
                    logger.error("Websocket is not responding")
            except Exception as e:
                logger.error(f"Error checking websocket health: {e}")
            time.sleep(1)


class BaseAioWebsocket:
    """Базовый класс асинхронного вебсокета."""

    pass
