__all__ = ["UniClient"]


import time
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
)

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Mexc API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.ticker_24hr()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.ticker_24hr()
        return Adapter.last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_ticker()
        return Adapter.futures_ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = (
            interval.to_exchange_format(Exchange.MEXC, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.klines(
            symbol=symbol,
            interval=interval,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
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
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit and (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию Mexc Futures не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            end_time = int(time.time())
            start_time = end_time - (limit * interval.to_seconds)  # type: ignore[reportOptionalOperand]

        interval = (
            interval.to_exchange_format(Exchange.MEXC, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_kline(
            symbol=symbol,
            interval=interval,
            start=start_time,
            end=end_time,
        )
        return Adapter.futures_klines(raw_data=raw_data, symbol=symbol)

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.futures_ticker()
        adapted_data = Adapter.funding_rate(raw_data=raw_data)  # type: ignore[reportArgumentType]
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.futures_ticker()
        adapted_data = Adapter.open_interest(raw_data=raw_data)  # type: ignore[reportArgumentType]
        if symbol:
            return adapted_data[symbol]
        return adapted_data

    @overload
    async def futures_best_bid_ask(self, symbol: str) -> BestBidAskItem: ...

    @overload
    async def futures_best_bid_ask(self, symbol: None) -> BestBidAskDict: ...

    @overload
    async def futures_best_bid_ask(self) -> BestBidAskDict: ...

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        raw_data = await self._client.futures_ticker(symbol=symbol)
        adapted_data = Adapter.futures_best_bid_ask(raw_data=raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        raise NotImplementedError(
            "Method 'futures_depth' will be implemented later. You can open pull request to contribute."
        )
