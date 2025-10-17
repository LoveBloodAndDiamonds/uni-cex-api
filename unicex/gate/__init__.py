"""Пакет, содержащий реализации клиентов и менеджеров для работы с биржей Gateio."""

__all__ = [
    "Client",
    "UniClient",
    "UserWebsocket",
    "WebsocketManager",
    "UniWebsocketManager",
    "ExchangeInfo",
]

from .client import Client
from .exchange_info import ExchangeInfo
from .uni_client import UniClient
from .uni_websocket_manager import UniWebsocketManager
from .user_websocket import UserWebsocket
from .websocket_manager import WebsocketManager


async def load_exchange_info() -> None:
    """Загружает информацию о бирже Gateio."""
    await ExchangeInfo.load_exchange_info()


async def start_exchange_info(parse_interval_seconds: int = 60 * 60) -> None:
    """Запускает процесс обновления информации о бирже Gateio."""
    await ExchangeInfo.start(parse_interval_seconds)
