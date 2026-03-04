__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, OrderSide, OrderType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    OrderIdDict,
    OrderInfoDict,
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
        adapted_data = Adapter.futures_best_bid_ask(raw_data)
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
        return Adapter.futures_depth(raw_data)

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

        if type == OrderType.LIMIT and price is None:
            raise ValueError("Price is required for limit orders.")

        if client_order_id and len(client_order_id) > 36:
            raise ValueError("client_order_id length must be less than or equal to 36.")

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

        return Adapter.futures_order_create(raw_data)

    async def futures_order_cancel(
        self,
        symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> list[OrderIdDict]:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_order_cancel_all(self, symbol: str) -> list[OrderInfoDict]:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_order_info(
        self,
        symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> OrderInfoDict:
        raise NotImplementedError("Method will be implemented later.")
