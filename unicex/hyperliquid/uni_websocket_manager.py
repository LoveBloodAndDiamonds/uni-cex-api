__all__ = ["IUniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any, overload

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex.enums import Exchange, Timeframe
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
            client (`Client | UniClient | None`): Клиент Hyperliquid или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
            ws_kwargs (`dict[str, Any]`): Дополнительные параметры инициализации, которые будут переданы WebsocketManager/Websocket.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client, **ws_kwargs)  # type: ignore
        self._adapter = Adapter()

    def _is_service_message(self, raw_msg: Any) -> bool:
        """Проверяет, является ли сообщение служебным."""
        return raw_msg.get("channel") in {"subscriptionResponse", "pong"}

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: str,
        symbols: None = None,
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: None = None,
        symbols: Sequence[str],
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        resolve_symbols: bool = True,
    ) -> Websocket:
        """Открывает стрим свечей (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            resolve_symbols (`bool`): Если True, преобразует символы из вида `@123` в обычный тикер.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(
            lambda raw_msg: self._adapter.klines_message(
                raw_msg=raw_msg,
                resolve_symbols=resolve_symbols,
            ),
            callback,
        )
        return self._websocket_manager.candle(
            callback=wrapper,
            interval=timeframe.to_exchange_format(Exchange.HYPERLIQUID),  # type: ignore
            coin=symbol,
            coins=list(symbols) if symbols else None,
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
        return self.klines(
            callback=callback,
            timeframe=timeframe,
            symbol=symbol,  # type: ignore
            symbols=symbols,  # type: ignore
            resolve_symbols=False,
        )

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        resolve_symbols: bool = True,
    ) -> Websocket:
        """Открывает стрим сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            resolve_symbols (`bool`): Если True, преобразует символы из вида `@123` в обычный тикер.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        wrapper = self._make_wrapper(
            lambda raw_msg: self._adapter.trades_message(
                raw_msg=raw_msg,
                resolve_symbols=resolve_symbols,
            ),
            callback,
        )
        return self._websocket_manager.trades(
            callback=wrapper,
            coin=symbol,
            coins=list(symbols) if symbols else None,
        )

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
        resolve_symbols: bool = True,
    ) -> Websocket: ...

    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        resolve_symbols: bool = True,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            resolve_symbols (`bool`): Если True, преобразует символы из вида `@123` в обычный тикер.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        return self.trades(
            callback=callback,
            symbol=symbol,  # type: ignore
            symbols=symbols,  # type: ignore
            resolve_symbols=resolve_symbols,
        )

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
        return self.trades(
            callback=callback,
            symbol=symbol,  # type: ignore
            symbols=symbols,  # type: ignore
            resolve_symbols=False,
        )

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
        return self.futures_trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore
