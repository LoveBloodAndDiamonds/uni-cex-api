__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Mexc."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://contract.mexc.com/api/v1/contract/detail"
            async with session.get(url) as response:
                data = await response.json()
                for contract in data["data"]:
                    # стоимость одного контракта
                    contract_size = float(contract["contractSize"])

                    tickers_info[contract["symbol"]] = TickerInfoItem(
                        tick_precision=0,
                        size_precision=0,
                        contract_size=contract_size,
                    )

        cls._tickers_info = tickers_info
        cls._logger.debug("Mexc exchange info loaded")
