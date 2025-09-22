__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable
from logging import getLogger
from typing import Any

from unicex._abc.asyncio import IUniWebsocketManager
from unicex._base.asyncio import Websocket
from unicex.enums import Exchange, Timeframe

from ..adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager


class UniWebsocketManager(IUniWebsocketManager):
    """Унифицированный менеджер вебсокетов для Binance."""

    def __init__(self, client: Client | UniClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов."""
        if isinstance(client, UniClient):
            self._client = client.client
        else:
            self._client = client
        self._socket_manager = WebsocketManager(self._client)
        self._adapter = Adapter()
        self._logger = getLogger(__name__)

    async def _adapter_wrapper(
        self, raw_msg: dict, adapter_func: Callable, callback: Callable[[Any], Awaitable[None]]
    ) -> None:
        """Функция обертка, в которую попадают сырые сообщения с вебсокета.
        Эти сообщения проходят через адаптер и отправляются в callback.

        Параметры:
            message (Any): Сырое сообщение с вебсокета.
            adapter_func (Callable): Функция адаптера, которая преобразует сырое сообщение в объект.
            callback (Callable): Функция, которая будет вызвана для каждого полученного сообщения.
        """
        try:
            adapted_msg = adapter_func(raw_msg)
        except Exception as e:
            self._logger.error(f"Failed to adapt message: {e}")
            return
        await callback(adapted_msg)

    def klines(
        self, callback: Callable[[Any], Awaitable[None]], symbol: str, timeframe: Timeframe
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения свечей.
        Все полученные сообщения будут преобразованы в объекты Kline и переданы в callback.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция, которая будет вызвана для каждого полученного сообщения.
            symbol (str): Символ, для которого нужно получить свечи.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.klines_message, callback)

        return self._socket_manager.klines(
            callback=_wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def futures_klines(
        self, callback: Callable[[Any], Awaitable[None]], symbol: str, timeframe: Timeframe
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения фьючерсов для получения свечей.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно получить свечи.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.futures_klines_message, callback)

        return self._socket_manager.futures_klines(
            callback=_wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def trades(self, callback: Callable[[Any], Awaitable[None]], symbol: str) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения сделок.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.trades_message, callback)

        return self._socket_manager.trade(
            callback=_wrapper,
            symbol=symbol,
        )

    def aggtrades(self, callback: Callable[[Any], Awaitable[None]], symbol: str) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения агрегированных сделок.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.aggtrades_message, callback)

        return self._socket_manager.agg_trade(
            callback=_wrapper,
            symbol=symbol,
        )

    def futures_trades(
        self, callback: Callable[[Any], Awaitable[None]], symbol: str
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения сделок.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.futures_trades_message, callback)

        return self._socket_manager.futures_trade(
            callback=_wrapper,
            symbol=symbol,
        )

    def futures_aggtrades(
        self, callback: Callable[[Any], Awaitable[None]], symbol: str
    ) -> Websocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения агрегированных сделок.

        Параметры:
            callback (Callable[[Any], Awaitable[None]]): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """

        async def _wrapper(raw_msg: dict) -> None:
            """Функция обертка, чтобы вызывать."""
            await self._adapter_wrapper(raw_msg, self._adapter.futures_aggtrades_message, callback)

        return self._socket_manager.futures_agg_trade(
            callback=_wrapper,
            symbol=symbol,
        )
