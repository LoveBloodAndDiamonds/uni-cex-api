__all__ = ["UniClient"]

from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import KlineDict, OpenInterestDict, OpenInterestItem, TickerDailyDict

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Bitget API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для конкретной биржи.

        Возвращает:
            `type[Client]`: Класс клиента.
        """
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        raw_data = await self._client.get_ticker_information()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.get_ticker_information()
        return Adapter.last_price(raw_data=raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.last_price(raw_data=raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `TickerDailyDict`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.get_ticker_information()
        return Adapter.ticker_24hr(raw_data=raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `TickerDailyDict`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.ticker_24hr(raw_data=raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
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
        interval = (
            interval.to_exchange_format(Exchange.BITGET, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.get_candlestick_data(
            symbol=symbol,
            granularity=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
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
        interval = (
            interval.to_exchange_format(Exchange.BITGET, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_get_candlestick_data(
            symbol=symbol,
            product_type="USDT-FUTURES",
            granularity=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        """Возвращает ставку финансирования для тикера или всех тикеров, если тикер не указан.

        - Параметры:
        symbol (`str | None`): Название тикера (Опционально).

        Возвращает:
          `dict[str, float] | float`: Ставка финансирования для тикера или словарь со ставками для всех тикеров.
        """
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

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
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data
