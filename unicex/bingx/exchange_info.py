__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи BingX."""

    exchange_name = "BingX"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        ...

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        ...
