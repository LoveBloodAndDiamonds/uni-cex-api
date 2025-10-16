__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Bybit."""

    exchange_name = "Bybit"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        exchange_info = await Client(session).instruments_info("spot")
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in exchange_info["result"]["list"]:
            tickers_info[symbol_info["symbol"]] = TickerInfoItem(
                tick_step=float(symbol_info["priceFilter"]["tickSize"]),
                tick_precision=None,
                size_step=float(symbol_info["lotSizeFilter"]["basePrecision"]),
                size_precision=None,
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        exchange_info = await Client(session).instruments_info("linear", limit=1000)
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in exchange_info["result"]["list"]:
            try:
                tickers_info[symbol_info["symbol"]] = TickerInfoItem(
                    tick_step=float(symbol_info["priceFilter"]["tickSize"]),
                    tick_precision=None,
                    size_step=float(symbol_info["lotSizeFilter"]["qtyStep"]),
                    size_precision=None,
                    contract_size=1,
                )
            except ValueError as e:
                cls._logger.trace(
                    f"ValueError on {cls.exchange_name} by {symbol_info['symbol']}: {e}"
                )
        cls._futures_tickers_info = tickers_info
