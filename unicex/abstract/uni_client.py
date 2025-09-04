__all__ = [
    "ISyncUniClient",
    "IAsyncUniClient",
]
import logging
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Generic, Self, TypeVar

import requests

from unicex.enums import Timeframe
from unicex.types import KlineDict, TickerDailyDict

from .adapter import IAdapter
from .client import BaseSyncClient

TClient = TypeVar("TClient", bound=BaseSyncClient)


class ISyncUniClient(Generic[TClient], ABC):  # noqa: UP046
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
        self._client: TClient = self.client_cls(
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
    def from_client(cls, client: TClient) -> Self:
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

    def __exit__(self, *_):
        """Выход из контекста."""
        self.close()

    @property
    @abstractmethod
    def client_cls(self) -> type[TClient]:
        """Возвращает класс клиента для конкретной биржи."""
        raise NotImplementedError()

    @cached_property
    @abstractmethod
    def adapter(self) -> IAdapter:
        """Возвращает реализацию адаптера под конкретную биржу."""
        raise NotImplementedError()

    @abstractmethod
    def tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raise NotImplementedError()

    @abstractmethod
    def futures_tickers(self, only_usdt: bool) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (bool): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raise NotImplementedError()

    @abstractmethod
    def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raise NotImplementedError()

    @abstractmethod
    def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            dict[str, float]: Словарь с последними ценами для каждого тикера.
        """
        raise NotImplementedError()

    @abstractmethod
    def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.

        Пример возвращаемого значения:
            ```python
            {
                "BTCUSDT": {
                    "p": 0.01,
                    "v": 1000000,
                    "c": 10000,
                },
                "ETHUSDT": {
                    "p": 0.02,
                    "v": 500000,
                    "c": 5000,
                },
            }
            ```
        """
        raise NotImplementedError()

    @abstractmethod
    def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь с статистикой за последние 24 часа для каждого тикера.

        Пример возвращаемого значения:
            ```python
            {
                "BTCUSDT": {
                    "p": 0.01,
                    "v": 1000000,
                    "c": 10000,
                },
                "ETHUSDT": {
                    "p": 0.02,
                    "v": 500000,
                    "c": 5000,
                },
            }
            ```
        """
        raise NotImplementedError()

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
        """
        raise NotImplementedError()

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
        """
        raise NotImplementedError()


class IAsyncUniClient:
    """Интерфейс для реализации асинхронного унифицированного клиента."""

    pass
