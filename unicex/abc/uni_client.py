__all__ = [
    "IUniClient",
    "IUniAioClient",
]
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, Self, TypeVar, overload

import aiohttp
import requests

from unicex.base import BaseAioClient, BaseClient
from unicex.enums import Timeframe
from unicex.types import KlineDict, TickerDailyDict

from .adapter import IAdapter

Client = TypeVar("Client", bound=BaseClient)
AioClient = TypeVar("AioClient", bound=BaseAioClient)


class IUniClient(Generic[Client], ABC):  # noqa: UP046
    """Интерфейс для реализации синхронного унифицированного клиента."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        session: requests.Session | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (str | None): Ключ API для аутентификации.
            api_secret (str | None): Секретный ключ API для аутентификации.
            session (requests.Session): Сессия для выполнения HTTP-запросов.
            logger (logging.Logger | None): Логгер для вывода информации.
            max_retries (int): Максимальное количество повторных попыток запроса.
            retry_delay (int | float): Задержка между повторными попытками.
            proxies (list[str] | None): Список HTTP(S) прокси для циклического использования.
            timeout (int): Максимальное время ожидания ответа от сервера.
        """
        self._client: Client = self.client_cls(
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
    def from_client(cls, client: Client) -> Self:
        """Создает UniClient из уже существующего BinanceClient."""
        instance = cls.__new__(cls)  # создаем пустой объект без вызова __init__
        instance._client = client
        return instance

    def close(self) -> None:
        """Закрывает сессию клиента."""
        self._client.close()

    def __enter__(self) -> Self:
        """Вход в контекст."""
        return self

    def __exit__(self, *_) -> None:
        """Выход из контекста."""
        self.close()

    @property
    def client(self) -> Client:
        """Возвращает клиент биржи.

        Возвращает:
            TClient: Клиент биржи.
        """
        return self._client

    @property
    @abstractmethod
    def client_cls(self) -> type[Client]:
        """Возвращает класс клиента для конкретной биржи.

        Возвращает:
            type[TClient]: Класс клиента.
        """

    @cached_property
    @abstractmethod
    def adapter(self) -> IAdapter:
        """Возвращает реализацию адаптера под конкретную биржу.

        Возвращает:
            IAdapter: Реализация адаптера.
        """

    @abstractmethod
    def tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @abstractmethod
    def futures_tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @abstractmethod
    def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """

    @abstractmethod
    def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """

    @abstractmethod
    def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """

    @abstractmethod
    def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """

    @abstractmethod
    def klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (str): Название тикера.
            limit (int): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int): Время начала периода в миллисекундах.
            end_time (int): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей.
        """

    @abstractmethod
    def futures_klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (str): Название тикера.
            limit (int): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int): Время начала периода в миллисекундах.
            end_time (int): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей.
        """

    @abstractmethod
    def funding_rate(self, only_usdt: bool) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера в %.
        """

    @overload
    def open_interest(self, symbol: str) -> float: ...

    @overload
    def open_interest(self, symbol: None) -> dict[str, float]: ...

    @abstractmethod
    def open_interest(self, symbol: str | None) -> float | dict[str, float]:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (str | None): Название тикера (Опционально).

        Возвращает:
            float: Объем открытых позиций в монетах.
        """


class IUniAioClient(Generic[AioClient], ABC):  # noqa: UP046
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
            api_key (str | None): Ключ API для аутентификации.
            api_secret (str | None): Секретный ключ API для аутентификации.
            session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
            logger (logging.Logger | None): Логгер для вывода информации.
            max_retries (int): Максимальное количество повторных попыток запроса.
            retry_delay (int | float): Задержка между повторными попытками.
            proxies (list[str] | None): Список HTTP(S) прокси для циклического использования.
            timeout (int): Максимальное время ожидания ответа от сервера.
        """
        self._client: AioClient = self.client_cls(
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

        Возвращает:
            BaseAsyncClient: Созданный экземпляр клиента.
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
    def from_client(cls, client: AioClient) -> Self:
        """Создает UniClient из уже существующего BinanceClient."""
        instance = cls.__new__(cls)  # создаем пустой объект без вызова __init__
        instance._client = client
        return instance

    def is_authorized(self) -> bool:
        """Проверяет, наличие апи ключей в инстансе клиента."""
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
    def client(self) -> AioClient:
        """Возвращает клиент биржи.

        Возвращает:
            AClient: Клиент биржи.
        """
        return self._client

    @property
    @abstractmethod
    def client_cls(self) -> type[AioClient]:
        """Возвращает класс клиента для конкретной биржи.

        Возвращает:
            type[AClient]: Класс клиента.
        """

    @cached_property
    @abstractmethod
    def adapter(self) -> IAdapter:
        """Возвращает реализацию адаптера под конкретную биржу.

        Возвращает:
            IAdapter: Реализация адаптера.
        """

    @abstractmethod
    async def tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @abstractmethod
    async def futures_tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @abstractmethod
    async def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """

    @abstractmethod
    async def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """

    @abstractmethod
    async def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """

    @abstractmethod
    async def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.
        """

    @abstractmethod
    async def klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (str): Название тикера.
            limit (int): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int): Время начала периода в миллисекундах.
            end_time (int): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей.
        """

    @abstractmethod
    async def futures_klines(
        self, symbol: str, limit: int, interval: Timeframe, start_time: int, end_time: int
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (str): Название тикера.
            limit (int): Количество свечей.
            interval (Timeframe): Таймфрейм свечей.
            start_time (int): Время начала периода в миллисекундах.
            end_time (int): Время окончания периода в миллисекундах.

        Возвращает:
            list[KlineDict]: Список свечей.
        """

    @abstractmethod
    async def funding_rate(self, only_usdt: bool) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            dict[str, float]: Ставка финансирования для каждого тикера.
        """

    @overload
    async def open_interest(self, symbol: str) -> float: ...

    @overload
    async def open_interest(self, symbol: None) -> dict[str, float]: ...

    @abstractmethod
    async def open_interest(self, symbol: str | None) -> float | dict[str, float]:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (str | None): Название тикера (Опционально).

        Возвращает:
            float: Объем открытых позиций в монетах.
        """
