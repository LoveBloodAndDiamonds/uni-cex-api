__all__ = ["UniClient"]


from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarginType, MarketType, OrderSide, OrderType, Timeframe
from unicex.exceptions import ResponseError
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestItem,
    OrderIdDict,
    PositionInfoDict,
    TickerDailyDict,
)

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Binance API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.ticker_price()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_ticker_price()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.ticker_price()
        return Adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_ticker_price()
        return Adapter.last_price(raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_ticker_24hr()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore | raw_data is list[dict] if symbol param is not omitted

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
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
        raw_data = await self._client.futures_mark_price(symbol=symbol)
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

    async def open_interest(self, symbol: str = None) -> OpenInterestItem:  # type: ignore[reportArgumentType] | We should provide our exception message
        if not symbol:
            raise ValueError("Symbol is required for binance open interest")
        raw_data = await self._client.open_interest(symbol=symbol)
        return Adapter.open_interest(raw_data)

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
                f"Invalid limit for binance futures depth: {limit}. "
                f"Valid values: {sorted(valid_limits)}"
            )

        raw_data = await self._client.futures_depth(symbol=symbol, limit=limit)
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
    ) -> OrderIdDict:
        self.ensure_authorized()

        if type == OrderType.LIMIT and price is None:
            raise ValueError("Price is required for limit order type on Binance futures.")

        raw_data = await self._client.futures_order_create(
            symbol=symbol,
            side=side.to_exchange_format(Exchange.BINANCE),
            type=type.to_exchange_format(Exchange.BINANCE),
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
                margin_type=margin_type.to_exchange_format(Exchange.BINANCE),
            )
        except ResponseError as e:
            if e.code != -4046:
                raise e
