"""unicex - библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс для работы с различными криптовалютными биржами."""

__all__ = [
    # Mappers
    "get_uni_client",
    "get_uni_websocket_manager",
    "get_exchange_info",
    # Exchanges info
    "load_exchanges_info",
    "start_exchanges_info",
    # Enums
    "MarketType",
    "Exchange",
    "Timeframe",
    "Side",
    # Types
    "TickerDailyDict",
    "TickerDailyItem",
    "KlineDict",
    "TradeDict",
    "AggTradeDict",
    "RequestMethod",
    "LoggerLike",
    "AccountType",
    "OpenInterestDict",
    "OpenInterestItem",
    "TickerInfoItem",
    "TickersInfoDict",
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
    "BinanceExchangeInfo",
    # Bitget
    "BitgetClient",
    "BitgetUniClient",
    "BitgetUniWebsocketManager",
    "BitgetWebsocketManager",
    "BitgetUserWebsocket",
    "BitgetExchangeInfo",
    # Bitrue
    "BitrueClient",
    "BitrueUniClient",
    "BitrueUniWebsocketManager",
    "BitrueWebsocketManager",
    "BitrueUserWebsocket",
    "BitrueExchangeInfo",
    # Mexc
    "MexcClient",
    "MexcUniClient",
    "MexcUniWebsocketManager",
    "MexcWebsocketManager",
    "MexcUserWebsocket",
    "MexcExchangeInfo",
    # Bybit
    "BybitClient",
    "BybitUniClient",
    "BybitUniWebsocketManager",
    "BybitWebsocketManager",
    "BybitUserWebsocket",
    "BybitExchangeInfo",
    # Okx
    "OkxClient",
    "OkxUniClient",
    "OkxUniWebsocketManager",
    "OkxWebsocketManager",
    "OkxUserWebsocket",
    "OkxExchangeInfo",
    # Hyperliquid
    "HyperliquidClient",
    "HyperliquidUniClient",
    "HyperliquidUniWebsocketManager",
    "HyperliquidWebsocketManager",
    "HyperliquidUserWebsocket",
    "HyperliquidExchangeInfo",
    # Gateio
    "GateioClient",
    "GateioUniClient",
    "GateioUniWebsocketManager",
    "GateioWebsocketManager",
    "GateioUserWebsocket",
    "GateioExchangeInfo",
    # Bitunix
    "BitunixClient",
    "BitunixUniClient",
    "BitunixUniWebsocketManager",
    "BitunixWebsocketManager",
    "BitunixUserWebsocket",
    "BitunixExchangeInfo",
    # Btse
    "BtseClient",
    "BtseUniClient",
    "BtseUniWebsocketManager",
    "BtseWebsocketManager",
    "BtseUserWebsocket",
    "BtseExchangeInfo",
    # Kcex
    "KcexClient",
    "KcexUniClient",
    "KcexUniWebsocketManager",
    "KcexWebsocketManager",
    "KcexUserWebsocket",
    "KcexExchangeInfo",
    # Kraken
    "KrakenClient",
    "KrakenUniClient",
    "KrakenUniWebsocketManager",
    "KrakenWebsocketManager",
    "KrakenUserWebsocket",
    "KrakenExchangeInfo",
    # Kucoin
    "KucoinClient",
    "KucoinUniClient",
    "KucoinUniWebsocketManager",
    "KucoinWebsocketManager",
    "KucoinUserWebsocket",
    "KucoinExchangeInfo",
    # Weex
    "WeexClient",
    "WeexUniClient",
    "WeexUniWebsocketManager",
    "WeexWebsocketManager",
    "WeexUserWebsocket",
    "WeexExchangeInfo",
    # Xt
    "XtClient",
    "XtUniClient",
    "XtUniWebsocketManager",
    "XtWebsocketManager",
    "XtUserWebsocket",
    "XtExchangeInfo",
]

# ruff: noqa

# abstract & base
import asyncio
from ._abc import IUniClient, IUniWebsocketManager
from ._base import BaseClient, Websocket

# enums, mappers, types
from .enums import Exchange, MarketType, Side, Timeframe
from .mapper import get_uni_client, get_uni_websocket_manager, get_exchange_info
from .types import *

# exchanges

from .binance import (
    Client as BinanceClient,
    UniClient as BinanceUniClient,
    UniWebsocketManager as BinanceUniWebsocketManager,
    UserWebsocket as BinanceUserWebsocket,
    WebsocketManager as BinanceWebsocketManager,
    ExchangeInfo as BinanceExchangeInfo,
)

from .bitget import (
    Client as BitgetClient,
    UniClient as BitgetUniClient,
    UniWebsocketManager as BitgetUniWebsocketManager,
    UserWebsocket as BitgetUserWebsocket,
    WebsocketManager as BitgetWebsocketManager,
    ExchangeInfo as BitgetExchangeInfo,
)

from .bitrue import (
    Client as BitrueClient,
    UniClient as BitrueUniClient,
    UniWebsocketManager as BitrueUniWebsocketManager,
    UserWebsocket as BitrueUserWebsocket,
    WebsocketManager as BitrueWebsocketManager,
    ExchangeInfo as BitrueExchangeInfo,
)

from .bitunix import (
    Client as BitunixClient,
    UniClient as BitunixUniClient,
    UniWebsocketManager as BitunixUniWebsocketManager,
    UserWebsocket as BitunixUserWebsocket,
    WebsocketManager as BitunixWebsocketManager,
    ExchangeInfo as BitunixExchangeInfo,
)

