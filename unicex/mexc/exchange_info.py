__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


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
        futures_tickers_info = {}
        url = "https://contract.mexc.com/api/v1/contract/detail"
        async with session.get(url) as response:
            data = await response.json()
            for el in data["data"]:
                futures_tickers_info[el["symbol"]] = TickerInfoItem(
                    tick_precision=cls._step_size_to_precision(el["priceUnit"]),
                    size_precision=el["amountScale"],
                    contract_size=el["contractSize"],
                )

        cls._futures_tickers_info = futures_tickers_info
