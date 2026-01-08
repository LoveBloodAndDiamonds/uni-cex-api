__all__ = ["IUniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any, overload

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex.enums import Exchange, MarketType, Timeframe
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
            client (`Client | UniClient | None`): Клиент Gateio или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
            ws_kwargs (`dict[str, Any]`): Дополнительные параметры инициализации, которые будут переданы WebsocketManager/Websocket.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client, **ws_kwargs)  # type: ignore
        self._adapter = Adapter()

    def _normalize_symbols(
        self,
        symbol: str | None,
        symbols: Sequence[str] | None,
    ) -> list[str]:
        """Преобразует параметры symbol/symbols в список тикеров."""
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if symbol:
            return [symbol]
        if symbols:
            return list(symbols)
        raise ValueError("Either symbol or symbols must be provided")

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
        tickers = self._normalize_symbols(symbol, symbols)

        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.candlesticks(
            callback=wrapper,
            interval=timeframe.to_exchange_format(Exchange.GATE, MarketType.SPOT),
            symbols=tickers,
        )

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
        tickers = self._normalize_symbols(symbol, symbols)

        wrapper = self._make_wrapper(self._adapter.futures_klines_message, callback)
        return self._websocket_manager.futures_candlesticks(
            callback=wrapper,
            interval=timeframe.to_exchange_format(Exchange.GATE, MarketType.FUTURES),
            symbols=tickers,
        )

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
        tickers = self._normalize_symbols(symbol, symbols)

        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trades(callback=wrapper, symbols=tickers)

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
        return self.trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore[reportCallIssue]

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
        tickers = self._normalize_symbols(symbol, symbols)

        wrapper = self._make_wrapper(self._adapter.futures_trades_message, callback)
        return self._websocket_manager.futures_trades(callback=wrapper, symbols=tickers)

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
        return self.futures_trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore[reportCallIssue]
