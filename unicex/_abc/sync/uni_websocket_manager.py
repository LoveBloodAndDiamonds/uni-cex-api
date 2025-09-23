__all__ = ["IUniWebsocketManager"]

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from unicex._base import Websocket
from unicex.enums import Timeframe

type CallbackType = Callable[[Any], None]


class IUniWebsocketManager(ABC):
    """Интерфейс для реализации менеджера асинхронных вебсокетов."""

    @abstractmethod
    def klines(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
        timeframe: Timeframe,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения свечей.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция, вызываемая для каждого сообщения.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            Websocket: Объект вебсокета для управления соединением.
        """
        pass

    @abstractmethod
    def futures_klines(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
        timeframe: Timeframe,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения фьючерсов для получения свечей.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            Websocket: Объект вебсокета.
        """
        pass

    @abstractmethod
    def trades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения сделок.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.

        Возвращает:
            Websocket: Объект вебсокета.
        """
        pass

    @abstractmethod
    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения агрегированных сделок.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.

        Возвращает:
            Websocket: Объект вебсокета.
        """
        pass

    @abstractmethod
    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения фьючерсов для получения сделок.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.

        Возвращает:
            Websocket: Объект вебсокета.
        """
        pass

    @abstractmethod
    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения фьючерсов для получения агрегированных сделок.

        Должен быть передан либо один символ (``symbol``), либо список символов (``symbols``).

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Асинхронная функция обратного вызова.
            symbol (str | None): Символ, для которого нужно открыть соединение.
            symbols (list[str] | None): Список символов, для которых нужно открыть соединение.

        Возвращает:
            Websocket: Объект вебсокета.
        """
        pass
