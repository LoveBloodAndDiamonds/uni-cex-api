__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Xt."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        futures_tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://fapi.xt.com/future/market/v3/public/symbol/list"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["result"]["symbols"]:
                    futures_tickers_info[el["symbol"]] = TickerInfoItem(
                        tick_precision=0,
                        size_precision=0,
                        contract_size=float(el["contractSize"]),
                        min_market_size=None,
                        max_market_size=None,
                        min_limit_size=None,
                        max_limit_size=None,
                    )
        cls._futures_tickers_info = futures_tickers_info
        cls._logger.debug("Xt futures exchange info loaded")
