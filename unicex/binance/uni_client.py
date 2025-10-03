__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import KlineDict, OpenInterestItem, TickerDailyDict

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Binance API."""

    @property
    def _client_cls(self) -> type[Client]:
        """Возвращает класс клиента для Binance.

        Возвращает:
            type[Client]: Класс клиента для Binance.
        """
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.ticker_price()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.futures_ticker_price()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.ticker_price()
        return Adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.futures_ticker_price()
        return Adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.futures_ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not ommited

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
            interval.to_exchange_format(Exchange.BINANCE, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.klines(
            symbol=symbol,
            interval=interval,
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
            interval.to_exchange_format(Exchange.BINANCE, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_klines(
            symbol=symbol,
            interval=interval,
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
        raw_data = await self._client.futures_mark_price(symbol=symbol)
        adapted_data = Adapter.funding_rate(raw_data if isinstance(raw_data, list) else [raw_data])  # type: ignore[arg-type]
        return adapted_data[symbol] if symbol else adapted_data

    async def open_interest(self, symbol: str = None) -> OpenInterestItem:  # type: ignore[reportArgumentType] | We should provide our exception message
        """Возвращает объем открытого интереса для тикера.

        Параметры:
            symbol (`str`): Название тикера.

        Возвращает:
            `OpenInterestItem`: Словарь со временем и объемом открытого интереса в монетах.
        """
        if not symbol:
            raise ValueError("Symbol is required for binance open interest")
        raw_data = await self._client.open_interest(symbol=symbol)
        return Adapter.open_interest(raw_data)
