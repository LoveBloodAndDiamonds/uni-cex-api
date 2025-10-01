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
    # Bitrue
    "BitrueClient",
    "BitrueUniClient",
    "BitrueUniWebsocketManager",
    "BitrueWebsocketManager",
    "BitrueUserWebsocket",
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
    # Gateio
    "GateioClient",
    "GateioUniClient",
    "GateioUniWebsocketManager",
    "GateioWebsocketManager",
    "GateioUserWebsocket",
    # Bitunix
    "BitunixClient",
    "BitunixUniClient",
    "BitunixUniWebsocketManager",
    "BitunixWebsocketManager",
    "BitunixUserWebsocket",
    # Btse
    "BtseClient",
    "BtseUniClient",
    "BtseUniWebsocketManager",
    "BtseWebsocketManager",
    "BtseUserWebsocket",
    # Kcex
    "KcexClient",
    "KcexUniClient",
    "KcexUniWebsocketManager",
    "KcexWebsocketManager",
    "KcexUserWebsocket",
    # Kraken
    "KrakenClient",
    "KrakenUniClient",
    "KrakenUniWebsocketManager",
    "KrakenWebsocketManager",
    "KrakenUserWebsocket",
    # Kucoin
    "KucoinClient",
    "KucoinUniClient",
    "KucoinUniWebsocketManager",
    "KucoinWebsocketManager",
    "KucoinUserWebsocket",
    # Weex
    "WeexClient",
    "WeexUniClient",
    "WeexUniWebsocketManager",
    "WeexWebsocketManager",
    "WeexUserWebsocket",
    # Xt
    "XtClient",
    "XtUniClient",
    "XtUniWebsocketManager",
    "XtWebsocketManager",
    "XtUserWebsocket",
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

from .bitrue import (
    Client as BitrueClient,
    UniClient as BitrueUniClient,
    UniWebsocketManager as BitrueUniWebsocketManager,
    UserWebsocket as BitrueUserWebsocket,
    WebsocketManager as BitrueWebsocketManager,
)

from .bitunix import (
    Client as BitunixClient,
    UniClient as BitunixUniClient,
    UniWebsocketManager as BitunixUniWebsocketManager,
    UserWebsocket as BitunixUserWebsocket,
    WebsocketManager as BitunixWebsocketManager,
)

from .btse import (
    Client as BtseClient,
    UniClient as BtseUniClient,
    UniWebsocketManager as BtseUniWebsocketManager,
    UserWebsocket as BtseUserWebsocket,
    WebsocketManager as BtseWebsocketManager,
)

from .bybit import (
    Client as BybitClient,
    UniClient as BybitUniClient,
    UniWebsocketManager as BybitUniWebsocketManager,
    UserWebsocket as BybitUserWebsocket,
    WebsocketManager as BybitWebsocketManager,
)

from .gateio import (
    Client as GateioClient,
    UniClient as GateioUniClient,
    UniWebsocketManager as GateioUniWebsocketManager,
    UserWebsocket as GateioUserWebsocket,
    WebsocketManager as GateioWebsocketManager,
)

from .hyperliquid import (
    Client as HyperliquidClient,
    UniClient as HyperliquidUniClient,
    UniWebsocketManager as HyperliquidUniWebsocketManager,
    UserWebsocket as HyperliquidUserWebsocket,
    WebsocketManager as HyperliquidWebsocketManager,
)

from .kcex import (
    Client as KcexClient,
    UniClient as KcexUniClient,
    UniWebsocketManager as KcexUniWebsocketManager,
    UserWebsocket as KcexUserWebsocket,
    WebsocketManager as KcexWebsocketManager,
)

from .kraken import (
    Client as KrakenClient,
    UniClient as KrakenUniClient,
    UniWebsocketManager as KrakenUniWebsocketManager,
    UserWebsocket as KrakenUserWebsocket,
    WebsocketManager as KrakenWebsocketManager,
)

from .kucoin import (
    Client as KucoinClient,
    UniClient as KucoinUniClient,
    UniWebsocketManager as KucoinUniWebsocketManager,
    UserWebsocket as KucoinUserWebsocket,
    WebsocketManager as KucoinWebsocketManager,
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

from .weex import (
    Client as WeexClient,
    UniClient as WeexUniClient,
    UniWebsocketManager as WeexUniWebsocketManager,
    UserWebsocket as WeexUserWebsocket,
    WebsocketManager as WeexWebsocketManager,
)

from .xt import (
    Client as XtClient,
    UniClient as XtUniClient,
    UniWebsocketManager as XtUniWebsocketManager,
    UserWebsocket as XtUserWebsocket,
    WebsocketManager as XtWebsocketManager,
)
