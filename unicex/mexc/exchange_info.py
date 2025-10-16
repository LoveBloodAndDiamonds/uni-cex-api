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
        exchange_info = await Client(session).exchange_info()
        tickers_info = {}
        for el in exchange_info["symbols"]:
            tickers_info[el["symbol"]] = TickerInfoItem(
                tick_precision=int(el["quotePrecision"]),
                tick_step=None,
                size_precision=int(el["baseAssetPrecision"]),
                size_step=None,
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        exchange_info = await Client(session).futures_contract_detail()
        tickers_info = {}
        for el in exchange_info["data"]:
            tickers_info[el["symbol"]] = TickerInfoItem(
                tick_precision=None,
                tick_step=el["priceUnit"],
                size_precision=None,
                size_step=el["contractSize"],
                contract_size=el["contractSize"],
            )

        cls._futures_tickers_info = tickers_info
