__all__ = ["IUniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any, overload

from unicex._abc.asyncio import IUniWebsocketManager
from unicex._base.asyncio import Websocket
from unicex.enums import Timeframe
from unicex.types import LoggerLike

from ..adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], Awaitable[None]]


class UniWebsocketManager(IUniWebsocketManager):
    """Реализация менеджера асинхронных унифицированных вебсокетов."""

    def __init__(
        self, client: Client | UniClient | None = None, logger: LoggerLike | None = None
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (`Client | UniClient | None`): Клиент Binance или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client)  # type: ignore
        self._adapter = Adapter()

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        raise NotImplementedError()

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError()

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trade(callback=wrapper, symbol=symbol, symbols=symbols)

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError()

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError()

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
        symbols: Sequence[str],
    ) -> Websocket: ...

    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError()
