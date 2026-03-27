__all__ = ["UniClient"]


import asyncio
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarginType, OrderSide, OrderType, Timeframe
from unicex.exceptions import ResponseError
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    FundingInfoDict,
    FundingInfoItem,
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
    """Унифицированный клиент для работы с Bybit API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.tickers("spot")
        return Adapter.tickers(raw_data, only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.tickers("linear")
        return Adapter.tickers(raw_data, only_usdt)

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.tickers("spot")
        return Adapter.last_price(raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.tickers("linear")
        return Adapter.last_price(raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.tickers("spot")
        return Adapter.ticker_24hr(raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.tickers("linear")
        return Adapter.ticker_24hr(raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = (
            interval.to_exchange_format(Exchange.BYBIT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.klines(
            category="spot",
            symbol=symbol,
            interval=interval,
            start=start_time,
            end=end_time,
            limit=limit,
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
        interval = (
            interval.to_exchange_format(Exchange.BYBIT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.klines(
            category="linear",
            symbol=symbol,
            interval=interval,
            start=start_time,
            end=end_time,
            limit=limit,
        )
        return Adapter.klines(raw_data)

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.tickers("linear", symbol=symbol)
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_interval(self, symbol: str) -> int: ...

    @overload
    async def funding_interval(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_interval(self) -> dict[str, int]: ...

    async def funding_interval(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.instruments_info(
            category="linear",
            symbol=symbol,
            limit=1000,
        )
        adapted_data = Adapter.funding_interval(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_next_time(self, symbol: str) -> int: ...

    @overload
    async def funding_next_time(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_next_time(self) -> dict[str, int]: ...

    async def funding_next_time(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.tickers("linear", symbol=symbol)
        adapted_data = Adapter.funding_next_time(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def funding_info(self, symbol: str | None = None) -> FundingInfoItem | FundingInfoDict:
        tickers_data, instruments_data = await asyncio.gather(
            self._client.tickers("linear", symbol=symbol),
            self._client.instruments_info(category="linear", symbol=symbol, limit=1000),
        )
        adapted_data = Adapter.funding_info(tickers_data, instruments_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.tickers("linear")
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def futures_best_bid_ask(self, symbol: str) -> BestBidAskItem: ...

    @overload
    async def futures_best_bid_ask(self, symbol: None) -> BestBidAskDict: ...

    @overload
    async def futures_best_bid_ask(self) -> BestBidAskDict: ...

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        raw_data = await self._client.tickers("linear", symbol=symbol)
        adapted_data = Adapter.best_bid_ask(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        if not 1 <= limit <= 500:
            raise ValueError(
                f"Invalid limit for bybit futures depth: {limit}. Valid range: [1, 500]"
            )

        raw_data = await self._client.orderbook(
            category="linear",
            symbol=symbol,
            limit=limit,
        )
        return Adapter.depth(raw_data)

    async def futures_delistings(self) -> dict[str, int]:
        raw_data = await self._client.instruments_info("linear", limit=1000)
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
        self.ensure_authorized()

        raw_data = await self.client.create_order(
            category="linear",
            symbol=symbol,
            side=side.to_exchange_format(Exchange.BYBIT),  # type: ignore
            order_type=type.to_exchange_format(Exchange.BYBIT),  # type: ignore
            qty=quantity,
            price=price,
            order_link_id=client_order_id,
            reduce_only=reduce_only,
        )

        return Adapter.order_create(raw_data)

    async def futures_position_info(self, symbol: str) -> PositionInfoDict:
        self.ensure_authorized()

        raw_data = await self._client.position_info(
            category="linear",
            symbol=symbol,
        )
        return Adapter.futures_position_info(raw_data)

    async def futures_set_leverage(self, symbol: str, leverage: int) -> None:
        self.ensure_authorized()

        try:
            await self._client.set_leverage(
                category="linear",
                symbol=symbol,
                buy_leverage=str(leverage),
                sell_leverage=str(leverage),
            )
        except ResponseError as e:
            if e.code != "110043":
                raise e

    async def futures_set_margin_type(
        self,
        symbol: str | None,
        margin_type: MarginType,
    ) -> None:
        self.ensure_authorized()

        await self._client.set_margin_mode(
            set_margin_mode=margin_type.to_exchange_format(Exchange.BYBIT),  # type: ignore
        )


