__all__ = ["IUniWebsocketManager"]

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

from unicex._base.asyncio import Websocket
from unicex.enums import Timeframe

type CallbackType = Callable[[Any], Awaitable[None]]


class IUniWebsocketManager(ABC):
    """Интерфейс менеджера асинхронных унифицированных вебсокетов."""

    @abstractmethod
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (spot) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.
                Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        pass

    @abstractmethod
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (futures) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.
                Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @abstractmethod
    def trades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Открывает стрим сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @abstractmethod
    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @abstractmethod
    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Открывает стрим сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @abstractmethod
    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None,
        symbols: list[str] | None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`Callable[[Any], Awaitable[None]]`): Асинхронная функция обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass
