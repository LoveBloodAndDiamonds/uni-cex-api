__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Okx."""

    exchange_name = "Okx"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        tickers_info = {}
        exchange_info = await Client(session).get_instruments("SPOT")
        for el in exchange_info["data"]:
            tickers_info[el["instId"]] = TickerInfoItem(
                tick_precision=None,
                tick_step=float(el["tickSz"]),
                size_precision=None,
                size_step=float(el["lotSz"]),
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        tickers_info = {}
        exchange_info = await Client(session).get_instruments("SWAP")
        for el in exchange_info["data"]:
            tickers_info[el["instId"]] = TickerInfoItem(
                tick_precision=None,
                tick_step=float(el["tickSz"]),
                size_precision=None,
                size_step=float(el["lotSz"]) * float(el["ctVal"]),
                contract_size=float(el["ctVal"]),
            )

        cls._futures_tickers_info = tickers_info
