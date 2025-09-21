from collections.abc import Callable
from logging import getLogger

from unicex.abc import IUniWebsocketManager
from unicex.base import BaseWebsocket
from unicex.enums import Exchange, Timeframe

from .adapter import BinanceAdapter
from .client import BinanceClient
from .uni_client import UniBinanceClient
from .websocket_manager import BinanceWebsocketManager


class UniBinanceWebsocketManager(IUniWebsocketManager):
    """Унифицированный менеджер вебсокетов для Binance."""

    def __init__(self, client: BinanceClient | UniBinanceClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов."""
        if isinstance(client, UniBinanceClient):
            self._client = client.client
        else:
            self._client = client
        self._socket_manager = BinanceWebsocketManager(self._client)
        self._adapter = BinanceAdapter()
        self._logger = getLogger(__name__)

    def _wrapper(self, raw_msg: dict, adapter_func: Callable, callback: Callable) -> None:
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
        callback(adapted_msg)

    def klines(self, callback: Callable, symbol: str, timeframe: Timeframe) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения свечей.
        Все полученные сообщения будут преобразованы в объекты Kline и переданы в callback.

        Параметры:
            callback (Callable): Функция, которая будет вызвана для каждого полученного сообщения.
            symbol (str): Символ, для которого нужно получить свечи.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.klines(
            callback=lambda raw_msg: self._wrapper(raw_msg, self._adapter.klines_message, callback),
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def futures_klines(
        self, callback: Callable, symbol: str, timeframe: Timeframe
    ) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения фьючерсов для получения свечей.

        Параметры:
            callback (Callable): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно получить свечи.
            timeframe (Timeframe): Временной интервал свечей.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.futures_klines(
            callback=lambda raw_msg: self._wrapper(
                raw_msg, self._adapter.futures_klines_message, callback
            ),
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def trades(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения сделок.

        Параметры:
            callback (Callable): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.trade(
            callback=lambda raw_msg: self._wrapper(raw_msg, self._adapter.trades_message, callback),
            symbol=symbol,
        )

    def aggtrades(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения агрегированных сделок.

        Параметры:
            callback (Callable): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.agg_trade(
            callback=lambda raw_msg: self._wrapper(
                raw_msg, self._adapter.aggtrades_message, callback
            ),
            symbol=symbol,
        )

    def futures_trades(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения сделок.

        Параметры:
            callback (Callable): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.futures_trade(
            callback=lambda raw_msg: self._wrapper(
                raw_msg, self._adapter.futures_trades_message, callback
            ),
            symbol=symbol,
        )

    def futures_aggtrades(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения агрегированных сделок.

        Параметры:
            callback (Callable): Функция обратного вызова, которая будет вызвана при получении данных.
            symbol (str): Символ, для которого нужно открыть вебсокет соединение.

        Возвращает:
            BaseWebsocket: Объект вебсокета, который можно использовать для управления соединением.
        """
        return self._socket_manager.futures_agg_trade(
            callback=lambda raw_msg: self._wrapper(
                raw_msg, self._adapter.futures_aggtrades_message, callback
            ),
            symbol=symbol,
        )
