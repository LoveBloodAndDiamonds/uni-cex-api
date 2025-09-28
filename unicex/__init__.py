"""unicex - библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс для работы с различными криптовалютными биржами."""

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
    # Base clients and websockets
    "Websocket",
    "BaseClient",
    # Binance
    "BinanceClient",
    "BinanceUniClient",
    "BinanceWebsocketManager",
    "BinanceUniWebsocketManager",
    "BinanceUserWebsocket",
    # Bitget
    "BitgetClient",
    "BitgetUniClient",
    "BitgetUniWebsocketManager",
    "BitgetWebsocketManager",
    "BitgetUserWebsocket",
]

from ._abc import IAdapter, IUniClient, IUniWebsocketManager
from ._base import BaseClient, Websocket
from .binance import Client as BinanceClient
from .binance import UniClient as BinanceUniClient
from .binance import UniWebsocketManager as BinanceUniWebsocketManager
from .binance import UserWebsocket as BinanceUserWebsocket
from .binance import WebsocketManager as BinanceWebsocketManager
from .bitget import Client as BitgetClient
from .bitget import UniClient as BitgetUniClient
from .bitget import UniWebsocketManager as BitgetUniWebsocketManager
from .bitget import UserWebsocket as BitgetUserWebsocket
from .bitget import WebsocketManager as BitgetWebsocketManager
from .enums import Exchange, MarketType, Side, Timeframe
from .mapper import get_uni_client, get_uni_websocket_manager
from .types import AggTradeDict, KlineDict, LoggerLike, RequestMethod, TickerDailyDict, TradeDict
