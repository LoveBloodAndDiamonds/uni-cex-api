"""Модуль, который предоставляет мапперы для унифицированных клиентов и вебсокет-менеджеров."""

__all__ = [
    "get_uni_client",
    "get_uni_websocket_manager",
    "get_exchange_info",
]


from ._abc import IExchangeInfo, IUniClient, IUniWebsocketManager
from .binance import ExchangeInfo as BinanceExchangeInfo
from .binance import UniClient as BinanceUniClient
from .binance import UniWebsocketManager as BinanceUniWebsocketManager
from .bitget import ExchangeInfo as BitgetExchangeInfo
from .bitget import UniClient as BitgetUniClient
from .bitget import UniWebsocketManager as BitgetUniWebsocketManager
from .bybit import ExchangeInfo as BybitExchangeInfo
from .bybit import UniClient as BybitUniClient
from .bybit import UniWebsocketManager as BybitUniWebsocketManager
from .enums import Exchange
from .exceptions import NotSupported
from .gate import ExchangeInfo as GateioExchangeInfo
from .gate import UniClient as GateioUniClient
from .gate import UniWebsocketManager as GateioUniWebsocketManager
from .hyperliquid import ExchangeInfo as HyperliquidExchangeInfo
from .hyperliquid import UniClient as HyperliquidUniClient
from .hyperliquid import UniWebsocketManager as HyperliquidUniWebsocketManager
from .mexc import ExchangeInfo as MexcExchangeInfo
from .mexc import UniClient as MexcUniClient
from .mexc import UniWebsocketManager as MexcUniWebsocketManager
from .okx import ExchangeInfo as OkxExchangeInfo
from .okx import UniClient as OkxUniClient
from .okx import UniWebsocketManager as OkxUniWebsocketManager

_UNI_CLIENT_MAPPER: dict[Exchange, type[IUniClient]] = {
    Exchange.BINANCE: BinanceUniClient,
    Exchange.BITGET: BitgetUniClient,
    Exchange.BYBIT: BybitUniClient,
    Exchange.GATE: GateioUniClient,
    Exchange.HYPERLIQUID: HyperliquidUniClient,
    Exchange.MEXC: MexcUniClient,
    Exchange.OKX: OkxUniClient,
}
"""Маппер, который связывает биржу и реализацию унифицированного клиента."""

_UNI_WS_MANAGER_MAPPER: dict[Exchange, type[IUniWebsocketManager]] = {
    Exchange.BINANCE: BinanceUniWebsocketManager,
    Exchange.BITGET: BitgetUniWebsocketManager,
    Exchange.BYBIT: BybitUniWebsocketManager,
    Exchange.GATE: GateioUniWebsocketManager,
    Exchange.HYPERLIQUID: HyperliquidUniWebsocketManager,
    Exchange.MEXC: MexcUniWebsocketManager,
    Exchange.OKX: OkxUniWebsocketManager,
}
"""Маппер, который связывает биржу и реализацию унифицированного вебсокет-менеджера."""

_EXCHANGE_INFO_MAPPER: dict[Exchange, type[IExchangeInfo]] = {
    Exchange.BINANCE: BinanceExchangeInfo,
    Exchange.BITGET: BitgetExchangeInfo,
    Exchange.BYBIT: BybitExchangeInfo,
    Exchange.GATE: GateioExchangeInfo,
    Exchange.HYPERLIQUID: HyperliquidExchangeInfo,
    Exchange.MEXC: MexcExchangeInfo,
    Exchange.OKX: OkxExchangeInfo,
}
"""Маппер, который связывает биржу и реализацию сборщика информации о тикерах на бирже."""


def get_uni_client(exchange: Exchange) -> type[IUniClient]:
    """Возвращает унифицированный клиент для указанной биржи.

    Параметры:
        exchange (`Exchange`): Биржа.

    Возвращает:
        `type[IUniClient]`: Унифицированный клиент для указанной биржи.
    """
    try:
        return _UNI_CLIENT_MAPPER[exchange]
    except KeyError as e:
        raise NotSupported(f"Unsupported exchange: {exchange}") from e


def get_uni_websocket_manager(exchange: Exchange) -> type[IUniWebsocketManager]:
    """Возвращает унифицированный вебсокет-менеджер для указанной биржи.

    Параметры:
        exchange (`Exchange`): Биржа.

    Возвращает:
        `type[IUniWebsocketManager]`: Унифицированный вебсокет-менеджер для указанной биржи.
    """
    try:
        return _UNI_WS_MANAGER_MAPPER[exchange]
    except KeyError as e:
        raise NotSupported(f"Unsupported exchange: {exchange}") from e


def get_exchange_info(exchange: Exchange) -> type[IExchangeInfo]:
    """Возвращает унифицированный интерфейс для получения информации о бирже.

    Параметры:
        exchange (`Exchange`): Биржа.

    Возвращает:
        `type[IExchangeInfo]`: Унифицированный интерфейс для получения информации о бирже.
    """
    try:
        return _EXCHANGE_INFO_MAPPER[exchange]
    except KeyError as e:
        raise NotSupported(f"Unsupported exchange: {exchange}") from e
