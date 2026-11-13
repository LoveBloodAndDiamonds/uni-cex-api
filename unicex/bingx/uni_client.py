__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import MarginType, OrderSide, OrderType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    FundingInfoDict,
    FundingInfoItem,
    KlineDict,
    LongShortRatioItem,
    OpenInterestDict,
    OpenInterestItem,
    OrderIdDict,
    PositionInfoDict,
    TickerDailyDict,
)

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с BingX API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.symbols()
        return Adapter.tickers(raw_data, only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_contracts()
        return Adapter.tickers(raw_data, only_usdt)

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.ticker_24hr()
        return Adapter.last_price(raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_ticker_price()
        return Adapter.last_price(raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.ticker_24hr()
        return Adapter.ticker_24hr(raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_ticker_24hr()
        return Adapter.ticker_24hr(raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = interval.value if isinstance(interval, Timeframe) else interval
        raw_data = await self._client.klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return Adapter.klines(raw_data)

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = interval.value if isinstance(interval, Timeframe) else interval
        raw_data = await self._client.futures_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )
        return Adapter.klines(raw_data)

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.futures_mark_price(symbol=symbol)
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_interval(self, symbol: str) -> int: ...

    @overload
    async def funding_interval(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_interval(self) -> dict[str, int]: ...

    async def funding_interval(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.futures_mark_price(symbol=symbol)
        adapted_data = Adapter.funding_interval(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_next_time(self, symbol: str) -> int: ...

    @overload
    async def funding_next_time(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_next_time(self) -> dict[str, int]: ...

    async def funding_next_time(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.futures_mark_price(symbol=symbol)
        adapted_data = Adapter.funding_next_time(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_info(self, symbol: str) -> FundingInfoItem: ...

    @overload
    async def funding_info(self, symbol: None) -> FundingInfoDict: ...

    @overload
    async def funding_info(self) -> FundingInfoDict: ...

    async def funding_info(self, symbol: str | None = None) -> FundingInfoItem | FundingInfoDict:
        raw_data = await self._client.futures_mark_price(symbol=symbol)
        adapted_data = Adapter.funding_info(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        if not symbol:
            raise ValueError("Symbol is required for bingx open interest")
        raw_data = await self._client.open_interest(symbol=symbol)
        return Adapter.open_interest(raw_data)

    async def long_short_ratio_history(
        self, symbol: str, period: Timeframe = Timeframe.MIN_5, limit: int = 30
    ) -> list[LongShortRatioItem]:
        raise NotImplementedError(
            "Method `long_short_ratio_history` cannot be implemented for BingX: "
            "public swap API has no long/short account ratio endpoint."
        )

    @overload
    async def futures_best_bid_ask(self, symbol: str) -> BestBidAskItem: ...

    @overload
    async def futures_best_bid_ask(self, symbol: None) -> BestBidAskDict: ...

    @overload
    async def futures_best_bid_ask(self) -> BestBidAskDict: ...

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        if symbol:
            raw_data = await self._client.futures_book_ticker(symbol=symbol)
            return Adapter.futures_best_bid_ask(raw_data)[symbol]
        raw_data = await self._client.futures_ticker_24hr()
        return Adapter.futures_best_bid_ask(raw_data)

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        valid_limits = {5, 10, 20, 50, 100, 500, 1000}
        if limit not in valid_limits:
            raise ValueError(
                f"Invalid limit for bingx futures depth: {limit}. Valid values: {sorted(valid_limits)}"
            )
        raw_data = await self._client.futures_order_book(symbol=symbol, limit=limit)
        return Adapter.futures_depth(raw_data, symbol=symbol)

    async def futures_delistings(self) -> dict[str, int]:
        raw_data = await self._client.futures_contracts()
        return Adapter.futures_delistings(raw_data)

    async def futures_order_create(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        quantity: str,
        price: str | None = None,
        client_order_id: str | None = None,
        reduce_only: bool | None = None,
    ) -> OrderIdDict:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_position_info(self, symbol: str) -> PositionInfoDict:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_set_leverage(self, symbol: str, leverage: int) -> None:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_set_margin_type(self, symbol: str, margin_type: MarginType) -> None:
        raise NotImplementedError("Method will be implemented later.")
