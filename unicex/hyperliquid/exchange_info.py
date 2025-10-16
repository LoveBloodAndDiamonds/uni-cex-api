__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Hyperliquid."""

    exchange_name = "Hyperliquid"
    """Название биржи, на которой работает класс."""

    _spot_meta: dict = {}
    """Словарь с метаинформацией о спотовом рынке."""

    _spot_ident_to_idx: dict = {}
    """Словарь, в котором ключ - индетефикатор тикера на бирже, например '@123', а значение - его индекс в _spot_meta."""

    _spot_idx_to_name: dict = {}
    """Словарь, в котором ключ - индекс в _spot_meta, например "123", а значение - название тикера, например 'BTC'."""

    _futures_meta: dict = {}
    """Словарь с метаинформацией о фьючерсном рынке."""

    # DOCS: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/tick-and-lot-size

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        cls._spot_meta = await Client(session).spot_metadata()
        cls._build_spot_mappings(cls._spot_meta)

        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in cls._spot_meta["tokens"]:
            tickers_info[symbol_info["name"]] = TickerInfoItem(
                tick_step=None,
                tick_precision=int(symbol_info["weiDecimals"]),
                size_step=None,
                size_precision=int(symbol_info["szDecimals"]),
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        cls._futures_meta = await Client(session).perp_metadata()

    @classmethod
    def _build_spot_mappings(cls, spot_meta: dict) -> None:
        """Строит словари соответствия '@индекс' ↔ индекс ↔ 'BTC'."""
        universe = spot_meta["universe"]
        tokens = spot_meta["tokens"]

        number_to_idx = {}
        for u in universe:
            number_to_idx[u["name"]] = u["tokens"][0]
        cls._spot_ident_to_idx = number_to_idx

        idx_to_name = {}
        for t in tokens:
            idx_to_name[t["index"]] = t["name"]
        cls._spot_idx_to_name = idx_to_name

    @classmethod
    def get_spot_meta(cls) -> dict:
        """Возвращает метаинформацию о спотовом рынке."""
        cls._check_loaded()
        return cls._spot_meta

    @classmethod
    def get_futures_meta(cls) -> dict:
        """Возвращает метаинформацию о фьючерсном рынке."""
        cls._check_loaded()
        return cls._futures_meta

    @classmethod
    def resolve_spot_symbol(cls, ident: str) -> str:
        """Преобразует внутренний идентификатор вида '@142' в тикер, например 'BTC'.
        Не рейзит KeyError, если тикер не найден.

        Параметры:
            token_name (str): Имя токена на бирже, например '@142' или 'BTC'.

        Возвращает:
            str | None: Название тикера (например 'BTC'), либо None, если не найден.
        """
        cls._check_loaded()

        try:
            return cls._spot_idx_to_name[cls._spot_ident_to_idx[ident]]
        except KeyError:
            return ident

    @classmethod
    def resolve_spot_ident(cls, symbol: str) -> str:
        """Преобразует тикер (например, 'BTC') в внутренний идентификатор (например, '@142').

        Параметры:
            symbol (str): Название тикера, например 'BTC'.

        Возвращает:
            str: Внутренний идентификатор (например '@142').

        Исключения:
            KeyError: Если тикер не найден в локальном кэше биржи.
        """
        cls._check_loaded()

        # Находим индекс по тикеру
        idx = next(k for k, v in cls._spot_idx_to_name.items() if v == symbol)

        # Возвращаем внутренний идентификатор вида "@142"
        return next(k for k, v in cls._spot_ident_to_idx.items() if v == idx)
