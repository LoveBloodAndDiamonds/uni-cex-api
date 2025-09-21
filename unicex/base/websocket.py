__all__ = [
    "BaseWebsocket",
    "BaseAioWebsocket",
]

import asyncio
import logging
import threading
import time
from collections import deque
from collections.abc import Callable

import orjson
import websockets  # async
from websocket import WebSocket, WebSocketApp  # sync
from websockets.asyncio.client import ClientConnection

from unicex.exceptions import QueueOverflowError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BaseWebsocket:
    """Базовый класс синхронного вебсокета."""

    MAX_QUEUE_SIZE: int = 100
    """Максимальная длина очереди."""

    def __init__(
        self,
        callback: Callable,
        url: str,
        subscription_messages: list[dict] | list[str] | None = None,
        ping_interval: int | float | None = 10,
        ping_message: str | None = None,
        pong_message: str | None = None,
        no_message_reconnect_timeout: int | float | None = 60,
        reconnect_timeout: int | float | None = 5,
        worker_count: int = 2,
    ) -> None:
        """Инициализация вебсокета.

        Параметры:
            callback (Callable): Функция обратного вызова для обработки сообщений.
            subscription_messages (list[dict] | list[str] | None): Список сообщений для подписки.
            ping_interval (int | float | None): Интервал отправки пинга (сек.).
            ping_message (str | None): Сообщение для пинга, если не указано - отправляется обычный PING FRAME.
            pong_message (str | None): Сообщение для погна, если не указано - отправляется обычный PONG FRAME.
            no_message_reconnect_timeout (int | float | None): Время ожидания без сообщений для переподключения (сек.).
            reconnect_timeout (int | float | None): Время ожидания переподключения (сек.).
            worker_count (int): Количество потоков для обработки сообщений.
        """
        self._callback = callback
        self._subscription_messages = subscription_messages or []
        self._ping_interval = ping_interval
        self._ping_message = ping_message
        self._pong_message = pong_message
        self._no_message_reconnect_timeout = no_message_reconnect_timeout
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
        """Запустить вебсокет в потоке."""
        # Проверяем что вебсокет еще не запущен
        if self._running:
            raise RuntimeError("Websocket is already running")
        self._running = True

        logger.info("Starting websocket")

        # Запускаем вебсокет
        self._ws_thread = threading.Thread(
            target=self._ws.run_forever,
            kwargs=self._generate_ws_kwargs(),
            daemon=True,
        )
        self._ws_thread.start()

        # Инициализируем время последнего сообщения
        self._last_message_time = time.monotonic()

        # Запускаем поток для проверки времени последнего сообщения
        self._healthcheck_thread = threading.Thread(
            target=self._healthcheck_task,
            daemon=True,
        )
        self._healthcheck_thread.start()

        # Запускаем воркеров
        for i in range(self._worker_count):
            worker = threading.Thread(
                target=self._worker,
                name=f"WebsocketWorker-{i}",
                daemon=True,
            )
            self._workers.append(worker)
            worker.start()

    def stop(self) -> None:
        """Останавливает вебсокет и поток."""
        logger.info("Stopping websocket")
        self._running = False

        # Останавливаем поток проверки последнего времени сообщения
        try:
            if isinstance(self._healthcheck_thread, threading.Thread):
                self._healthcheck_thread.join(timeout=1)
        except Exception as e:
            logger.error(f"Error stopping healthcheck thread: {e}")

        # Останавилваем вебсокет
        try:
            if self._ws:
                self._ws.close()  # отправляем "close frame"
        except Exception as e:
            logger.error(f"Error closing websocket: {e}")

        # Ждем остановки вебсокета
        try:
            if self._ws_thread and self._ws_thread.is_alive():
                self._ws_thread.join(timeout=5)  # ждём завершения потока
                self._ws_thread = None
        except Exception as e:
            logger.error(f"Error stopping websocket thread: {e}")

        # Ждем остановки воркеров
        for worker in self._workers:
            try:
                if worker.is_alive():
                    worker.join(timeout=1)
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
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
                logger.error(f"Error in worker: {e}")
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
        logger.info("Websocket opened")
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
                logger.debug(f"{self} Received ping message: {message}")
            else:
                logger.error(f"Failed to decode JSON message: {message}, error: {e}")

        self._last_message_time = time.monotonic()

        with self._queue_lock:
            if len(self._queue) >= self.MAX_QUEUE_SIZE:
                raise QueueOverflowError("Message queue is overflow")
            self._queue.append(message)

    def _on_error(self, _: WebSocket, error: Exception) -> None:
        """Обработчик события ошибки вебсокета."""
        logger.error(f"Websocket error: {error}")
        self.restart()

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

    def _healthcheck_task(self) -> None:
        """Проверка работоспособности вебсокета исходя из времени последнего сообщения."""
        if not self._no_message_reconnect_timeout:
            return

        while self._running:
            try:
                if time.monotonic() - self._last_message_time > self._no_message_reconnect_timeout:  # type: ignore
                    logger.error("Websocket no message timeout triggered")
                    self.restart()
            except Exception as e:
                logger.error(f"Error checking websocket health: {e}")
            time.sleep(1)


