__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Mexc."""

    exchange_name = "Mexc"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        ...

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        tickers_info = {}
        exchange_info = await Client(session).futures_contract_detail()
        for el in exchange_info["data"]:
            tickers_info[el["symbol"]] = TickerInfoItem(
                tick_precision=el["priceUnit"],
                tick_step=None,
                size_precision=el["amountScale"],
                size_step=None,
                contract_size=el["contractSize"],
            )

        cls._futures_tickers_info = tickers_info
