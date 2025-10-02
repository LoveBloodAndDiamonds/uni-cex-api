__all__ = ["UniClient"]


import time
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import KlineDict, OpenInterestDict, OpenInterestItem, TickerDailyDict
from unicex.utils import symbol_to_exchange_format

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Mexc API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для Mexc.

        Возвращает:
            type[Client]: Класс клиента для Mexc.
        """
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.ticker_24hr()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.ticker_24hr()
        return Adapter.last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера.
            limit (int | None): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raw_data = await self._client.klines(
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.MEXC, MarketType.SPOT),
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера.
            limit (int | None): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию Mexc Futures не принимают этот параметр
            end_time = int(time.time())
            start_time = end_time - (limit * interval.to_seconds)  # type: ignore[reportOptionalOperand]
        raw_data = await self._client.futures_kline(
            symbol=symbol_to_exchange_format(symbol, Exchange.MEXC, MarketType.FUTURES),
            interval=interval.to_exchange_format(Exchange.MEXC),
            start=start_time,
            end=end_time,
        )
        return Adapter.futures_klines(raw_data=raw_data, symbol=symbol)

    async def funding_rate(self) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """
        raw_data = await self._client.futures_ticker()
        return Adapter.funding_rate(raw_data=raw_data)  # type: ignore[reportArgumentType]

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
        raw_data = await self._client.futures_ticker()
        adapted_data = Adapter.open_interest(raw_data=raw_data)  # type: ignore[reportArgumentType]
        if symbol:
            exchange_symbol = symbol_to_exchange_format(symbol, Exchange.MEXC, MarketType.FUTURES)
            return adapted_data[exchange_symbol]
        return adapted_data
