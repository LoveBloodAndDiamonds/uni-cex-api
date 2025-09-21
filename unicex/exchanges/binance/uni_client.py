__all__ = [
    "UniBinanceClient",
    "AsyncUniBinanceClient",
]

from functools import cached_property

from unicex.abc import IUniAioClient, IUniClient
from unicex.enums import Exchange, Timeframe
from unicex.exceptions import NotSupported
from unicex.types import KlineDict, TickerDailyDict

from .adapter import BinanceAdapter
from .client import AsyncBinanceClient, BinanceClient


class UniBinanceClient(IUniClient[BinanceClient]):
    """Унифицированный клиент для работы с Binance API."""

    @cached_property
    def adapter(self) -> BinanceAdapter:
        """Возвращает реализацию адаптера для Binance.

        Возвращает:
            BinanceAdapter: Реализация адаптера для Binance.
        """
        return BinanceAdapter()

    @property
    def client_cls(self) -> type[BinanceClient]:
        """Возвращает класс клиента для Binance.

        Возвращает:
            type[BinanceClient]: Класс клиента для Binance.
        """
        return BinanceClient

    def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = self._client.ticker_price()
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = self._client.futures_ticker_price()
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = self._client.ticker_24h()
        return self.adapter.ticker_24h(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = self._client.futures_ticker_24h()
        return self.adapter.futures_ticker_24h(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = self._client.ticker_price()
        return self.adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = self._client.futures_ticker_price()
        return self.adapter.futures_last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def klines(
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
        raw_data = self._client.klines(
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.BINANCE),  # type: ignore
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return self.adapter.klines(raw_data)

    def futures_klines(
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
            interval (Timeframe): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raw_data = self._client.futures_klines(
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.BINANCE),  # type: ignore
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return self.adapter.futures_klines(raw_data)

    def funding_rate(self, only_usdt: bool = True) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """
        raw_data = self._client.futures_mark_price()
        return self.adapter.funding_rate(raw_data, only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    def open_interest(self, symbol: str) -> float:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (str | None): Название тикера (Опционально).

        Возвращает:
            float: Объем открытых позиций в монетах.
        """
        if not symbol:
            raise NotSupported("Open interest for all symbols is not supported for binance")

        raw_data = self._client.open_interest(symbol)
        return self.adapter.open_interest(raw_data)  # type: ignore | binance supports only single ticker open interest


class AsyncUniBinanceClient(IUniAioClient[AsyncBinanceClient]):
    """Унифицированный клиент для работы с Binance API."""

    @cached_property
    def adapter(self) -> BinanceAdapter:
        """Возвращает реализацию адаптера для Binance.

        Возвращает:
            BinanceAdapter: Реализация адаптера для Binance.
        """
        return BinanceAdapter()

    @property
    def client_cls(self) -> type[AsyncBinanceClient]:
        """Возвращает класс клиента для Binance.

        Возвращает:
            type[BinanceClient]: Класс клиента для Binance.
        """
        return AsyncBinanceClient

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.ticker_price()
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.futures_ticker_price()
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.ticker_24h()
        return self.adapter.ticker_24h(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.futures_ticker_24h()
        return self.adapter.futures_ticker_24h(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.ticker_price()
        return self.adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.futures_ticker_price()
        return self.adapter.futures_last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

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
            interval=interval.to_exchange_format(Exchange.BINANCE),  # type: ignore
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return self.adapter.klines(raw_data)

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
            interval (Timeframe): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raw_data = await self._client.futures_klines(
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.BINANCE),  # type: ignore
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return self.adapter.futures_klines(raw_data)

    async def funding_rate(self, only_usdt: bool = True) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """
        raw_data = await self._client.futures_mark_price()
        return self.adapter.funding_rate(raw_data, only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited
