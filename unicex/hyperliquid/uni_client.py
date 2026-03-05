__all__ = ["UniClient"]

from typing import Self, overload

import aiohttp

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, OrderSide, OrderType, Timeframe
from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    LoggerLike,
    OpenInterestDict,
    OpenInterestItem,
    OrderIdDict,
    PositionInfoDict,
    TickerDailyDict,
)
from unicex.utils import batched_list

from .adapter import Adapter
from .client import Client


class UniClient(IUniClient[Client]):
    """Унифицированный клиент для работы с Hyperliquid API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        private_key: str | bytes | None = None,
        wallet_address: str | None = None,
        vault_address: str | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            session (`aiohttp.ClientSession`): Сессия для выполнения HTTP‑запросов.
            private_key (`str | bytes | None`): Приватный ключ API для аутентификации (Hyperliquid).
            wallet_address (`str | None`): Адрес кошелька для аутентификации (Hyperliquid).
            vault_address (`str | None`): Адрес хранилища для аутентификации (Hyperliquid).
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера, сек.
        """
        self._client: Client = self._client_cls(
            private_key=private_key,
            wallet_address=wallet_address,
            vault_address=vault_address,
            session=session,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    @classmethod
    async def create(
        cls,
        private_key: str | bytes | None = None,
        wallet_address: str | None = None,
        vault_address: str | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        return cls(
            session=aiohttp.ClientSession(),
            private_key=private_key,
            wallet_address=wallet_address,
            vault_address=vault_address,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    @property
    def _client_cls(self) -> type[Client]:
        return Client

    async def tickers(self, resolve_symbols: bool = True) -> list[str]:
        raw_data = await self._client.spot_metadata()
        return Adapter.tickers(raw_data, resolve_symbols=resolve_symbols)

    async def tickers_batched(
        self, batch_size: int = 20, resolve_symbols: bool = True
    ) -> list[list[str]]:
        tickers = await self.tickers(resolve_symbols=resolve_symbols)
        return batched_list(tickers, batch_size)

    async def futures_tickers(self) -> list[str]:
        raw_data = await self._client.perp_metadata()
        return Adapter.futures_tickers(raw_data)

    async def futures_tickers_batched(self, batch_size: int = 20) -> list[list[str]]:
        tickers = await self.futures_tickers()
        return batched_list(tickers, batch_size)

    async def last_price(self, resolve_symbols: bool = True) -> dict[str, float]:
        raw_data = await self._client.all_mids()
        return Adapter.last_price(raw_data, resolve_symbols=resolve_symbols)

    async def futures_last_price(self) -> dict[str, float]:
        raw_data = await self._client.all_mids()
        return Adapter.futures_last_price(raw_data)

    async def ticker_24hr(self, resolve_symbols: bool = True) -> TickerDailyDict:
        raw_data = await self._client.spot_meta_and_asset_contexts()
        return Adapter.ticker_24hr(raw_data, resolve_symbols=resolve_symbols)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        raw_data = await self._client.perp_meta_and_asset_contexts()
        return Adapter.futures_ticker_24hr(raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        resolve_symbols: bool = True,
    ) -> list[KlineDict]:
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit or (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            start_time, end_time = self.limit_to_start_and_end_time(interval, limit)
        interval = (
            interval.to_exchange_format(Exchange.HYPERLIQUID)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.candle_snapshot(
            coin=symbol,
            interval=interval,
            start_time=start_time,  # type: ignore[reportArgumentType]
            end_time=end_time,  # type: ignore[reportArgumentType]
        )
        adapted_klines = Adapter.futures_klines(raw_data)
        return adapted_klines[-limit:] if limit else adapted_klines

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

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            start_time, end_time = self.limit_to_start_and_end_time(interval, limit)
        interval = (
            interval.to_exchange_format(Exchange.HYPERLIQUID, MarketType.FUTURES)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.candle_snapshot(
            coin=symbol,
            interval=interval,
            start_time=start_time,  # type: ignore[reportArgumentType]
            end_time=end_time,  # type: ignore[reportArgumentType]
        )
        adapted_klines = Adapter.futures_klines(raw_data)
        return adapted_klines[-limit:] if limit else adapted_klines

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        raw_data = await self._client.perp_meta_and_asset_contexts()
        adapted_data = Adapter.funding_rate(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    @overload
    async def open_interest(self, symbol: str) -> OpenInterestItem: ...

    @overload
    async def open_interest(self, symbol: None) -> OpenInterestDict: ...

    @overload
    async def open_interest(self) -> OpenInterestDict: ...

    async def open_interest(self, symbol: str | None = None) -> OpenInterestItem | OpenInterestDict:
        raw_data = await self._client.perp_meta_and_asset_contexts()
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data

    async def futures_best_bid_ask(
        self, symbol: str | None = None
    ) -> BestBidAskItem | BestBidAskDict:
        raise NotImplementedError(
            "Method `futures_best_bid_ask` cannot be implemented for Hyperliquid: "
            "no REST endpoint with best bid/ask and sizes."
        )

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
