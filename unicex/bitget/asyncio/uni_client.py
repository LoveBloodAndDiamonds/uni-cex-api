__all__ = ["UniClient"]

from functools import cached_property
from typing import overload

from unicex._abc.asyncio import IUniClient
from unicex.enums import Timeframe
from unicex.types import KlineDict, TickerDailyDict

from ..adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Binance API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для конкретной биржи.

        Возвращает:
            `type[Client]`: Класс клиента.
        """
        return Client

    @cached_property
    def adapter(self) -> Adapter:
        """Возвращает реализацию адаптера под конкретную биржу.

        Возвращает:
            `Adapter`: Реализация адаптера.
        """
        return Adapter()

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        raw_data = await self._client.get_tickers()
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        raise NotImplementedError()

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        raise NotImplementedError()

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        raise NotImplementedError()

    async def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.get_tickers()
        return self.adapter.ticker_24h(raw_data=raw_data)

    async def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raise NotImplementedError()

    async def klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            interval (`Timeframe`): Таймфрейм свечей.
            limit (`int`): Количество свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        raise NotImplementedError()

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            interval (`Timeframe`): Таймфрейм свечей.
            limit (`int`): Количество свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        raise NotImplementedError()

    async def funding_rate(self) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Возвращает:
            `dict[str, float]`: Ставка финансирования для каждого тикера.
        """
        raise NotImplementedError()

    @overload
    async def open_interest(self, symbol: str) -> float: ...

    @overload
    async def open_interest(self, symbol: None) -> dict[str, float]: ...

    async def open_interest(self, symbol: str | None) -> float | dict[str, float]:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера (Опционально).

        Возвращает:
            `float`: Объем открытых позиций в монетах.
        """
        raise NotImplementedError()
