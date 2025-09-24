__all__ = ["IUniWebsocketManager"]

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, overload

from unicex._base import Websocket
from unicex.enums import Timeframe

type CallbackType = Callable[[Any], None]


class IUniWebsocketManager(ABC):
    """Интерфейс менеджера синхронных унифицированных вебсокетов."""

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

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
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        pass

    @overload
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

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
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

    @abstractmethod
    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

    @abstractmethod
    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @overload
    def futures_trades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_trades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

    @abstractmethod
    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass

    @overload
    def futures_aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: list[str],
    ) -> Websocket: ...

    @abstractmethod
    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        pass
