from collections.abc import Callable

from unicex.base import BaseSyncClient, BaseSyncWebsocket

from .types import StreamType


class BinanceWebsocketManager:
    """Менеджер вебсокетов для Binance."""

    # _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    _BASE_SPOT_URL: str = "wss://stream.binance.com:443"
    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    _TESTNET_FUTURES_URL: str = "wss://testnet.binancefuture.com/ws-fapi/v1"

    def __init__(self, client: BaseSyncClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (BaseSyncClient | None): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
        """
        self.client = client

    @classmethod
    def set_base_spot_url(cls, url: str = "wss://stream.binance.com:443") -> None:
        """Устанавливает базовый URL для вебсокетов Binance Spot."""
        cls._BASE_SPOT_WS_URL = url

    @classmethod
    def set_base_futures_url(cls, url: str) -> None:
        """Устанавливает базовый URL для вебсокетов Binance Futures."""
        cls._BASE_FUTURES_WS_URL = url

    def _generate_stream_url(
        self,
        type: StreamType,
        url: str,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> str:
        """Генерирует URL для вебсокета Binance. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (StreamType): Тип вебсокета.
            url (str): Базовый URL для вебсокета.
            symbol (str | None): Символ для подписки.
            symbols (list[str] | None): Список символов для подписки.

        Возвращает:
            str: URL для вебсокета.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if symbol:
            return f"{url}/{symbol.lower()}@{type}"
        if symbols:
            return f"{url}/{'!'.join([symbol.lower() for symbol in symbols])}@{type}"
        return f"{url}/@{type}"

    def agg_trade(self, callback: Callable, symbol: str) -> BaseSyncWebsocket:
        """Создает вебсокет для получения агрегированных сделок."""
        url = self._generate_stream_url(type="aggTrade", url=self._BASE_SPOT_URL, symbol=symbol)
        print(url)
        return BaseSyncWebsocket(callback=callback, url=url)