from .btse import (
    Client as BtseClient,
    UniClient as BtseUniClient,
    UniWebsocketManager as BtseUniWebsocketManager,
    UserWebsocket as BtseUserWebsocket,
    WebsocketManager as BtseWebsocketManager,
    ExchangeInfo as BtseExchangeInfo,
)

from .bybit import (
    Client as BybitClient,
    UniClient as BybitUniClient,
    UniWebsocketManager as BybitUniWebsocketManager,
    UserWebsocket as BybitUserWebsocket,
    WebsocketManager as BybitWebsocketManager,
    ExchangeInfo as BybitExchangeInfo,
)

from .gateio import (
    Client as GateioClient,
    UniClient as GateioUniClient,
    UniWebsocketManager as GateioUniWebsocketManager,
    UserWebsocket as GateioUserWebsocket,
    WebsocketManager as GateioWebsocketManager,
    ExchangeInfo as GateioExchangeInfo,
)

from .hyperliquid import (
    Client as HyperliquidClient,
    UniClient as HyperliquidUniClient,
    UniWebsocketManager as HyperliquidUniWebsocketManager,
    UserWebsocket as HyperliquidUserWebsocket,
    WebsocketManager as HyperliquidWebsocketManager,
    ExchangeInfo as HyperliquidExchangeInfo,
)

from .kcex import (
    Client as KcexClient,
    UniClient as KcexUniClient,
    UniWebsocketManager as KcexUniWebsocketManager,
    UserWebsocket as KcexUserWebsocket,
    WebsocketManager as KcexWebsocketManager,
    ExchangeInfo as KcexExchangeInfo,
)

from .kraken import (
    Client as KrakenClient,
    UniClient as KrakenUniClient,
    UniWebsocketManager as KrakenUniWebsocketManager,
    UserWebsocket as KrakenUserWebsocket,
    WebsocketManager as KrakenWebsocketManager,
    ExchangeInfo as KrakenExchangeInfo,
)

from .kucoin import (
    Client as KucoinClient,
    UniClient as KucoinUniClient,
    UniWebsocketManager as KucoinUniWebsocketManager,
    UserWebsocket as KucoinUserWebsocket,
    WebsocketManager as KucoinWebsocketManager,
    ExchangeInfo as KucoinExchangeInfo,
)

from .mexc import (
    Client as MexcClient,
    UniClient as MexcUniClient,
    UniWebsocketManager as MexcUniWebsocketManager,
    UserWebsocket as MexcUserWebsocket,
    WebsocketManager as MexcWebsocketManager,
    ExchangeInfo as MexcExchangeInfo,
)

from .okx import (
    Client as OkxClient,
    UniClient as OkxUniClient,
    UniWebsocketManager as OkxUniWebsocketManager,
    UserWebsocket as OkxUserWebsocket,
    WebsocketManager as OkxWebsocketManager,
    ExchangeInfo as OkxExchangeInfo,
)

from .weex import (
    Client as WeexClient,
    UniClient as WeexUniClient,
    UniWebsocketManager as WeexUniWebsocketManager,
    UserWebsocket as WeexUserWebsocket,
    WebsocketManager as WeexWebsocketManager,
    ExchangeInfo as WeexExchangeInfo,
)

from .xt import (
    Client as XtClient,
    UniClient as XtUniClient,
    UniWebsocketManager as XtUniWebsocketManager,
    UserWebsocket as XtUserWebsocket,
    WebsocketManager as XtWebsocketManager,
    ExchangeInfo as XtExchangeInfo,
)


async def load_exchanges_info() -> None:
    """Единожды загружает информацию о тикерах на всех биржах."""
    await asyncio.gather(
        BinanceExchangeInfo.load_exchange_info(),
        BitgetExchangeInfo.load_exchange_info(),
        BitrueExchangeInfo.load_exchange_info(),
        BitunixExchangeInfo.load_exchange_info(),
        BtseExchangeInfo.load_exchange_info(),
        BybitExchangeInfo.load_exchange_info(),
        GateioExchangeInfo.load_exchange_info(),
        HyperliquidExchangeInfo.load_exchange_info(),
        KcexExchangeInfo.load_exchange_info(),
        KrakenExchangeInfo.load_exchange_info(),
        KucoinExchangeInfo.load_exchange_info(),
        MexcExchangeInfo.load_exchange_info(),
        OkxExchangeInfo.load_exchange_info(),
        WeexExchangeInfo.load_exchange_info(),
        XtExchangeInfo.load_exchange_info(),
    )


async def start_exchanges_info(parse_interval_seconds: int = 60 * 60) -> None:
    """Запускает цикл обновления информации о тикерах на всех биржах."""
    asyncio.gather(
        BinanceExchangeInfo.start(parse_interval_seconds),
        BitgetExchangeInfo.start(parse_interval_seconds),
        BitrueExchangeInfo.start(parse_interval_seconds),
        BitunixExchangeInfo.start(parse_interval_seconds),
        BtseExchangeInfo.start(parse_interval_seconds),
        BybitExchangeInfo.start(parse_interval_seconds),
        GateioExchangeInfo.start(parse_interval_seconds),
        HyperliquidExchangeInfo.start(parse_interval_seconds),
        KcexExchangeInfo.start(parse_interval_seconds),
        KrakenExchangeInfo.start(parse_interval_seconds),
        KucoinExchangeInfo.start(parse_interval_seconds),
        MexcExchangeInfo.start(parse_interval_seconds),
        OkxExchangeInfo.start(parse_interval_seconds),
        WeexExchangeInfo.start(parse_interval_seconds),
        XtExchangeInfo.start(parse_interval_seconds),
    )
