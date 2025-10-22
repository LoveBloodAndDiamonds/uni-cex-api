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
    "LiquidationDict",
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
]

# ruff: noqa

# abstract & base
import asyncio
from ._abc import IUniClient, IUniWebsocketManager
from ._base import BaseClient, Websocket

# enums, mappers, types
from .enums import Exchange, MarketType, Side, Timeframe
from .mapper import get_uni_client, get_uni_websocket_manager, get_exchange_info
from .types import (
    TickerDailyDict,
    TickerDailyItem,
    KlineDict,
    TradeDict,
    AggTradeDict,
    RequestMethod,
    LoggerLike,
    AccountType,
    OpenInterestDict,
    OpenInterestItem,
    TickerInfoItem,
    TickersInfoDict,
    LiquidationDict,
)

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

from .bybit import (
    Client as BybitClient,
    UniClient as BybitUniClient,
    UniWebsocketManager as BybitUniWebsocketManager,
    UserWebsocket as BybitUserWebsocket,
    WebsocketManager as BybitWebsocketManager,
    ExchangeInfo as BybitExchangeInfo,
)

from .gate import (
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


async def load_exchanges_info() -> None:
    """Единожды загружает информацию о тикерах на всех биржах."""
    await asyncio.gather(
        BinanceExchangeInfo.load_exchange_info(),
        BitgetExchangeInfo.load_exchange_info(),
        BybitExchangeInfo.load_exchange_info(),
        GateioExchangeInfo.load_exchange_info(),
        HyperliquidExchangeInfo.load_exchange_info(),
        MexcExchangeInfo.load_exchange_info(),
        OkxExchangeInfo.load_exchange_info(),
    )


async def start_exchanges_info(parse_interval_seconds: int = 60 * 60) -> None:
    """Запускает цикл обновления информации о тикерах на всех биржах."""
    asyncio.gather(
        BinanceExchangeInfo.start(parse_interval_seconds),
        BitgetExchangeInfo.start(parse_interval_seconds),
        BybitExchangeInfo.start(parse_interval_seconds),
        GateioExchangeInfo.start(parse_interval_seconds),
        HyperliquidExchangeInfo.start(parse_interval_seconds),
        MexcExchangeInfo.start(parse_interval_seconds),
        OkxExchangeInfo.start(parse_interval_seconds),
    )
