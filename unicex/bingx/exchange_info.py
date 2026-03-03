__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo


class ExchangeInfo(IExchangeInfo):

    exchange_name = "BingX"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        ...

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        ...
