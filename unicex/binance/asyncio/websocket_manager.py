__all__ = ["WebsocketManager"]


from collections.abc import Awaitable, Callable
from typing import Any

from unicex._base.asyncio import Websocket

from .._factories import WebsocketManagerFactory
from .client import Client
from .user_websocket import UserWebsocket


class WebsocketManager(
    WebsocketManagerFactory[Client, Websocket, UserWebsocket, Callable[[Any], Awaitable[None]]]
):
    """Менеджер асинхронных вебсокетов для Binance."""

    def __init__(self, client: Client | None = None) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (Client | None): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
        """
        super().__init__(websocket_cls=Websocket, user_websocket_cls=UserWebsocket, client=client)
