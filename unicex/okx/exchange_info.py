__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Okx."""

    exchange_name = "Okx"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        tickers_info = {}
        url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
        async with session.get(url) as response:
            data = await response.json()
            for el in data["data"]:
                tickers_info[el["instId"]] = TickerInfoItem(
                    tick_precision=cls._step_size_to_precision(el["tickSz"]),
                    size_precision=cls._step_size_to_precision(el["lotSz"]),
                    contract_size=1,
                )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        futures_tickers_info = {}
        url = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"
        async with session.get(url) as response:
            data = await response.json()
            for el in data["data"]:
                futures_tickers_info[el["instId"]] = TickerInfoItem(
                    tick_precision=cls._step_size_to_precision(el["tickSz"]),
                    size_precision=cls._step_size_to_precision(el["lotSz"]),
                    contract_size=float(el["ctVal"]),
                )

        cls._futures_tickers_info = futures_tickers_info
