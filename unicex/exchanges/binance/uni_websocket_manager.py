from collections.abc import Callable
from logging import getLogger

from unicex.abc import IUniWebsocketManager
from unicex.base import BaseSyncWebsocket
from unicex.enums import Exchange, Timeframe

from .adapter import BinanceAdapter
from .client import BinanceClient
from .uni_client import UniBinanceClient
from .websocket_manager import BinanceWebsocketManager


class UniBinanceWebsocketManager(IUniWebsocketManager):
    """Унифицированный менеджер вебсокетов для Binance."""

    def __init__(self, client: BinanceClient | UniBinanceClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов."""  # todo
        if isinstance(client, UniBinanceClient):
            self._client = client.client
        else:
            self._client = client
        self._socket_manager = BinanceWebsocketManager(self._client)
        self._adapter = BinanceAdapter()
        self._logger = getLogger(__name__)

    def klines(self, callback: Callable, symbol: str, timeframe: Timeframe) -> BaseSyncWebsocket:
        """Унифицированный интерфейс для открытия вебсокет соединения для получения свечей.
        Все полученные сообщения будут преобразованы в объекты Kline и переданы в callback.

        Параметры:
            callback (Callable): Функция, которая будет вызвана для каждого полученного сообщения.
            symbol (str): Символ, для которого нужно получить свечи.
            timeframe (Timeframe): Временной интервал свечей.
        """

        def wrapper(raw_msg: dict) -> None:
            """Функция обертка, которая получает сырое сообщение, унифицирует его через адаптер
            и передает пользователю.
            """
            try:
                klines = self._adapter.klines_message(raw_msg)
            except Exception as e:
                self._logger.error(e)
            callback(klines)

        return self._socket_manager.klines(
            callback=wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def futures_klines(
        self, callback: Callable, symbol: str, timeframe: Timeframe
    ) -> BaseSyncWebsocket:
        """"""  # todo

        def wrapper(raw_msg: dict) -> None:
            """"""  # todo
            klines = self._adapter.futures_klines_message(raw_msg)
            callback(klines)

        return self._socket_manager.futures_klines(
            callback=wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )
