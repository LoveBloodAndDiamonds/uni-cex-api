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
    # Mexc
    "MexcClient",
    "MexcUniClient",
    "MexcUniWebsocketManager",
    "MexcWebsocketManager",
    "MexcUserWebsocket",
    # Bybit
    "BybitClient",
    "BybitUniClient",
    "BybitUniWebsocketManager",
    "BybitWebsocketManager",
    "BybitUserWebsocket",
    # Okx
    "OkxClient",
    "OkxUniClient",
    "OkxUniWebsocketManager",
    "OkxWebsocketManager",
    "OkxUserWebsocket",
    # Hyperliquid
    "HyperliquidClient",
    "HyperliquidUniClient",
    "HyperliquidUniWebsocketManager",
    "HyperliquidWebsocketManager",
    "HyperliquidUserWebsocket",
]

# ruff: noqa

# abstract & base
from ._abc import IUniClient, IUniWebsocketManager
from ._base import BaseClient, Websocket

# enums, mappers, types
from .enums import Exchange, MarketType, Side, Timeframe
from .mapper import get_uni_client, get_uni_websocket_manager
from .types import (
    AggTradeDict,
    KlineDict,
    LoggerLike,
    RequestMethod,
    TickerDailyDict,
    TradeDict,
)

# exchanges

from .binance import (
    Client as BinanceClient,
    UniClient as BinanceUniClient,
    UniWebsocketManager as BinanceUniWebsocketManager,
    UserWebsocket as BinanceUserWebsocket,
    WebsocketManager as BinanceWebsocketManager,
)

from .bitget import (
    Client as BitgetClient,
    UniClient as BitgetUniClient,
    UniWebsocketManager as BitgetUniWebsocketManager,
    UserWebsocket as BitgetUserWebsocket,
    WebsocketManager as BitgetWebsocketManager,
)

from .bybit import (
    Client as BybitClient,
    UniClient as BybitUniClient,
    UniWebsocketManager as BybitUniWebsocketManager,
    UserWebsocket as BybitUserWebsocket,
    WebsocketManager as BybitWebsocketManager,
)

from .mexc import (
    Client as MexcClient,
    UniClient as MexcUniClient,
    UniWebsocketManager as MexcUniWebsocketManager,
    UserWebsocket as MexcUserWebsocket,
    WebsocketManager as MexcWebsocketManager,
)

from .okx import (
    Client as OkxClient,
    UniClient as OkxUniClient,
    UniWebsocketManager as OkxUniWebsocketManager,
    UserWebsocket as OkxUserWebsocket,
    WebsocketManager as OkxWebsocketManager,
)

from .hyperliquid import (
    Client as HyperliquidClient,
    UniClient as HyperliquidUniClient,
    UniWebsocketManager as HyperliquidUniWebsocketManager,
    UserWebsocket as HyperliquidUserWebsocket,
    WebsocketManager as HyperliquidWebsocketManager,
)
