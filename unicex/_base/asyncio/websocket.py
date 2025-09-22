__all__ = ["Websocket"]

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

import orjson
import websockets  # async
from websockets.asyncio.client import ClientConnection

from unicex.exceptions import QueueOverflowError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Websocket:
    """Базовый класс асинхронного вебсокета."""

    MAX_QUEUE_SIZE: int = 100
    """Максимальная длина очереди."""

    def __init__(
        self,
        callback: Callable[[Any], Awaitable[None]],
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
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова для обработки сообщений.
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
        if not self._no_message_reconnect_timeout:
            return

        while self._running:
            if time.monotonic() - self._last_message_time > self._no_message_reconnect_timeout:
                logger.error("Websocket is not responding, restarting...")
                await self.restart()
                return
            await asyncio.sleep(1)
