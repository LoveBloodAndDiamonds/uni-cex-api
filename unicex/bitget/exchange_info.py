__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Bitget."""

    exchange_name = "Bitget"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        exchange_info = await Client(session).get_symbol_info()
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in exchange_info["data"]:
            tickers_info[symbol_info["symbol"]] = TickerInfoItem(
                tick_precision=int(symbol_info["pricePrecision"]),
                tick_step=None,
                size_precision=int(symbol_info["quantityPrecision"]),
                size_step=None,
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        tickers_info: dict[str, TickerInfoItem] = {}
        exchange_info = await Client(session).futures_get_contracts("USDT-FUTURES")
        for symbol_info in exchange_info["data"]:
            symbol = symbol_info["symbol"]
            tickers_info[symbol] = TickerInfoItem(
                tick_precision=int(symbol_info["pricePlace"]),
                tick_step=None,
                size_precision=int(symbol_info["volumePlace"]),
                size_step=None,
                contract_size=float(symbol_info["sizeMultiplier"]),
            )

        cls._futures_tickers_info = tickers_info
