__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Timeframe
from unicex.types import KlineDict, OpenInterestDict, OpenInterestItem, TickerDailyDict

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Kucoin API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для Kucoin.

        Возвращает:
            type[Client]: Класс клиента для Kucoin.
        """
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.ticker("SPOT")
        return Adapter.tickers(raw_data, only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.ticker("FUTURES")
        return Adapter.tickers(raw_data, only_usdt)

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.ticker("SPOT")
        return Adapter.last_price(raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.ticker("FUTURES")
        return Adapter.last_price(raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.ticker("SPOT")
        return Adapter.ticker_24hr(raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.ticker("FUTURES")
        return Adapter.ticker_24hr(raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера.
            limit (int | None): Количество свечей.
            interval (Timeframe | str): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raise NotImplementedError()

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера.
            limit (int | None): Количество свечей.
            interval (Timeframe | str): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raise NotImplementedError()

    async def funding_rate(self) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """
        raise NotImplementedError()

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        """Возвращает объем открытого интереса для тикера или всех тикеров, если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера. (Опционально, но обязателен для следующих бирж: BINANCE).

        Возвращает:
            `OpenInterestItem | OpenInterestDict`: Если тикер передан - словарь со временем и объемом
                открытого интереса в монетах. Если нет передан - то словарь, в котором ключ - тикер,
                а значение - словарь с временем и объемом открытого интереса в монетах.
        """
        raw_data = await self._client.open_interest()
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data
