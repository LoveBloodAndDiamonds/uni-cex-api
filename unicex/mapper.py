"""Модуль, который предоставляет мапперы для унифицированных клиентов и вебсокет-менеджеров."""

__all__ = [
    "get_uni_client",
    "get_uni_websocket_manager",
]

from typing import Literal, overload

from ._abc import IUniClient, IUniWebsocketManager
from ._abc.asyncio import IUniClient as IUniAioClient
from ._abc.asyncio import IUniWebsocketManager as IUniAioWebsocketManager
from .binance import UniClient as BinanceUniClient
from .binance import UniWebsocketManager as BinanceUniWebsocketManager
from .binance.asyncio import UniClient as BinanceUniAioClient
from .binance.asyncio import UniWebsocketManager as BinanceUniAioWebsocketManager
from .enums import Exchange
from .exceptions import NotSupported

_UNI_CLIENT_MAPPER: dict[Exchange, type[IUniClient]] = {Exchange.BINANCE: BinanceUniClient}
"""Маппер, который связывает биржу и синхронную реализацию унифицированного клиента."""

_UNI_AIO_CLIENT_MAPPER: dict[Exchange, type[IUniAioClient]] = {
    Exchange.BINANCE: BinanceUniAioClient
}
"""Маппер, который связывает биржу и асинхронную реализацию унифицированного клиента."""

_UNI_WS_MANAGER_MAPPER: dict[Exchange, type[IUniWebsocketManager]] = {
    Exchange.BINANCE: BinanceUniWebsocketManager
}
"""Маппер, который связывает биржу и синхронную реализацию унифицированного вебсокет-менеджера."""

_UNI_AIO_WS_MANAGER_MAPPER: dict[Exchange, type[IUniAioWebsocketManager]] = {
    Exchange.BINANCE: BinanceUniAioWebsocketManager
}
"""Маппер, который связывает биржу и асинхронную реализацию унифицированного вебсокет-менеджера."""


@overload
def get_uni_client(exchange: Exchange) -> type[IUniClient]: ...


@overload
def get_uni_client(exchange: Exchange, sync: Literal[True]) -> type[IUniClient]: ...


@overload
def get_uni_client(exchange: Exchange, sync: Literal[False]) -> type[IUniAioClient]: ...


def get_uni_client(exchange: Exchange, sync: bool = True) -> type[IUniClient] | type[IUniAioClient]:
    """Возвращает унифицированный клиент для указанной биржи.

    Параметры:
        exchange (`Exchange`): Биржа.
        sync (`bool`): Если True, возвращает синхронный клиент. Иначе - асинхронный. По умолчанию True.

    Возвращает:
        `type[IUniClient] | type[IUniAioClient]`: Унифицированный клиент для указанной биржи.
    """
    try:
        if sync:
            return _UNI_CLIENT_MAPPER[exchange]
        else:
            return _UNI_AIO_CLIENT_MAPPER[exchange]
    except KeyError as e:
        raise NotSupported(f"Unsupported exchange: {exchange}") from e


@overload
def get_uni_websocket_manager(exchange: Exchange) -> type[IUniWebsocketManager]: ...


@overload
def get_uni_websocket_manager(
    exchange: Exchange, sync: Literal[True]
) -> type[IUniWebsocketManager]: ...


@overload
def get_uni_websocket_manager(
    exchange: Exchange, sync: Literal[False]
) -> type[IUniAioWebsocketManager]: ...


def get_uni_websocket_manager(
    exchange: Exchange, sync: bool = True
) -> type[IUniWebsocketManager] | type[IUniAioWebsocketManager]:
    """Возвращает унифицированный вебсокет-менеджер для указанной биржи.

    Параметры:
        exchange (`Exchange`): Биржа.
        sync (`bool`): Если True, возвращает синхронный вебсокет-менеджер. Иначе - асинхронный. По умолчанию True.

    Возвращает:
        `type[IUniWebsocketManager] | type[IUniAioWebsocketManager]`: Унифицированный вебсокет-менеджер для указанной биржи.
    """
    try:
        if sync:
            return _UNI_WS_MANAGER_MAPPER[exchange]
        else:
            return _UNI_AIO_WS_MANAGER_MAPPER[exchange]
    except KeyError as e:
        raise NotSupported(f"Unsupported exchange: {exchange}") from e
