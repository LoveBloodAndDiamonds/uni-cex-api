__all__ = [
    "BybitUniClient",
]

from functools import cached_property

from unicex._abc import IUniClient
from unicex.enums import Exchange, Timeframe
from unicex.types import KlineDict, TickerDailyDict

from .adapter import BybitAdapter
from .client import BybitClient


class BybitUniClient(IUniClient[BybitClient]):
    """Унифицированный клиент для работы с Bybit API."""

    @cached_property
    def adapter(self) -> BybitAdapter:
        """Возвращает реализацию адаптера для Bybit.

        Возвращает:
            BybitAdapter: Реализация адаптера для Bybit.
        """
        return BybitAdapter()

    @property
    def client_cls(self) -> type[BybitClient]:
        """Возвращает класс клиента для Bybit.

        Возвращает:
            type[BybitClient]: Класс клиента для Bybit.
        """
        return BybitClient

    def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = self._client.instruments_info(category="spot")
        return self.adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров для фьючерсов.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = self._client.futures_instruments_info(category="linear")
        return self.adapter.futures_tickers(raw_data=raw_data, only_usdt=only_usdt)

    def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = self._client.tickers(category="spot")
        return self.adapter.ticker_24h(raw_data=raw_data)

    def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера фьючерсов.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = self._client.futures_tickers(category="linear")
        return self.adapter.futures_ticker_24h(raw_data=raw_data)

    def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = self._client.tickers(category="spot")
        return self.adapter.last_price(raw_data)

    def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера фьючерсов.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = self._client.futures_tickers(category="linear")
        return self.adapter.futures_last_price(raw_data)

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
            interval (Timeframe | str): Таймфрейм свечей.
            limit (int | None): Количество свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raw_data = self._client.klines(
            category="spot",
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.BYBIT),  # type: ignore
            start=start_time,
            end=end_time,
            limit=limit,
        )
        return self.adapter.klines(raw_data)

    def futures_klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера фьючерсов.

        Параметры:
            symbol (str): Название тикера.
            interval (Timeframe | str): Таймфрейм свечей.
            limit (int | None): Количество свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        raw_data = self._client.futures_klines(
            category="linear",
            symbol=symbol,
            interval=interval.to_exchange_format(Exchange.BYBIT),  # type: ignore
            start=start_time,
            end=end_time,
            limit=limit,
        )
        return self.adapter.futures_klines(raw_data)

    def funding_rate(self, only_usdt: bool = True) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """
        raw_data = self._client.futures_tickers()
        return self.adapter.funding_rate(raw_data, only_usdt)
