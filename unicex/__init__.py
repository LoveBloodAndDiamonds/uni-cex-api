"""`unicex` - библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс для работы с различными криптовалютными биржами."""

__all__ = [
    # Mappers
    "get_uni_client",
    "get_uni_websocket_manager",
    # Enums
    "MarketType",
    "Exchange",
    "Timeframe",
    "Side",
    # Types
    "KlineDict",
    "AggTradeDict",
    "TradeDict",
    "TickerDailyDict",
    "RequestMethod",
    "LoggerLike",
    # Interfaces
    "IUniClient",
    "IUniWebsocketManager",
    "IAdapter",
    "IUniAsyncClient",
    "IUniAsyncWebsocketManager",
    # Base clients and websockets
    "Websocket",
    "BaseClient",
    "AsyncWebsocket",
    "BaseAsyncClient",
]

from ._abc import IAdapter, IUniClient, IUniWebsocketManager
from ._abc import IUniClient as IUniAsyncClient
from ._abc import IUniWebsocketManager as IUniAsyncWebsocketManager
from ._base import BaseClient, Websocket
from ._base import BaseClient as BaseAsyncClient
from ._base import Websocket as AsyncWebsocket
from .enums import Exchange, MarketType, Side, Timeframe
from .mapper import get_uni_client, get_uni_websocket_manager
from .types import AggTradeDict, KlineDict, LoggerLike, RequestMethod, TickerDailyDict, TradeDict
