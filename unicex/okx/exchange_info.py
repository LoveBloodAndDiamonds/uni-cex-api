__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Okx."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        tickers_info = {}
        async with aiohttp.ClientSession() as session:
            url = "https://www.okx.com/api/v5/public/instruments?instType=SWAP"
            async with session.get(url) as response:
                data = await response.json()
                for el in data["data"]:
                    print(el)
                    # минимальный шаг цены
                    tick_size = el["tickSz"]
                    # минимальный шаг количества
                    step_size = el["lotSz"]
                    # стоимость одного контракта
                    contract_size = float(el["ctVal"])

                    tickers_info[el["instId"]] = TickerInfoItem(
                        tick_precision=cls.step_size_to_precision(tick_size),
                        size_precision=cls.step_size_to_precision(step_size),
                        contract_size=contract_size,
                    )
        cls._tickers_info = tickers_info
        cls._logger.debug("Okx exchange info loaded")
