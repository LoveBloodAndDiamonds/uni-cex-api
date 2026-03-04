__all__ = ["UniClient"]

from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, OrderSide, OrderType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    OrderInfoDict,
    TickerDailyDict,
)

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Bitget API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.get_ticker_information()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.get_ticker_information()
        return Adapter.last_price(raw_data=raw_data)

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.last_price(raw_data=raw_data)

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.get_ticker_information()
        return Adapter.ticker_24hr(raw_data=raw_data)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        return Adapter.ticker_24hr(raw_data=raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = (
            interval.to_exchange_format(Exchange.BITGET, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.get_candlestick_data(
            symbol=symbol,
            granularity=interval,
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
        interval = (
            interval.to_exchange_format(Exchange.BITGET, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_get_candlestick_data(
            symbol=symbol,
            product_type="USDT-FUTURES",
            granularity=interval,
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
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
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
        raw_data = await self._client.futures_get_all_tickers("USDT-FUTURES")
        adapted_data = Adapter.futures_best_bid_ask(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        valid_limits = {1, 5, 15, 50, 100}
        if limit not in valid_limits:
            raise ValueError(
                f"Invalid limit for bitget futures depth: {limit}. "
                f"Valid values: {sorted(valid_limits)}"
            )

        raw_data = await self._client.futures_get_merge_depth(
            symbol=symbol,
            product_type="USDT-FUTURES",
            limit=str(limit),
        )
        return Adapter.futures_depth(raw_data=raw_data, symbol=symbol)

    async def futures_order_create(
        self,
        symbol: str,
        side: OrderSide,
        type: OrderType,
        quantity: str,
        price: str | None = None,
        client_order_id: str | None = None,
        reduce_only: bool | None = None,
    ) -> OrderInfoDict:
        raise NotImplementedError("Method will be implemented later.")

    async def futures_order_cancel(
        self,
        symbol: str,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> None:
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
