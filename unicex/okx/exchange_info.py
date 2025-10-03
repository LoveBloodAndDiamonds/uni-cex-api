__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Okx."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        async with aiohttp.ClientSession() as session:
            tickers_info = {}
            url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["data"]:
                    tickers_info[el["instId"]] = TickerInfoItem(
                        tick_precision=cls._step_size_to_precision(el["tickSz"]),
                        size_precision=cls._step_size_to_precision(el["lotSz"]),
                        contract_size=1,
                        min_market_size=float(el["minSz"]),
                        max_market_size=float(el["maxMktSz"]),
                        min_limit_size=float(el["minSz"]),
                        max_limit_size=float(el["maxLmtSz"]),
                    )

            cls._tickers_info = tickers_info
            cls._logger.debug("Okx spot exchange info loaded")

            futures_tickers_info = {}
            url = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["data"]:
                    futures_tickers_info[el["instId"]] = TickerInfoItem(
                        tick_precision=cls._step_size_to_precision(el["tickSz"]),
                        size_precision=cls._step_size_to_precision(el["lotSz"]),
                        contract_size=float(el["ctVal"]),
                        min_market_size=el["minSz"],
                        max_market_size=el["maxMktSz"],
                        min_limit_size=el["minSz"],
                        max_limit_size=el["maxLmtSz"],
                    )

            cls._futures_tickers_info = futures_tickers_info
            cls._logger.debug("Okx futures exchange info loaded")
