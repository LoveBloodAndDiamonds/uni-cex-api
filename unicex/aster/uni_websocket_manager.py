__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex.enums import Exchange, Timeframe
from unicex.exceptions import NotSupported
from unicex.types import LoggerLike

from .adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], Awaitable[None]]


class UniWebsocketManager(IUniWebsocketManager):
    """Реализация менеджера асинхронных унифицированных вебсокетов."""

    def __init__(
        self,
        client: Client | UniClient | None = None,
        logger: LoggerLike | None = None,
        **ws_kwargs: Any,
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (`Client | UniClient | None`): Клиент Aster или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
            ws_kwargs (`dict[str, Any]`): Дополнительные параметры инициализации, которые будут переданы WebsocketManager/Websocket.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client, **ws_kwargs)  # type: ignore
        self._adapter = Adapter()

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
        raise NotSupported("Spot market data is not supported for Aster")

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
        wrapper = self._make_wrapper(self._adapter.Klines_message, callback)
        return self._websocket_manager.futures_klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.ASTER),
        )

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
        raise NotSupported("Spot market data is not supported for Aster")

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
        raise NotSupported("Spot market data is not supported for Aster")

    def futures_trades(
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

        В Aster доступен только поток агрегированных сделок, поэтому `futures_aggtrades`
        будет использован автоматически.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        return self.futures_aggtrades(callback, symbol, symbols)  # type: ignore

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
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.futures_agg_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )

    def futures_best_bid_ask(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим лучших бидов и асков с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError("Method `futures_best_bid_ask` will be implemented later")

    def futures_partial_book_depth(
        self,
        callback: CallbackType,
        limit: int,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает поток частичного стакана глубиной limit с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            limit (`int`): Лимит лучших асков и бидов в одном сообщении.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        raise NotImplementedError("Method `futures_partial_book_depth` will be implemented later")
