from collections.abc import Callable

from unicex.base import BaseWebsocket
from unicex.exceptions import NotAuthorized

from .client import BinanceClient
from .types import (
    BookDepthLevels,
    ContinuousContractType,
    FuturesTimeframe,
    MarkPriceUpdateSpeed,
    RollingWindowSize,
    SpotTimeframe,
)
from .user_websocket import BinanceUserWebsocket


class BinanceWebsocketManager:
    """Менеджер вебсокетов для Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    _TESTNET_FUTURES_URL: str = "wss://testnet.binancefuture.com/ws-fapi/v1"

    def __init__(self, client: BinanceClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (BaseSyncClient | None): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
        """
        self.client = client

    def _generate_stream_url(
        self,
        type: str,
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
            return f"{url}/ws/{symbol.lower()}@{type}"
        if symbols:
            streams = "/".join(f"{s.lower()}@{type}" for s in symbols)
            return f"{url}/stream?streams={streams}"
        return f"{url}/ws/{type}"

    def trade(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения сделок."""
        url = self._generate_stream_url(type="trade", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def agg_trade(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения агрегированных сделок."""
        url = self._generate_stream_url(type="aggTrade", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def klines(self, callback: Callable, symbol: str, interval: SpotTimeframe) -> BaseWebsocket:
        """Создает вебсокет для получения свечей."""
        url = self._generate_stream_url(
            type=f"kline_{interval}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def depth_stream(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины)."""
        url = self._generate_stream_url(type="depth", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def symbol_mini_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения мини-статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="miniTicker", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def mini_ticker(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_SPOT_URL)
        return BaseWebsocket(callback=callback, url=url)

    def symbol_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения расширенной статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="ticker", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def ticker(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_SPOT_URL)
        return BaseWebsocket(callback=callback, url=url)

    def symbol_rolling_window_ticker(
        self, callback: Callable, symbol: str, window: RollingWindowSize
    ) -> BaseWebsocket:
        """Создает вебсокет для получения статистики тикера за указанное окно времени."""
        url = self._generate_stream_url(
            type=f"ticker_{window}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def rolling_window_ticker(self, callback: Callable, window: RollingWindowSize) -> BaseWebsocket:
        """Создает вебсокет для получения статистики всех тикеров за указанное окно времени."""
        url = self._generate_stream_url(type=f"!ticker_{window}@arr", url=self._BASE_SPOT_URL)
        return BaseWebsocket(callback=callback, url=url)

    def avg_price(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения среднего прайса (Average Price)."""
        url = self._generate_stream_url(type="avgPrice", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def book_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения лучших бид/аск по символу."""
        url = self._generate_stream_url(type="bookTicker", url=self._BASE_SPOT_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def book_depth(self, callback: Callable, symbol: str, levels: BookDepthLevels) -> BaseWebsocket:
        """Создает вебсокет для получения стакана глубиной N уровней."""
        url = self._generate_stream_url(
            type=f"depth{levels}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def user_data_stream(self, callback: Callable) -> BinanceUserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных."""
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return BinanceUserWebsocket(callback=callback, client=self.client, type="SPOT")

    def futures_trade(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения сделок."""
        url = self._generate_stream_url(type="trade", url=self._BASE_FUTURES_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def futures_agg_trade(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения агрегированных сделок."""
        url = self._generate_stream_url(type="aggTrade", url=self._BASE_FUTURES_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def futures_klines(
        self, callback: Callable, symbol: str, interval: FuturesTimeframe
    ) -> BaseWebsocket:
        """Создает вебсокет для получения свечей."""
        url = self._generate_stream_url(
            type=f"kline_{interval}", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def futures_symbol_mini_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения мини-статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(
            type="miniTicker", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def futures_mini_ticker(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_symbol_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения расширенной статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="ticker", url=self._BASE_FUTURES_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def futures_ticker(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_book_ticker(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения лучших бид/аск по символу."""
        url = self._generate_stream_url(
            type="bookTicker", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def futures_book_depth(
        self, callback: Callable, symbol: str, levels: BookDepthLevels
    ) -> BaseWebsocket:
        """Создает вебсокет для получения стакана глубиной N уровней."""
        url = self._generate_stream_url(
            type=f"depth{levels}", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def futures_depth_stream(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины)."""
        url = self._generate_stream_url(type="depth", url=self._BASE_FUTURES_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def futures_mark_price(
        self, callback: Callable, interval: MarkPriceUpdateSpeed = "1s"
    ) -> BaseWebsocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров."""
        if interval == "1s":
            type = f"!markPrice@arr@{interval}"
        else:
            type = "!markPrice@arr"
        url = self._generate_stream_url(type=type, url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_symbol_mark_price(
        self, callback: Callable, symbol: str, interval: MarkPriceUpdateSpeed = "1s"
    ) -> BaseWebsocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров."""
        if interval == "1s":
            type = f"markPrice@{interval}"
        else:
            type = "markPrice"
        url = self._generate_stream_url(type=type, url=self._BASE_FUTURES_URL, symbol=symbol)
        return BaseWebsocket(callback=callback, url=url)

    def futures_continuous_klines(
        self,
        callback: Callable,
        pair: str,
        contract_type: ContinuousContractType,
        interval: FuturesTimeframe,
    ) -> BaseWebsocket:
        """Создает вебсокет для получения свечей по непрерывным контрактам (continuous contract)."""
        url = self._generate_stream_url(
            type=f"{pair.lower()}_{contract_type}@continuousKline_{interval}",
            url=self._BASE_FUTURES_URL,
        )
        return BaseWebsocket(callback=callback, url=url)

    def liquidation_order(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения ликвидационных ордеров по символу."""
        url = self._generate_stream_url(
            type="forceOrder", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def all_liquidation_orders(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения всех ликвидационных ордеров по рынку."""
        url = self._generate_stream_url(type="!forceOrder@arr", url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_composite_index(self, callback: Callable, symbol: str) -> BaseWebsocket:
        """Создает вебсокет для получения информации по композитному индексу (Не работает на 2025.09.07)."""
        url = self._generate_stream_url(
            type="compositeIndex", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return BaseWebsocket(callback=callback, url=url)

    def futures_contract_info(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения информации о контрактах (Contract Info Stream)."""
        url = self._generate_stream_url(type="!contractInfo", url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_multi_assets_index(self, callback: Callable) -> BaseWebsocket:
        """Создает вебсокет для получения индекса активов в режиме Multi-Assets Mode."""
        url = self._generate_stream_url(type="!assetIndex@arr", url=self._BASE_FUTURES_URL)
        return BaseWebsocket(callback=callback, url=url)

    def futures_user_data_stream(self, callback: Callable) -> BinanceUserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных."""
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return BinanceUserWebsocket(callback=callback, client=self.client, type="FUTURES")
