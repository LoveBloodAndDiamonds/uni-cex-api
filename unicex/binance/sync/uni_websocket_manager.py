__all__ = ["UniWebsocketManager"]

from collections.abc import Callable
from typing import Any

from loguru import logger as _logger

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex.enums import Exchange, Timeframe
from unicex.types import LoggerLike

from ..adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], None]


class UniWebsocketManager(IUniWebsocketManager):
    """Синхронный унифицированный менеджер вебсокетов Binance."""

    def __init__(
        self, client: Client | UniClient | None = None, logger: LoggerLike | None = None
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (Client | UniClient | None): Клиент Binance или унифицированный клиент.
            logger (`LoggerLike | None`): Логгер для записи логов.
        """
        if isinstance(client, UniClient):
            client = client.client
        self._websocket_manager = WebsocketManager(client)
        self._adapter = Adapter()
        self._logger = logger or _logger

    def _make_wrapper(
        self, adapter_func: Callable[[dict], Any], callback: CallbackType
    ) -> CallbackType:
        """Создает обертку над callback, применяя адаптер к сырым сообщениям."""

        def _wrapper(raw_msg: dict) -> None:
            try:
                adapted = adapter_func(raw_msg)
            except Exception as e:  # noqa: BLE001
                self._logger.error(f"Failed to adapt message: {e}")
                return
            callback(adapted)

        return _wrapper

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Создаёт вебсокет для получения свечей на споте с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Функция обработки адаптированных сообщений.
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
            callback (`CallbackType`): Функция обработки адаптированных сообщений.
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
            callback (`CallbackType`): Функция обработки адаптированных сообщений.
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
            callback (`CallbackType`): Функция обработки адаптированных сообщений.
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
            callback (`CallbackType`): Функция обработки
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
            callback (`CallbackType`): Функция обработки адаптированных сообщений.
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
