__all__ = ["UniClient"]


import asyncio
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarginType, OrderSide, OrderType, Timeframe
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
from .exchange_info import ExchangeInfo


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Kucoin API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def _contract_sizes(self, symbol: str | None = None) -> dict[str, float]:
        """Размеры контрактов: из ExchangeInfo, а если он не загружен — запросом инструментов."""
        loaded = getattr(ExchangeInfo, "_futures_tickers_info", None) or {}
        if (symbol and symbol in loaded) or (not symbol and loaded):
            return {}
        raw_data = await self._client.symbol("FUTURES", symbol)
        return Adapter.contract_sizes(raw_data)

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
        raw_data, sizes = await asyncio.gather(
            self._client.kline(
                trade_type="FUTURES",
                symbol=symbol,
                interval=interval,
                start_at=self.to_seconds(start_time),
                end_at=self.to_seconds(end_time),
            ),
            self._contract_sizes(symbol),
        )
        return Adapter.klines(
            raw_data=raw_data,
            symbol=symbol,
            contract_size=Adapter._contract_size(symbol, sizes),
        )

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.funding_rate(symbol=symbol)
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_interval(self, symbol: str) -> int: ...

    @overload
    async def funding_interval(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_interval(self) -> dict[str, int]: ...

    async def funding_interval(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.funding_rate(symbol=symbol)
        adapted_data = Adapter.funding_interval(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_next_time(self, symbol: str) -> int: ...

    @overload
    async def funding_next_time(self, symbol: None) -> dict[str, int]: ...

    @overload
    async def funding_next_time(self) -> dict[str, int]: ...

    async def funding_next_time(self, symbol: str | None = None) -> dict[str, int] | int:
        raw_data = await self._client.funding_rate(symbol=symbol)
        adapted_data = Adapter.funding_next_time(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def funding_info(self, symbol: str) -> FundingInfoItem: ...

    @overload
    async def funding_info(self, symbol: None) -> FundingInfoDict: ...

    @overload
    async def funding_info(self) -> FundingInfoDict: ...

    async def funding_info(self, symbol: str | None = None) -> FundingInfoItem | FundingInfoDict:
        raw_data = await self._client.funding_rate(symbol=symbol)
        adapted_data = Adapter.funding_info(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data, sizes = await asyncio.gather(self._client.open_interest(), self._contract_sizes())
        adapted_data = Adapter.open_interest(raw_data, sizes)
        return adapted_data[symbol] if symbol else adapted_data

    async def long_short_ratio_history(
        self, symbol: str, period: Timeframe = Timeframe.MIN_5, limit: int = 30
    ) -> list[LongShortRatioItem]:
        raise NotImplementedError(
            "Method `long_short_ratio_history` cannot be implemented for Kucoin: "
            "public futures API has no long/short account ratio endpoint."
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
        raw_data, sizes = await asyncio.gather(
            self._client.ticker("FUTURES", symbol), self._contract_sizes(symbol)
        )
        adapted_data = Adapter.futures_best_bid_ask(raw_data, sizes)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        if not 1 <= limit <= 1000:
            raise ValueError(
                f"Invalid limit for kucoin futures depth: {limit}. Valid range: [1, 1000]"
            )
        raw_data, sizes = await asyncio.gather(
            self._client.orderbook(symbol=symbol, trade_type="FUTURES", limit=str(limit)),
            self._contract_sizes(symbol),
        )
        return Adapter.futures_depth(
            raw_data, symbol=symbol, contract_size=Adapter._contract_size(symbol, sizes)
        )

    async def futures_delistings(self) -> dict[str, int]:
        raw_data = await self._client.symbol("FUTURES")
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
