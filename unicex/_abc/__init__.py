"""Пакет с абстракциями и интерфейсами."""

__all__ = [
    "IUniClient",
    "IUniWebsocketManager",
    "IExchangeInfo",
    "IDecoder",
]

from .decoder import IDecoder
from .exchange_info import IExchangeInfo
from .uni_client import IUniClient
from .uni_websocket_manager import IUniWebsocketManager
