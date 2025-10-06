__all__ = ["UniClient"]

import time
from typing import Self, overload

import aiohttp

from unicex._abc import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from unicex.types import KlineDict, LoggerLike, OpenInterestDict, OpenInterestItem, TickerDailyDict
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
        """Создает инстанцию клиента.
        Создать клиент можно и через __init__, но в таком случае session: `aiohttp.ClientSession` - обязательный параметр.

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

        Возвращает:
            `IUniClient`: Созданный экземпляр клиента.
        """
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
        """Возвращает класс клиента для Hyperliquid.

        Возвращает:
            type[Client]: Класс клиента для Hyperliquid.
        """
        return Client

    async def tickers(self, resolve_symbols: bool = False) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.spot_metadata()
        return Adapter.tickers(raw_data, resolve_symbols)

    async def tickers_batched(
        self, resolve_symbols: bool = False, batch_size: int = 20
    ) -> list[list[str]]:
        """Возвращает список тикеров в чанках.

        Параметры:
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".
            batch_size (`int`): Размер чанка.

        Возвращает:
            `list[list[str]]`: Список тикеров в чанках.
        """
        tickers = await self.tickers(resolve_symbols)
        return batched_list(tickers, batch_size)

    async def futures_tickers(self) -> list[str]:
        """Возвращает список тикеров.

        Возвращает:
            list[str]: Список тикеров.
        """
        raw_data = await self._client.perp_metadata()
        return Adapter.futures_tickers(raw_data)

    async def futures_tickers_batched(self, batch_size: int = 20) -> list[list[str]]:
        """Возвращает список тикеров в чанках.

        Параметры:
            batch_size (`int`): Размер чанка.

        Возвращает:
            `list[list[str]]`: Список тикеров в чанках.
        """
        tickers = await self.futures_tickers()
        return batched_list(tickers, batch_size)

    async def last_price(self, resolve_symbols: bool = False) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Параметры:
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.all_mids()
        return Adapter.last_price(raw_data, resolve_symbols)

    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raw_data = await self._client.all_mids()
        return Adapter.futures_last_price(raw_data)

    async def ticker_24hr(self, resolve_symbols: bool = False) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Параметры:
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.spot_meta_and_asset_contexts()
        return Adapter.ticker_24hr(raw_data, resolve_symbols)

    async def futures_ticker_24hr(self) -> TickerDailyDict:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            TickerDailyDict: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        raw_data = await self._client.perp_meta_and_asset_contexts()
        return Adapter.futures_ticker_24hr(raw_data)

    async def klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        resolve_symbols: bool = False,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера. Например "@1".
            limit (int | None): Количество свечей.
            interval (Timeframe | str): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.
            resolve_symbols (bool): Если True, тикер маппится из вида "@123" в "BTC".

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit and (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            end_time = int(time.time() * 1000)
            start_time = end_time - (limit * interval.to_seconds * 1000)  # type: ignore[reportOptionalOperand]
        interval = (
            interval.to_exchange_format(Exchange.HYPERLIQUID, MarketType.SPOT)
            if isinstance(interval, Timeframe)
            else interval
        )
        raw_data = await self._client.candle_snapshot(
            coin=symbol,
            interval=interval,
            start_time=start_time,  # type: ignore[reportArgumentType]
            end_time=end_time,  # type: ignore[reportArgumentType]
        )
        return Adapter.klines(raw_data=raw_data, resolve_symbols=resolve_symbols)

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe | str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей для тикера.

        Параметры:
            symbol (str): Название тикера. Например "BTC".
            limit (int | None): Количество свечей.
            interval (Timeframe | str): Таймфрейм свечей.
            start_time (int | None): Время начала периода в миллисекундах.
            end_time (int | None): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей для тикера.
        """
        if not limit and not all([start_time, end_time]):
            raise ValueError("limit and (start_time and end_time) must be provided")

        if limit:  # Перезаписываем start_time и end_time если указан limit, т.к. по умолчанию HyperLiquid не принимают этот параметр
            if not isinstance(interval, Timeframe):
                raise ValueError("interval must be a Timeframe if limit param provided")
            end_time = int(time.time() * 1000)
            start_time = end_time - (limit * interval.to_seconds * 1000)  # type: ignore[reportOptionalOperand]
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
        return Adapter.futures_klines(raw_data)

    @overload
    async def funding_rate(self, symbol: str) -> float: ...

    @overload
    async def funding_rate(self, symbol: None) -> dict[str, float]: ...

    @overload
    async def funding_rate(self) -> dict[str, float]: ...

    async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
        """Возвращает ставку финансирования для тикера или всех тикеров, если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера (Опционально).

        Возвращает:
            `dict[str, float] | float`: Ставка финансирования для тикера или словарь со ставками для всех тикеров.
        """
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
        """Возвращает объем открытого интереса для тикера или всех тикеров, если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера. (Опционально, но обязателен для следующих бирж: BINANCE).

        Возвращает:
            `OpenInterestItem | OpenInterestDict`: Если тикер передан - словарь со временем и объемом
                открытого интереса в монетах. Если нет передан - то словарь, в котором ключ - тикер,
                а значение - словарь с временем и объемом открытого интереса в монетах.
        """
        raw_data = await self._client.perp_meta_and_asset_contexts()
        adapted_data = Adapter.open_interest(raw_data)
        return adapted_data[symbol] if symbol else adapted_data
