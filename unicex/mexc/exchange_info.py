__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Mexc."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        futures_tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://contract.mexc.com/api/v1/contract/detail"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["data"]:
                    futures_tickers_info[el["symbol"]] = TickerInfoItem(
                        tick_precision=cls._step_size_to_precision(el["priceUnit"]),
                        size_precision=el["amountScale"],
                        contract_size=el["contractSize"],
                        min_market_size=el["minVol"],
                        max_market_size=el["maxVol"],
                        min_limit_size=el["minVol"],
                        max_limit_size=el["maxVol"],
                    )

            cls._futures_tickers_info = futures_tickers_info
            cls._logger.debug("Mexc futures exchange info loaded")
