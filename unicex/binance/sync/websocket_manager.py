__all__ = ["WebsocketManager"]


from unicex._base import Websocket

from .._base import BaseWebsocketManager
from .client import Client
from .user_websocket import UserWebsocket


class WebsocketManager(BaseWebsocketManager[Client, Websocket, UserWebsocket]):
    """Менеджер асинхронных вебсокетов для Binance."""

    def __init__(self, client: Client | None = None) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (Client | None): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
        """
        super().__init__(websocket_cls=Websocket, user_websocket_cls=UserWebsocket, client=client)
