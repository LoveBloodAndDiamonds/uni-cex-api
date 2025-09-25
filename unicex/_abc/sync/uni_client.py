__all__ = ["IUniClient"]

from abc import ABC, abstractmethod
from functools import cached_property
from itertools import batched
from typing import Generic, Self, TypeVar, overload

import requests

from unicex._base import BaseClient
from unicex.enums import Timeframe
from unicex.types import KlineDict, LoggerLike, TickerDailyDict

from ..adapter import IAdapter

TClient = TypeVar("TClient", bound="BaseClient")


class IUniClient(ABC, Generic[TClient]):
    """Интерфейс для реализации синхронного унифицированного клиента."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        session: requests.Session | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (str | None): Ключ API для аутентификации.
            api_secret (str | None): Секретный ключ API для аутентификации.
            api_passphrase (`str | None`): Пароль API для аутентификации (Bitget).
            session (requests.Session): Сессия для выполнения HTTP-запросов.
            logger (LoggerLike | None): Логгер для вывода информации.
            max_retries (int): Максимальное количество повторных попыток запроса.
            retry_delay (int | float): Задержка между повторными попытками.
            proxies (list[str] | None): Список HTTP(S) прокси для циклического использования.
            timeout (int): Максимальное время ожидания ответа от сервера.
        """
        self._client: TClient = self._client_cls(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            session=session,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    @classmethod
    def from_client(cls, client: TClient) -> Self:
        """Создает UniClient из уже существующего Client.

        Принимает:
            client (`TClient`): Экземпляр Client.

        Возвращает:
            `Self`: Созданный экземпляр клиента.
        """
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
    def tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        pass

    def tickers_batched(
        self, only_usdt: bool = True, batch_size: int = 20
    ) -> list[tuple[str, ...]]:
        """Возвращает список тикеров в чанках.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.
            batch_size (`int`): Размер чанка.

        Возвращает:
            `list[list[str]]`: Список тикеров в чанках.
        """
        tickers = self.tickers(only_usdt=only_usdt)
        return list(batched(tickers, n=batch_size))

    @abstractmethod
    def futures_tickers(self, only_usdt: bool = True) -> list[str]:
        """Возвращает список тикеров.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        pass

    def futures_tickers_batched(
        self, only_usdt: bool = True, batch_size: int = 20
    ) -> list[tuple[str, ...]]:
        """Возвращает список тикеров в чанках.

        Параметры:
            only_usdt (`bool`): Если True, возвращает только тикеры в паре к USDT.
            batch_size (`int`): Размер чанка.

        Возвращает:
            `list[list[str]]`: Список тикеров в чанках.
        """
        tickers = self.futures_tickers(only_usdt=only_usdt)
        return list(batched(tickers, n=batch_size))

    @abstractmethod
    def last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        pass

    @abstractmethod
    def futures_last_price(self) -> dict[str, float]:
        """Возвращает последнюю цену для каждого тикера.

        Возвращает:
            `dict[str, float]`: Словарь с последними ценами для каждого тикера.
        """
        pass

    @abstractmethod
    def ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        pass

    @abstractmethod
    def futures_ticker_24h(self) -> dict[str, TickerDailyDict]:
        """Возвращает статистику за последние 24 часа для каждого тикера.

        Возвращает:
            `dict[str, TickerDailyDict]`: Словарь с статистикой за последние 24 часа для каждого тикера.
        """
        pass

    @abstractmethod
    def klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            interval (`Timeframe`): Таймфрейм свечей.
            limit (`int`): Количество свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        pass

    @abstractmethod
    def futures_klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[KlineDict]:
        """Возвращает список свечей.

        Параметры:
            symbol (`str`): Название тикера.
            interval (`Timeframe`): Таймфрейм свечей.
            limit (`int`): Количество свечей.
            start_time (`int`): Время начала периода в миллисекундах.
            end_time (`int`): Время окончания периода в миллисекундах.

        Возвращает:
            `list[KlineDict]`: Список свечей.
        """
        pass

    @abstractmethod
    def funding_rate(self) -> dict[str, float]:
        """Возвращает ставку финансирования для всех тикеров.

        Возвращает:
            `dict[str, float]`: Ставка финансирования для каждого тикера.
        """
        pass

    @overload
    def open_interest(self, symbol: str) -> float: ...

    @overload
    def open_interest(self, symbol: None) -> dict[str, float]: ...

    @abstractmethod
    def open_interest(self, symbol: str | None) -> float | dict[str, float]:
        """Возвращает объем открытого интереса для тикера или всех тикеров,
        если тикер не указан.

        Параметры:
            symbol (`str | None`): Название тикера (Опционально).

        Возвращает:
            `float`: Объем открытых позиций в монетах.
        """
        pass
