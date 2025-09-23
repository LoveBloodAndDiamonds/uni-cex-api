__all__ = ["UniWebsocketManager"]

from collections.abc import Callable
from typing import Any

from unicex._base import Websocket

from .._factories import UniWebsocketManagerFactory
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager


class UniWebsocketManager(
    UniWebsocketManagerFactory[
        Client,
        UniClient,
        WebsocketManager,
        Websocket,
        Callable[[Any], None],
    ]
):
    """Синхронный унифицированный менеджер вебсокетов для Binance."""

    def __init__(self, client: Client | UniClient | None = None) -> None:
        """Инициализирует синхронный унифицированный менеджер вебсокетов для Binance.

        Параметры:
            client (Client | UniClient | None): Клиент для работы с Binance.
        """
        super().__init__(websocket_manager_cls=WebsocketManager, sync=True, client=client)
