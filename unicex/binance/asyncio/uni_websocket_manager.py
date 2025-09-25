__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable
from typing import Any

from unicex._abc.asyncio import IUniWebsocketManager
from unicex._base.asyncio import Websocket
from unicex.enums import Exchange, Timeframe
from unicex.types import LoggerLike

from ..adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], Awaitable[None]]


class UniWebsocketManager(IUniWebsocketManager):
    """Унифицированный менеджер асинхронных вебсокетов Binance."""

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

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения свечей на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            timeframe (`Timeframe`): Временной интервал свечей (унифицированный).
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения свечей на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            timeframe (`Timeframe`): Временной интервал свечей (унифицированный).
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.futures_klines_message, callback)
        return self._websocket_manager.futures_klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def trades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Создаёт вебсокет для получения сделок на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def aggtrades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Создаёт вебсокет для получения агрегированных сделок на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.aggtrades_message, callback)
        return self._websocket_manager.agg_trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def futures_trades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Создаёт вебсокет для получения сделок на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки
                адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.futures_trades_message, callback)
        return self._websocket_manager.futures_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )

    def futures_aggtrades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Создаёт вебсокет для получения агрегированных сделок на фьючерсах с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обработки адаптированных сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`list[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        wrapper = self._make_wrapper(self._adapter.futures_aggtrades_message, callback)
        return self._websocket_manager.futures_agg_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )
