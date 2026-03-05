__all__ = ["UniClient"]


from decimal import Decimal
from typing import overload

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, OrderSide, OrderType, Timeframe
from unicex.exceptions import ResponseError
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
    """Унифицированный клиент для работы с Gateio API."""

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.tickers()
        return Adapter.tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        raw_data = await self._client.futures_tickers(settle="usdt")
        return Adapter.futures_tickers(raw_data=raw_data, only_usdt=only_usdt)  # type: ignore[reportArgumentType]

    async def last_price(self) -> dict[str, float]:
        raw_data = await self._client.tickers()
        return Adapter.last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.futures_tickers(settle="usdt")
        return Adapter.futures_last_price(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.tickers()
        return Adapter.ticker_24hr(raw_data=raw_data)  # type: ignore[reportArgumentType]

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.futures_tickers(settle="usdt")
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
            interval.to_exchange_format(Exchange.GATE, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.candlesticks(
            currency_pair=symbol,
            interval=interval,
            limit=limit,
            from_time=self._to_seconds(start_time),
            to_time=self._to_seconds(end_time),
        )
        return Adapter.klines(raw_data=raw_data, symbol=symbol)  # type: ignore[reportArgumentType]

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        interval = (
            interval.to_exchange_format(Exchange.GATE, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.futures_candlesticks(
            settle="usdt",
            contract=symbol,
            interval=interval,
            limit=limit,
            from_time=self._to_seconds(start_time),
            to_time=self._to_seconds(end_time),
        )
        return Adapter.futures_klines(raw_data=raw_data, symbol=symbol)  # type: ignore[reportArgumentType]

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.futures_tickers(settle="usdt", contract=symbol)
        items = raw_data if isinstance(raw_data, list) else [raw_data]
        adapted_data = Adapter.funding_rate(raw_data=items)  # type: ignore[reportArgumentType]
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.futures_tickers(settle="usdt", contract=symbol)
        items = raw_data if isinstance(raw_data, list) else [raw_data]
        adapted_data = Adapter.open_interest(raw_data=items)  # type: ignore[reportArgumentType]
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
        raw_data = await self._client.futures_tickers(settle="usdt", contract=symbol)
        adapted_data = Adapter.futures_best_bid_ask(raw_data=raw_data)  # type: ignore[reportArgumentType]
        return adapted_data[symbol] if symbol else adapted_data

    @staticmethod
    def _to_seconds(value: int | None) -> int | None:
        if value is None:
            return None
        if value >= 1_000_000_000_000:
            return value // 1000
        return value

    async def futures_depth(
        self,
        symbol: str,
        limit: int,
    ) -> BookDepthDict:
        raw_data = await self._client.futures_order_book(
            settle="usdt",
            contract=symbol,
            limit=limit,
            with_id="true",  # type: ignore
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
    ) -> OrderIdDict:
        self.ensure_authorized()

        if type == OrderType.LIMIT and price is None:
            raise ValueError("Price is required for limit order type on Gate futures.")

        if type not in {OrderType.LIMIT, OrderType.MARKET}:
            raise ValueError(f"Unsupported order type for Gate futures: {type}.")

        contract_size = Adapter._get_contract_size(symbol)
        contracts = Decimal(quantity) / Decimal(str(contract_size))
        signed_size = contracts if side == OrderSide.BUY else -contracts
        size = self._format_decimal(signed_size)

        text = None
        if client_order_id:
            text = client_order_id if client_order_id.startswith("t-") else f"t-{client_order_id}"

        order_data = {
            "contract": symbol,
            "size": size,
            "price": "0" if type == OrderType.MARKET else price,
            "tif": "ioc" if type == OrderType.MARKET else "gtc",
            "text": text,
            "reduce_only": reduce_only,
        }
        raw_data = await self._client.futures_create_order(
            settle="usdt",
            order=order_data,
        )
        return Adapter.futures_order_create(raw_data)

    async def futures_position_info(self, symbol: str) -> PositionInfoDict:
        self.ensure_authorized()

        try:
            raw_data = await self._client.futures_position(
                settle="usdt",
                contract=symbol,
            )
        except ResponseError as e:
            if e.response_json.get("label") == "POSITION_NOT_FOUND":
                raw_data = {}
            else:
                raise
        return Adapter.futures_position_info(raw_data)

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        """Преобразует Decimal в строку без экспоненты и лишних нулей."""
        normalized = format(value, "f")
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        return normalized or "0"