class BaseAioWebsocket:
    """Базовый класс асинхронного вебсокета."""

    MAX_QUEUE_SIZE: int = 100
    """Максимальная длина очереди."""

    def __init__(
        self,
        callback: Callable,
        url: str,
        subscription_messages: list[dict] | list[str] | None = None,
        ping_interval: int | float = 10,
        ping_message: str | None = None,
        pong_message: str | None = None,
        no_message_reconnect_timeout: int | float | None = 60,
        reconnect_timeout: int | float | None = 5,
        worker_count: int = 2,
    ) -> None:
        """Инициализация вебсокета.

        Параметры:
            callback (Callable): Функция обратного вызова для обработки сообщений.
            subscription_messages (list[dict] | list[str] | None): Список сообщений для подписки.
            ping_interval (int | float | None): Интервал отправки пинга (сек.).
            ping_message (str | None): Сообщение для пинга, если не указано - отправляется обычный PING FRAME.
            pong_message (str | None): Сообщение для погна, если не указано - отправляется обычный PONG FRAME.
            no_message_reconnect_timeout (int | float | None): Время ожидания без сообщений для переподключения (сек.).
            reconnect_timeout (int | float | None): Время ожидания переподключения (сек.).
            worker_count (int): Количество потоков для обработки сообщений.
        """
        self._callback = callback
        self._url = url
        self._subscription_messages = subscription_messages or []
        self._ping_interval = ping_interval
        self._ping_message = ping_message
        self._pong_message = pong_message
        self._no_message_reconnect_timeout = no_message_reconnect_timeout
        self._reconnect_timeout = reconnect_timeout or 0
        self._last_message_time = time.monotonic()
        self._worker_count = worker_count
        self._tasks: list[asyncio.Task] = []
        self._queue = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Запустить вебсокет."""
        # Проверяем что вебсокет еще не запущен
        if self._running:
            raise RuntimeError("Websocket is already running")
        self._running = True

        # Запускаем вебсокет
        await self._connect()

    async def stop(self) -> None:
        """Остановить вебсокет."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

        # Очистка очереди
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Exception:
                break

    async def restart(self) -> None:
        """Перезапустить вебсокет."""
        await self.stop()
        await asyncio.sleep(self._reconnect_timeout)
        await self.start()

    async def _connect(self) -> None:
        """Подключиться к вебсокету."""
        logger.debug(f"Estabilishing connection with {self._url}")
        async for conn in websockets.connect(uri=self._url, **self._generate_ws_kwargs()):
            try:
                logger.info(f"Websocket connection was established to {self._url}")
                await self._after_connect(conn)

                # Цикл получения сообщений
                while self._running:
                    message = await conn.recv(decode=True)
                    await self._handle_message(message)

            except websockets.exceptions.ConnectionClosed:
                logger.error("Websocket connection was closed unexpectedly")
                continue
            finally:
                await asyncio.sleep(self._reconnect_timeout)
                await self._after_disconnect()

    async def _handle_message(self, message: str) -> None:
        """Обрабатывает сообщение из вебсокета."""
        try:
            # Обновленяем время последнего сообщения
            self._last_message_time = time.monotonic()

            # Ложим сообщение в очередь, предварительно его сериализуя
            await self._queue.put(orjson.loads(message))

            # Проверяем размер очереди сообщений и выбрасываем ошибку, если он превышает максимальный размер
            self._check_queue_size()
        except orjson.JSONDecodeError as e:
            if message in ["ping", "pong"]:
                logger.debug(f"{self} Received ping message: {message}")
            else:
                logger.error(f"Failed to decode JSON message: {message}, error: {e}")

    def _check_queue_size(self) -> None:
        """Проверяет размер очереди сообщений и выбрасывает ошибку, если он превышает максимальный размер."""
        qsize = self._queue.qsize()
        if qsize >= self.MAX_QUEUE_SIZE:
            raise QueueOverflowError("Message queue is overflow")

    async def _after_connect(self, conn: ClientConnection) -> None:
        """Вызывается после установки соединения с вебсокетом."""
        # Подписываемся на топики
        await self._send_subscribe_messages(conn)

        # Обновленяем время последнего сообщения перед каждым подключением
        self._last_message_time = time.monotonic()

        # Запускам задачу для кастомного пинг сообщения
        if self._ping_message:
            self._tasks.append(asyncio.create_task(self._custom_ping_task(conn)))

        # Запускаем healthcheck
        if self._no_message_reconnect_timeout:
            self._tasks.append(asyncio.create_task(self._healthcheck_task()))

        # Запускаем воркеров
        for _ in range(self._worker_count):
            task = asyncio.create_task(self._worker())
            self._tasks.append(task)

    async def _after_disconnect(self) -> None:
        """Вызывается после отключения от вебсокета."""
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

        # Очистить очередь
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Exception:
                break

    async def _send_subscribe_messages(self, conn: ClientConnection) -> None:
        """Отправляет сообщения с подпиской на топики, если нужно."""
        for message in self._subscription_messages:
            await conn.send(message)
            logger.debug(f"Sent subscribe message: {message}")

    async def _worker(self) -> None:
        """Обрабатывает сообщения из очереди."""
        while self._running:
            try:
                data = await self._queue.get()  # Получаем сообщение
                await self._callback(data)  # Передаем в callback
            except Exception as e:
                logger.error(f"{self} Error({type(e)}) while processing message: {e}")
            finally:
                self._queue.task_done()

    def _generate_ws_kwargs(self) -> dict:
        """Генерирует аргументы для запуска вебсокета."""
        ws_kwargs = {}
        if self._ping_interval:
            ws_kwargs["ping_interval"] = self._ping_interval
        return ws_kwargs

    async def _custom_ping_task(self, conn: ClientConnection) -> None:
        """Периодически отправляет кастомный ping."""
        while self._running and self._ping_message:
            try:
                await conn.send(self._ping_message)
                logger.debug(f"Sent ping message: {self._ping_message}")
            except Exception as e:
                logger.error(f"Error sending ping: {e}")
                return
            await asyncio.sleep(self._ping_interval)

    async def _healthcheck_task(self) -> None:
        """Следит за таймаутом получения сообщений."""
        while self._running:
            if time.monotonic() - self._last_message_time > self._no_message_reconnect_timeout:  # type: ignore
                logger.error("Websocket is not responding, restarting...")
                await self.restart()
                return
            await asyncio.sleep(1)
