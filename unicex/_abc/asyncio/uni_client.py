__all__ = ["IUniClient"]

import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, Self, TypeVar, overload

import aiohttp

from unicex._base.asyncio import BaseClient
from unicex.enums import Timeframe
from unicex.types import KlineDict, TickerDailyDict

from ..adapter import IAdapter

TClient = TypeVar("TClient", bound="BaseClient")


class IUniClient(ABC, Generic[TClient]):
    """Интерфейс для реализации асинхронного унифицированного клиента."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str | None = None,
        api_secret: str | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (`str | None`): Ключ API для аутентификации.
            api_secret (`str | None`): Секретный ключ API для аутентификации.
            session (`aiohttp.ClientSession`): Сессия для выполнения HTTP-запросов.
            logger (`logging.Logger | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками.
            proxies (`list[str] | None`): Список HTTP(S) прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера.
        """
        self._client: TClient = self._client_cls(
            api_key=api_key,
            api_secret=api_secret,
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
        api_key: str | None = None,
        api_secret: str | None = None,
        session: aiohttp.ClientSession | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        """Создает инстанцию клиента.
        Создать клиент можно и через __init__, но в таком случае session: `aiohttp.ClientSession` - обязательный параметр.

        Параметры:
            api_key (`str | None`): Ключ API для аутентификации.
            api_secret (`str | None`): Секретный ключ API для аутентификации.
            session (`aiohttp.ClientSession | None`): Сессия для выполнения HTTP-запросов.
            logger (`logging.Logger | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками.
            proxies (`list[str] | None`): Список HTTP(S) прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера.

        Возвращает:
            `IUniClient`: Созданный экземпляр клиента.
        """
        return cls(
            session=session or aiohttp.ClientSession(),
            api_key=api_key,
            api_secret=api_secret,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    @classmethod
    def from_client(cls, client: TClient) -> Self:
        """Создает UniClient из уже существующего BinanceClient.

        Параметры:
            client (`TClient`): Экземпляр BinanceClient.

        Возвращает:
            `IUniClient`: Созданный экземпляр клиента.
        """
        instance = cls.__new__(cls)  # создаем пустой объект без вызова __init__
        instance._client = client
        return instance

    def is_authorized(self) -> bool:
        """Проверяет, наличие апи ключей в инстансе клиента.

        Возвращает:
            `bool`: True, если апи ключи присутствуют, иначе False.
        """
        return self._client._api_key is not None and self._client._api_secret is not None

    async def close(self) -> None:
        """Закрывает сессию клиента."""
        await self._client.close()

    async def __aenter__(self) -> Self:
        """Вход в асинхронный контекст."""
        return self

    async def __aexit__(self, *_) -> None:
        """Выход из асинхронного контекста."""
        await self.close()

    @property
    def client(self) -> TClient:
        """Возвращает клиент биржи.

        Возвращает:
            `TClient`: Клиент биржи.
        """
        return self._client

    @property
    @abstractmethod
    def _client_cls(self) -> type[TClient]:
        """Возвращает класс клиента для конкретной биржи.

        Возвращает:
            `type[TClient]`: Класс клиента.
        """
        pass

    @cached_property
    @abstractmethod
    def adapter(self) -> IAdapter:
        """Возвращает реализацию адаптера под конкретную биржу.

        Возвращает:
            `IAdapter`: Реализация адаптера.
        """
        pass

    @abstractmethod
    async def tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        pass

    @abstractmethod
    async def futures_tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        pass

    @abstractmethod
    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        pass

    @abstractmethod
    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        pass

    @abstractmethod
    async def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        pass

    @abstractmethod
    async def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        pass

    @abstractmethod
    async def klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            limit (`int`): Количество свечей.
            interval (`Timeframe`): Таймфрейм свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        pass

    @abstractmethod
    async def futures_klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            limit (`int`): Количество свечей.
            interval (`Timeframe`): Таймфрейм свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        pass

    @abstractmethod
    async def funding_rate(self, only_usdt: bool) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `dict[str, float]`: Ставка финансирования для каждого тикера.
        """
        pass

    @overload
    async def open_interest(self, symbol: str) -> float: ...

    @overload
    async def open_interest(self, symbol: None) -> dict[str, float]: ...

    @abstractmethod
    async def open_interest(self, symbol: str | None) -> float | dict[str, float]:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера (Опционально).

        Возвращает:
            `float`: Объем открытых позиций в монетах.
        """
        pass
