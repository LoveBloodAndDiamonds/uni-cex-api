__all__ = ["UniClient"]


import time
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, Timeframe
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
        return Adapter.futures_tickers(raw_data, only_usdt)

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
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit or (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            start_time, end_time = self.limit_to_start_and_end_time(
                interval, limit, use_milliseconds=False
            )
        interval = (
            interval.to_exchange_format(Exchange.KUCOIN)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.kline(
            trade_type="SPOT",
            symbol=symbol,
            interval=interval,
            start_at=self.to_seconds(start_time),
            end_at=self.to_seconds(end_time),
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
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit or (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            start_time, end_time = self.limit_to_start_and_end_time(
                interval, limit, use_milliseconds=False
            )
        interval = (
            interval.to_exchange_format(Exchange.KUCOIN)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.kline(
            trade_type="FUTURES",
            symbol=symbol,
            interval=interval,
            start_at=self.to_seconds(start_time),
            end_at=self.to_seconds(end_time),
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        """Возвращает ставку финансирования для тикера.

        Параметры:
            symbol (`str | None`): Название тикера. На Kucoin параметр обязателен.

        Возвращает:
            `dict[str, float] | float`: Ставка финансирования в процентах.
        """
        if not symbol:
            raise ValueError("Symbol is required to fetch Kucoin funding rate")

        end_time = int(time.time() * 1000)
        # Kucoin публикует ставку каждые 8 часов, берем окно в 24 часа для гарантии наличия записи.
        start_time = end_time - 24 * 60 * 60 * 1000
        raw_data = await self._client.funding_rate_history(
            symbol=symbol,
            start_at=start_time,
            end_at=end_time,
        )
        adapted_data = Adapter.funding_rate(raw_data)
        if symbol not in adapted_data:
            raise ValueError(f"Kucoin funding rate history is empty for {symbol}")
        return adapted_data[symbol]

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
