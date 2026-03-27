__all__ = ["UniClient"]


import asyncio
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarginType, OrderSide, OrderType, Timeframe
from unicex.exceptions import NotSupported, ResponseError
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
    """Унифицированный клиент для работы с Aster API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raise NotSupported("Spot market data is not supported for Aster")

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_ticker_price()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[arg-type] | raw_data is list[dict] if symbol param is not omitted

    async def last_price(self) -> dict[str, float]:
        raise NotSupported("Spot market data is not supported for Aster")

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_ticker_price()
        return Adapter.last_price(raw_data)  # type: ignore[arg-type] | raw_data is list[dict] if symbol param is not omitted

    async def ticker_24hr(self) -> TickerDailyDict:
        raise NotSupported("Spot market data is not supported for Aster")

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore[arg-type] | raw_data is list[dict] if symbol param is not omitted

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        raise NotSupported("Spot market data is not supported for Aster")

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = (
            interval.to_exchange_format(Exchange.ASTER)
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
        raw_data = await self._client.futures_mark_price()
        adapted_data = Adapter.funding_rate(raw_data if isinstance(raw_data, list) else [raw_data])  # type: ignore[arg-type]
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_interval(self, symbol: str) -> int: ...

    @overload
    async def funding_interval(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_interval(self) -> dict[str, int]: ...

    async def funding_interval(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.futures_funding_info()
        adapted_data = Adapter.funding_interval(raw_data=raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_next_time(self, symbol: str) -> int: ...

    @overload
    async def funding_next_time(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_next_time(self) -> dict[str, int]: ...

    async def funding_next_time(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.futures_mark_price()
        adapted_data = Adapter.funding_next_time(
            raw_data if isinstance(raw_data, list) else [raw_data]
        )  # type: ignore[arg-type]
        return adapted_data[symbol] if symbol else adapted_data

    async def funding_info(self, symbol: str | None = None) -> FundingInfoItem | FundingInfoDict:
        # Два разных endpoint'а: mark_price — rate + next_time, funding_info — interval
        mark_data, funding_data = await asyncio.gather(
            self._client.futures_mark_price(),
            self._client.futures_funding_info(),
        )
        adapted_data = Adapter.funding_info(
            mark_data=mark_data if isinstance(mark_data, list) else [mark_data],  # type: ignore[arg-type]
            funding_data=funding_data,
        )
        return adapted_data[symbol] if symbol else adapted_data

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

    @overload
    async def futures_best_bid_ask(self, symbol: str) -> BestBidAskItem: ...

    @overload
    async def futures_best_bid_ask(self, symbol: None) -> BestBidAskDict: ...

    @overload
    async def futures_best_bid_ask(self) -> BestBidAskDict: ...

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        raw_data = await self._client.futures_ticker_book_ticker(symbol=symbol)
        adapted_data = Adapter.futures_best_bid_ask(
            raw_data if isinstance(raw_data, list) else [raw_data]
        )
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        valid_limits = {5, 10, 20, 50, 100, 500, 1000}
        if limit not in valid_limits:
            raise ValueError(
                f"Invalid limit for aster futures depth: {limit}. "
                f"Valid values: {sorted(valid_limits)}"
            )

        raw_data = await self._client.futures_depth(symbol=symbol, limit=limit)
        return Adapter.futures_depth(raw_data=raw_data, symbol=symbol)

    async def futures_delistings(self) -> dict[str, int]:
        exchange_info = await self._client.futures_exchange_info()
        return Adapter.futures_delistings(exchange_info)

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
            raise ValueError("Price is required for limit order type on Aster futures.")

        raw_data = await self._client.futures_order_create(
            symbol=symbol,
            side=side.to_exchange_format(Exchange.ASTER),  # type: ignore
            type=type.to_exchange_format(Exchange.ASTER),  # type: ignore
            quantity=quantity,
            price=price,
            new_client_order_id=client_order_id,
            reduce_only=reduce_only,
            time_in_force="GTC" if type == OrderType.LIMIT else None,
        )
        return Adapter.futures_order_create(raw_data)

    async def futures_position_info(self, symbol: str) -> PositionInfoDict:
        self.ensure_authorized()

        raw_data = await self._client.futures_position_info(symbol=symbol)
        return Adapter.futures_position_info(raw_data=raw_data, symbol=symbol)

    async def futures_set_leverage(self, symbol: str, leverage: int) -> None:
        self.ensure_authorized()

        await self._client.futures_leverage_change(symbol=symbol, leverage=leverage)

    async def futures_set_margin_type(self, symbol: str, margin_type: MarginType) -> None:
        self.ensure_authorized()

        try:
            await self._client.futures_margin_type_change(
                symbol=symbol,
                margin_type=margin_type.to_exchange_format(Exchange.ASTER),
            )
        except ResponseError as e:
            if e.code != -4046:
                raise e
