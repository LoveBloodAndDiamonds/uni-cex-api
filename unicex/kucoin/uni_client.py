__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarginType, OrderSide, OrderType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    OrderIdDict,
    PositionInfoDict,
    TickerDailyDict,
)

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Kucoin API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.ticker("SPOT")
        return Adapter.tickers(raw_data, only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.ticker("FUTURES")
        return Adapter.futures_tickers(raw_data, only_usdt)

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.ticker("SPOT")
        return Adapter.last_price(raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.ticker("FUTURES")
        return Adapter.last_price(raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.ticker("SPOT")
        return Adapter.ticker_24hr(raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
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
        if not symbol:
            raise ValueError("Symbol is required to fetch Kucoin funding rate")
        raw_data = await self._client.funding_rate(symbol=symbol)
        return Adapter.funding_rate(raw_data)

    @overload
    async def funding_interval(self, symbol: str) -> int: ...

    @overload
    async def funding_interval(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_interval(self) -> dict[str, int]: ...

    async def funding_interval(self, symbol: str | None = None) -> dict[str, int] | int:
        raise NotImplementedError("This method will be implemented in a future release")

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.open_interest()
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        raise NotImplementedError("Method `futures_best_bid_ask` will be implemented later")

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        raise NotImplementedError(
            "Method 'futures_depth' will be implemented later. You can open pull request to contribute."
        )

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

    async def futures_set_leverage(self, symbol: str) -> None:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_set_margin_type(self, symbol: str, margin_type: MarginType) -> None:
        raise NotImplementedError("Method will be implemented later.")
