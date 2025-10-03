__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Kcex."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://www.kcex.com/fapi/v1/contract/detailV2?client=web"
            async with session.get(url) as response:
                data = (await response.json())["data"]
                for el in data:
                    # стоимость одного контракта
                    contract_size = float(el["cs"])

                    tickers_info[el["symbol"]] = TickerInfoItem(
                        tick_precision=0,
                        size_precision=0,
                        contract_size=contract_size,
                    )

        cls._tickers_info = tickers_info
        cls._logger.debug("Kcex exchange data loaded")
