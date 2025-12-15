__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Kucoin."""

    exchange_name = "Kucoin"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        tickers_info = {}
        exchange_info = await Client(session).symbol("SPOT")
        for el in exchange_info["data"]["list"]:
            tickers_info[el["symbol"]] = TickerInfoItem(
                tick_precision=None,
                tick_step=None,
                size_precision=None,
                size_step=None,
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        tickers_info = {}
        exchange_info = await Client(session).symbol("FUTURES")
        for el in exchange_info["data"]["list"]:
            tickers_info[el["symbol"]] = TickerInfoItem(
                tick_precision=None,
                tick_step=None,
                size_precision=None,
                size_step=None,
                contract_size=float(el["unitSize"]),
            )

        cls._futures_tickers_info = tickers_info
