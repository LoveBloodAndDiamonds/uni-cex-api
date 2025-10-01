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
from .bitrue import UniClient as BitrueUniClient
from .bitrue import UniWebsocketManager as BitrueUniWebsocketManager
from .bitunix import UniClient as BitunixUniClient
from .bitunix import UniWebsocketManager as BitunixUniWebsocketManager
from .btse import UniClient as BtseUniClient
from .btse import UniWebsocketManager as BtseUniWebsocketManager
from .bybit import UniClient as BybitUniClient
from .bybit import UniWebsocketManager as BybitUniWebsocketManager
from .enums import Exchange
from .exceptions import NotSupported
from .gateio import UniClient as GateioUniClient
from .gateio import UniWebsocketManager as GateioUniWebsocketManager
from .hyperliquid import UniClient as HyperliquidUniClient
from .hyperliquid import UniWebsocketManager as HyperliquidUniWebsocketManager
from .kcex import UniClient as KcexUniClient
from .kcex import UniWebsocketManager as KcexUniWebsocketManager
from .kraken import UniClient as KrakenUniClient
from .kraken import UniWebsocketManager as KrakenUniWebsocketManager
from .kucoin import UniClient as KucoinUniClient
from .kucoin import UniWebsocketManager as KucoinUniWebsocketManager
from .mexc import UniClient as MexcUniClient
from .mexc import UniWebsocketManager as MexcUniWebsocketManager
from .okx import UniClient as OkxUniClient
from .okx import UniWebsocketManager as OkxUniWebsocketManager
from .weex import UniClient as WeexUniClient
from .weex import UniWebsocketManager as WeexUniWebsocketManager
from .xt import UniClient as XtUniClient
from .xt import UniWebsocketManager as XtUniWebsocketManager

_UNI_CLIENT_MAPPER: dict[Exchange, type[IUniClient]] = {
    Exchange.BINANCE: BinanceUniClient,
    Exchange.BITGET: BitgetUniClient,
    Exchange.BITRUE: BitrueUniClient,
    Exchange.BITUNIX: BitunixUniClient,
    Exchange.BTSE: BtseUniClient,
    Exchange.BYBIT: BybitUniClient,
    Exchange.GATEIO: GateioUniClient,
    Exchange.HYPERLIQUID: HyperliquidUniClient,
    Exchange.KCEX: KcexUniClient,
    Exchange.KRAKEN: KrakenUniClient,
    Exchange.KUCOIN: KucoinUniClient,
    Exchange.MEXC: MexcUniClient,
    Exchange.OKX: OkxUniClient,
    Exchange.WEEX: WeexUniClient,
    Exchange.XT: XtUniClient,
}
"""Маппер, который связывает биржу и реализацию унифицированного клиента."""

_UNI_WS_MANAGER_MAPPER: dict[Exchange, type[IUniWebsocketManager]] = {
    Exchange.BINANCE: BinanceUniWebsocketManager,
    Exchange.BITGET: BitgetUniWebsocketManager,
    Exchange.BITRUE: BitrueUniWebsocketManager,
    Exchange.BITUNIX: BitunixUniWebsocketManager,
    Exchange.BTSE: BtseUniWebsocketManager,
    Exchange.BYBIT: BybitUniWebsocketManager,
    Exchange.GATEIO: GateioUniWebsocketManager,
    Exchange.HYPERLIQUID: HyperliquidUniWebsocketManager,
    Exchange.KCEX: KcexUniWebsocketManager,
    Exchange.KRAKEN: KrakenUniWebsocketManager,
    Exchange.KUCOIN: KucoinUniWebsocketManager,
    Exchange.MEXC: MexcUniWebsocketManager,
    Exchange.OKX: OkxUniWebsocketManager,
    Exchange.WEEX: WeexUniWebsocketManager,
    Exchange.XT: XtUniWebsocketManager,
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
