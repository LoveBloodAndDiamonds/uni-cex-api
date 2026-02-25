__all__ = ["IUniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

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
            client (`Client | UniClient | None`): Клиент Okx или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
            ws_kwargs (`dict[str, Any]`): Дополнительные параметры инициализации, которые будут переданы WebsocketManager/Websocket.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client, **ws_kwargs)  # type: ignore
        self._adapter = Adapter()

    def _is_service_message(self, raw_msg: Any) -> bool:
        """Дополнительно обрабатывает ошибку адаптации сообщения на случай, если это сервисное сообщение, например `ping` или `subscribe`.

        Переопределяется в каждом наследнике в связи с разным форматом входящих данных.
        """
        return raw_msg.get("event") == "subscribe"

    def _normalize_symbol(
        self,
        symbol: str | None,
        symbols: Sequence[str] | None,
    ) -> list[str]:
        """Преобразует параметры symbol/symbols в один тикер."""
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if symbol:
            return [symbol]
        if symbols:
            return list(symbols)
        raise ValueError("Either symbol or symbols must be provided")

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.candlesticks(
            callback=wrapper,
            interval=timeframe.to_exchange_format(Exchange.OKX),  # type: ignore
            inst_id=inst_id,
        )

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.candlesticks(
            callback=wrapper,
            interval=timeframe.to_exchange_format(Exchange.OKX),  # type: ignore
            inst_id=inst_id,
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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.all_trades(callback=wrapper, inst_id=inst_id)

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trades(callback=wrapper, inst_id=inst_id)

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.all_trades(callback=wrapper, inst_id=inst_id)

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trades(callback=wrapper, inst_id=inst_id)

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
        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.futures_best_bid_ask_message, callback)
        return self._websocket_manager.order_book(
            callback=wrapper,
            channel="bbo-tbt",
            inst_id=inst_id,
        )

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
        channel_by_limit = {
            1: "bbo-tbt",
            5: "books5",
            50: "books50-l2-tbt",
            400: "books-l2-tbt",
        }
        if limit not in channel_by_limit:
            raise ValueError("Parameter `limit` must be one of: 1, 5, 50, 400")

        inst_id = self._normalize_symbol(symbol, symbols)
        wrapper = self._make_wrapper(self._adapter.futures_partial_book_depth_message, callback)
        return self._websocket_manager.order_book(
            callback=wrapper,
            channel=channel_by_limit[limit],  # type: ignore[arg-type]
            inst_id=inst_id,
        )
