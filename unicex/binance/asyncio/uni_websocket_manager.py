__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable
from typing import Any

from unicex._base.asyncio import Websocket

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
        Callable[[Any], Awaitable[None]],
    ]
):
    """Асинхронный унифицированный менеджер вебсокетов для Binance."""

    def __init__(self, client: Client | UniClient | None = None) -> None:
        """Инициализирует асинхронный унифицированный менеджер вебсокетов для Binance.

        Параметры:
            client (Client | UniClient | None): Клиент для работы с Binance.
        """
        super().__init__(websocket_manager_cls=WebsocketManager, sync=False, client=client)
