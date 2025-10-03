__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Xt."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://fapi.xt.com/future/market/v3/public/symbol/list"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["result"]["symbols"]:
                    # стоимость одного контракта
                    contract_size = float(el["contractSize"])

                    tickers_info[el["symbol"]] = TickerInfoItem(
                        tick_precision=0,
                        size_precision=0,
                        contract_size=contract_size,
                    )
        cls._tickers_info = tickers_info
        cls._logger.debug("Okx exchange info loaded")
