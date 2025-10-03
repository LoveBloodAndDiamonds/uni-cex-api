__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import KlineDict, OpenInterestDict, OpenInterestItem, TickerDailyDict

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Gateio API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для Gateio.

        Возвращает:
            type[Client]: Класс клиента для Gateio.
        """
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.tickers()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.futures_tickers(settle="usdt")
        return Adapter.futures_tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.tickers()
        return Adapter.last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.futures_tickers(settle="usdt")
        return Adapter.futures_last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.tickers()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.futures_tickers(settle="usdt")
        return Adapter.futures_ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

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
        interval = (
            interval.to_exchange_format(Exchange.GATEIO, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.candlesticks(
            currency_pair=symbol,
            interval=interval,
            limit=limit,
            from_time=self._to_seconds(start_time),
            to_time=self._to_seconds(end_time),
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)  # type: ignore[reportArgumentType]

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
        interval = (
            interval.to_exchange_format(Exchange.GATEIO, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_candlesticks(
            settle="usdt",
            contract=symbol,
            interval=interval,
            limit=limit,
            from_time=self._to_seconds(start_time),
            to_time=self._to_seconds(end_time),
        )
        return Adapter.futures_klines(raw_data=raw_data, symbol=symbol)  # type: ignore[reportArgumentType]

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
        raw_data = await self._client.futures_tickers(settle="usdt", contract=symbol)
        items = raw_data if isinstance(raw_data, list) else [raw_data]
        adapted_data = Adapter.funding_rate(raw_data=items)  # type: ignore[reportArgumentType]
        if symbol:
            return adapted_data[symbol]
        return adapted_data

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
        raw_data = await self._client.futures_tickers(settle="usdt", contract=symbol)
        items = raw_data if isinstance(raw_data, list) else [raw_data]
        adapted_data = Adapter.open_interest(raw_data=items)  # type: ignore[reportArgumentType]
        if symbol:
            return adapted_data[symbol]
        return adapted_data

    @staticmethod
    def _to_seconds(value: int | None) -> int | None:
        """Преобразует значение из миллисекунд в секунды для передачи в API."""
        if value is None:
            return None
        if value >= 1_000_000_000_000:
            return value // 1000
        return value
