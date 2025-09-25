__all__ = ["Websocket"]

import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Any

import orjson
from loguru import logger as _logger
from websocket import WebSocket, WebSocketApp

from unicex.exceptions import QueueOverflowError
from unicex.types import LoggerLike


class Websocket:
    """Базовый класс синхронного вебсокета."""

    MAX_QUEUE_SIZE: int = 100
    """Максимальная длина очереди."""

    def __init__(
        self,
        callback: Callable[[Any], None],
        url: str,
        subscription_messages: list[dict] | list[str] | None = None,
        ping_interval: int | float | None = 10,
        ping_message: str | None = None,
        pong_message: str | None = None,
        no_message_reconnect_timeout: int | float | None = 60,
        reconnect_timeout: int | float | None = 5,
        worker_count: int = 2,
        logger: LoggerLike | None = None,
        **kwargs: Any,  # Не дадим сломаться, если юзер передал ненужные аргументы
    ) -> None:
        """Инициализация вебсокета.

        Параметры:
            callback (`Callable[[Any], None]`): Обработчик входящих сообщений.
            url (`str`): URL вебсокета.
            subscription_messages (`list[dict] | list[str] | None`): Сообщения для подписки после подключения.
            ping_interval (`int | float | None`): Интервал отправки ping, сек.
            ping_message (`str | None`): Сообщение для ping (если не указано — используется ping‑frame).
            pong_message (`str | None`): Сообщение для pong (если не указано — используется pong‑frame).
            no_message_reconnect_timeout (`int | float | None`): Таймаут без сообщений до рестарта, сек.
            reconnect_timeout (`int | float | None`): Пауза перед переподключением, сек.
            worker_count (`int`): Количество рабочих потоков.
            logger (`LoggerLike | None`): Логгер для записи логов.
        """
        self._callback = callback
        self._subscription_messages = subscription_messages or []
        self._ping_interval = ping_interval
        self._ping_message = ping_message
        self._pong_message = pong_message
        self._no_message_reconnect_timeout = no_message_reconnect_timeout
        self._logger = logger or _logger
        self._reconnect_timeout = reconnect_timeout or 0
        self._last_message_time: float | None = None
        self._healthcheck_thread: threading.Thread | None = None
        self._ws_thread: threading.Thread | None = None
        self._ws = WebSocketApp(
            url=url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        # Очередь сообщений
        self._queue: deque = deque()
        self._queue_lock = threading.Lock()

        # Воркеры
        self._worker_count = worker_count
        self._workers: list[threading.Thread] = []

        self._running = False

    def start(self) -> None:
        """Запускает вебсокет в отдельном потоке."""
        # Проверяем что вебсокет еще не запущен
        if self._running:
            raise RuntimeError("Websocket is already running")
        self._running = True

        self._logger.info("Starting websocket")

        # Запускаем вебсокет
        self._ws_thread = threading.Thread(
            target=self._ws.run_forever,
            name="WebsocketThread",
            kwargs=self._generate_ws_kwargs(),
            daemon=True,
        )
        self._ws_thread.start()

        # Инициализируем время последнего сообщения
        self._last_message_time = time.monotonic()

        # Запускаем поток для проверки времени последнего сообщения
        self._healthcheck_thread = threading.Thread(
            target=self._healthcheck_task,
            name="WebsocketHealthcheckThread",
            daemon=True,
        )
        self._healthcheck_thread.start()

        # Запускаем воркеров
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker,
                name=f"WebsocketWorkerThread-{i}",
                daemon=True,
            )
            self._workers.append(worker)
            worker.start()

    def stop(self) -> None:
        """Останавливает вебсокет и поток."""
        self._logger.info("Stopping websocket")
        self._running = False

        # Останавливаем поток проверки последнего времени сообщения
        try:
            if isinstance(self._healthcheck_thread, threading.Thread):
                self._healthcheck_thread.join(timeout=1)
        except Exception as e:
            self._logger.error(f"Error stopping healthcheck thread: {e}")

        # Останавилваем вебсокет
        try:
            if self._ws:
                self._ws.close()  # отправляем "close frame"
        except Exception as e:
            self._logger.error(f"Error closing websocket: {e}")

        # Ждем остановки вебсокета
        try:
            if self._ws_thread and self._ws_thread.is_alive():
                self._ws_thread.join(timeout=5)  # ждём завершения потока
                self._ws_thread = None
        except Exception as e:
            self._logger.error(f"Error stopping websocket thread: {e}")

        # Ждем остановки воркеров
        for worker in self._workers:
            try:
                if worker.is_alive():
                    worker.join(timeout=1)
            except Exception as e:
                self._logger.error(f"Error stopping worker: {e}")
        self._workers.clear()

    def restart(self) -> None:
        """Перезапускает вебсокет."""
        self.stop()
        time.sleep(self._reconnect_timeout)
        self.start()

    def _worker(self) -> None:
        """Цикл обработки сообщений из очереди."""
        while self._running:
            try:
                with self._queue_lock:
                    if not self._queue:
                        time.sleep(0.01)
                        continue
                    message = self._queue.popleft()

                self._callback(message)
            except Exception as e:
                self._logger.error(f"Error in worker: {e}")
            time.sleep(0.01)  # чтобы не крутиться на пустой очереди

    def _generate_ws_kwargs(self) -> dict:
        """Генерирует аргументы для запуска вебсокета."""
        ws_kwargs = {}
        if self._ping_interval:
            ws_kwargs["ping_interval"] = self._ping_interval
        if self._ping_message:
            ws_kwargs["ping_payload"] = self._ping_message
        return ws_kwargs

    def _on_open(self, ws: WebSocket) -> None:
        """Обработчик события открытия вебсокета."""
        self._logger.info("Websocket opened")
        for subscription_message in self._subscription_messages:
            if isinstance(subscription_message, dict):
                subscription_message = orjson.dumps(subscription_message)  # noqa: PLW2901
            ws.send(subscription_message)

    def _on_message(self, _: WebSocket, message: str) -> None:
        """Обработчик события получения сообщения."""
        try:
            message = orjson.loads(message)
        except orjson.JSONDecodeError as e:
            if message in ["ping", "pong"]:
                self._logger.debug(f"{self} Received ping message: {message}")
            else:
                self._logger.error(f"Failed to decode JSON message: {message}, error: {e}")

        self._last_message_time = time.monotonic()

        with self._queue_lock:
            if len(self._queue) >= self.MAX_QUEUE_SIZE:
                raise QueueOverflowError("Message queue is overflow")
            self._queue.append(message)

    def _on_error(self, _: WebSocket, error: Exception) -> None:
        """Обработчик события ошибки вебсокета."""
        self._logger.error(f"Websocket error: {error}")
        self.restart()

    def _on_close(self, _: WebSocket, status_code: int, reason: str) -> None:
        """Обработчик события закрытия вебсокета."""
        self._logger.info(f"Websocket closed with status code {status_code} and reason {reason}")

    def _on_ping(self, ws: WebSocket, message: str) -> None:
        """Обработчик события получения ping."""
        self._logger.info(f"Websocket received ping: {message}")
        if self._pong_message:
            ws.pong(self._pong_message)
        else:
            ws.pong()

    def _healthcheck_task(self) -> None:
        """Проверяет работоспособность по времени последнего сообщения."""
        if not self._no_message_reconnect_timeout:
            return

        while self._running:
            try:
                if time.monotonic() - self._last_message_time > self._no_message_reconnect_timeout:  # type: ignore
                    self._logger.error("Websocket no message timeout triggered")
                    self.restart()
            except Exception as e:
                self._logger.error(f"Error checking websocket health: {e}")
            time.sleep(1)
