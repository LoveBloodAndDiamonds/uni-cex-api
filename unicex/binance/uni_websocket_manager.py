__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

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
    """Реализация менеджера асинхронных унифицированных вебсокетов для биржи Binance."""

    def __init__(
        self,
        client: Client | UniClient | None = None,
        logger: LoggerLike | None = None,
        **ws_kwargs: Any,
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (`Client | UniClient | None`): Клиент Binance или унифицированный клиент. Нужен для подключения к приватным топикам.
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
        """Создаёт вебсокет для получения свечей на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            timeframe (`Timeframe`): Временной интервал свечей (унифицированный).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE, MarketType.SPOT),
        )

    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения свечей на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            timeframe (`Timeframe`): Временной интервал свечей (унифицированный).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.futures_klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE, MarketType.FUTURES),
        )

    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения сделок на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения агрегированных сделок на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.aggtrades_message, callback)
        return self._websocket_manager.agg_trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения сделок на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки
                адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.futures_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )

    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения агрегированных сделок на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.aggtrades_message, callback)
        return self._websocket_manager.futures_agg_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )

    def liquidations(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим ликвидаций (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        return self._websocket_manager.liquidation_order(
            callback=self._make_wrapper(self._adapter.liquidations_message, callback),
            symbol=symbol,
            symbols=symbols,
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
        wrapper = self._make_wrapper(self._adapter.futures_best_bid_ask_message, callback)
        return self._websocket_manager.futures_symbol_book_ticker(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
        )

    def futures_partial_book_depth(
        self,
        callback: CallbackType,
        limit: int,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> Websocket:
        """Открывает поток частичного стакана глубиной limit с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            limit (`int`): Лимит лучших асков и бидов в одном сообщении.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            kwargs (`Any`): Дополнительные аргументы для базового метода создания вебсокета.
                Поддерживается:
                  - `update_speed` (`str | None`): Интервал обновления (`"100ms"` или `"500ms"`).
                    Если не передан, используется дефолтный интервал Binance — `250ms`.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        allowed_levels = {5, 10, 20}
        if limit not in allowed_levels:
            raise ValueError("Parameter `limit` must be one of: 5, 10, 20")

        allowed_kwargs = {"update_speed"}
        unknown_kwargs = set(kwargs) - allowed_kwargs
        if unknown_kwargs:
            allowed_kwargs_message = ", ".join(sorted(allowed_kwargs))
            unknown_kwargs_message = ", ".join(sorted(unknown_kwargs))
            raise ValueError(
                f"Unsupported kwargs: {unknown_kwargs_message}. "
                f"Allowed kwargs: {allowed_kwargs_message}"
            )

        update_speed: str | None = kwargs.get("update_speed")
        allowed_update_speeds = {None, "100ms", "500ms"}
        if update_speed not in allowed_update_speeds:
            raise ValueError("Parameter `update_speed` must be one of: '100ms', '500ms' or None")

        wrapper = self._make_wrapper(self._adapter.futures_partial_book_depth_message, callback)
        return self._websocket_manager.futures_partial_book_depth(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            levels=str(limit),
            update_speed=update_speed,
        )
