"""Модуль, который предоставляет мапперы для унифицированных клиентов и вебсокет-менеджеров."""

__all__ = [
    "get_uni_client",
    "get_uni_websocket_manager",
]


from ._abc import IUniClient, IUniWebsocketManager
from .binance import UniClient as BinanceUniClient
from .binance import UniWebsocketManager as BinanceUniWebsocketManager
from .bitget import UniClient as BitgetUniClient
from .bitget import UniWebsocketManager as BitgetUniWebsocketManager
from .bybit import UniClient as BybitUniClient
from .bybit import UniWebsocketManager as BybitUniWebsocketManager
from .enums import Exchange
from .exceptions import NotSupported
from .hyperliquid import UniClient as HyperliquidUniClient
from .hyperliquid import UniWebsocketManager as HyperliquidUniWebsocketManager
from .mexc import UniClient as MexcUniClient
from .mexc import UniWebsocketManager as MexcUniWebsocketManager
from .okx import UniClient as OkxUniClient
from .okx import UniWebsocketManager as OkxUniWebsocketManager

_UNI_CLIENT_MAPPER: dict[Exchange, type[IUniClient]] = {
    Exchange.BINANCE: BinanceUniClient,
    Exchange.BITGET: BitgetUniClient,
    Exchange.BYBIT: BybitUniClient,
    Exchange.MEXC: MexcUniClient,
    Exchange.OKX: OkxUniClient,
    Exchange.HYPERLIQUID: HyperliquidUniClient,
}
"""Маппер, который связывает биржу и реализацию унифицированного клиента."""

_UNI_WS_MANAGER_MAPPER: dict[Exchange, type[IUniWebsocketManager]] = {
    Exchange.BINANCE: BinanceUniWebsocketManager,
    Exchange.BITGET: BitgetUniWebsocketManager,
    Exchange.MEXC: MexcUniWebsocketManager,
    Exchange.BYBIT: BybitUniWebsocketManager,
    Exchange.OKX: OkxUniWebsocketManager,
    Exchange.HYPERLIQUID: HyperliquidUniWebsocketManager,
}
"""Маппер, который связывает биржу и реализацию унифицированного вебсокет-менеджера."""


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
