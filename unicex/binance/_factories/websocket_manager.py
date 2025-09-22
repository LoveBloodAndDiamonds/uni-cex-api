# pyright: reportArgumentType=false
# Отключили pyright для строчек типа:
# ```python
# return self._websocket_cls(callback=callback, url=url)
# ```
# Потому что мы знаем, что в фабрики будем передавать только SyncWebsocket+SyncCallback, или
# AsyncWebsocket+AsyncCallback, а вот pytight допускает, что это может быть не так.


__all__ = ["WebsocketManagerFactory"]

from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar, overload

from unicex._base.asyncio import Websocket as AsyncWebsocket
from unicex._base.sync import Websocket
from unicex.exceptions import NotAuthorized

from ..asyncio.client import Client as AsyncClient
from ..asyncio.user_websocket import UserWebsocket as AsyncUserWebsocket
from ..sync.client import Client
from ..sync.user_websocket import UserWebsocket
from ..types import (
    BookDepthLevels,
    ContinuousContractType,
    FuturesTimeframe,
    MarkPriceUpdateSpeed,
    RollingWindowSize,
    SpotTimeframe,
)

TClient = TypeVar("TClient", Client, AsyncClient)
TWebsocket = TypeVar("TWebsocket", Websocket, AsyncWebsocket)
TUserWebsocket = TypeVar("TUserWebsocket", UserWebsocket, AsyncUserWebsocket)
type SyncCallback = Callable[[Any], None]
type AsyncCallback = Callable[[Any], Awaitable[None]]
TCallbackType = TypeVar("TCallbackType", SyncCallback, AsyncCallback)


class WebsocketManagerFactory(Generic[TClient, TWebsocket, TUserWebsocket, TCallbackType]):
    """Фабрика менеджеров вебсокетов Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    def __init__(
        self,
        websocket_cls: type[TWebsocket],
        user_websocket_cls: type[TUserWebsocket],
        client: TClient | None = None,
    ) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            websocket_cls (TWebsocket): Класс вебсокета для использования.
            user_websocket_cls (TUserWebsocket): Класс вебсокета для использования.
            client (TClient | None): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
        """
        self._websocket_cls = websocket_cls
        self._user_websocket_cls = user_websocket_cls
        self.client = client

    @overload
    def _generate_stream_url(
        self,
        *,
        type: str,
        url: str,
        symbol: str,
        symbols: None = None,
        require_symbol: bool = True,
    ) -> str: ...

    @overload
    def _generate_stream_url(
        self,
        *,
        type: str,
        url: str,
        symbol: None = None,
        symbols: list[str],
        require_symbol: bool = True,
    ) -> str: ...

    @overload
    def _generate_stream_url(
        self,
        *,
        type: str,
        url: str,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        require_symbol: bool = False,
    ) -> str: ...

    def _generate_stream_url(
        self,
        type: str,
        url: str,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        require_symbol: bool = False,
    ) -> str:
        """Генерирует URL для вебсокета Binance. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (StreamType): Тип вебсокета.
            url (str): Базовый URL для вебсокета.
            symbol (str | None): Символ для подписки.
            symbols (list[str] | None): Список символов для подписки.
            require_symbol (bool): Требуется ли символ для подписки.

        Возвращает:
            str: URL для вебсокета.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if require_symbol and not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")
        if symbol:
            return f"{url}/ws/{symbol.lower()}@{type}"
        if symbols:
            streams = "/".join(f"{s.lower()}@{type}" for s in symbols)
            return f"{url}/stream?streams={streams}"
        return f"{url}/ws/{type}"

    def trade(
        self,
        callback: TCallbackType,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> TWebsocket:
        """Создает вебсокет для получения сделок."""
        url = self._generate_stream_url(
            type="trade",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return self._websocket_cls(callback=callback, url=url)

    def agg_trade(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения агрегированных сделок."""
        url = self._generate_stream_url(type="aggTrade", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def klines(self, callback: TCallbackType, symbol: str, interval: SpotTimeframe) -> TWebsocket:
        """Создает вебсокет для получения свечей."""
        url = self._generate_stream_url(
            type=f"kline_{interval}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def depth_stream(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины)."""
        url = self._generate_stream_url(type="depth", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def symbol_mini_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения мини-статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="miniTicker", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def mini_ticker(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_SPOT_URL)
        return self._websocket_cls(callback=callback, url=url)

    def symbol_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения расширенной статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="ticker", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def ticker(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_SPOT_URL)
        return self._websocket_cls(callback=callback, url=url)

    def symbol_rolling_window_ticker(
        self, callback: TCallbackType, symbol: str, window: RollingWindowSize
    ) -> TWebsocket:
        """Создает вебсокет для получения статистики тикера за указанное окно времени."""
        url = self._generate_stream_url(
            type=f"ticker_{window}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def rolling_window_ticker(
        self, callback: TCallbackType, window: RollingWindowSize
    ) -> TWebsocket:
        """Создает вебсокет для получения статистики всех тикеров за указанное окно времени."""
        url = self._generate_stream_url(type=f"!ticker_{window}@arr", url=self._BASE_SPOT_URL)
        return self._websocket_cls(callback=callback, url=url)

    def avg_price(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения среднего прайса (Average Price)."""
        url = self._generate_stream_url(type="avgPrice", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def book_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения лучших бид/аск по символу."""
        url = self._generate_stream_url(type="bookTicker", url=self._BASE_SPOT_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def book_depth(
        self, callback: TCallbackType, symbol: str, levels: BookDepthLevels
    ) -> TWebsocket:
        """Создает вебсокет для получения стакана глубиной N уровней."""
        url = self._generate_stream_url(
            type=f"depth{levels}", url=self._BASE_SPOT_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def user_data_stream(self, callback: TCallbackType) -> TUserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных."""
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return self._user_websocket_cls(callback=callback, client=self.client, type="SPOT")

    def futures_trade(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения сделок."""
        url = self._generate_stream_url(type="trade", url=self._BASE_FUTURES_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def futures_agg_trade(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения агрегированных сделок."""
        url = self._generate_stream_url(type="aggTrade", url=self._BASE_FUTURES_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def futures_klines(
        self, callback: TCallbackType, symbol: str, interval: FuturesTimeframe
    ) -> TWebsocket:
        """Создает вебсокет для получения свечей."""
        url = self._generate_stream_url(
            type=f"kline_{interval}", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def futures_symbol_mini_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения мини-статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(
            type="miniTicker", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def futures_mini_ticker(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_symbol_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения расширенной статистики тикера за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="ticker", url=self._BASE_FUTURES_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def futures_ticker(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч. (Не за сутки)."""
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_book_ticker(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения лучших бид/аск по символу."""
        url = self._generate_stream_url(
            type="bookTicker", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def futures_book_depth(
        self, callback: TCallbackType, symbol: str, levels: BookDepthLevels
    ) -> TWebsocket:
        """Создает вебсокет для получения стакана глубиной N уровней."""
        url = self._generate_stream_url(
            type=f"depth{levels}", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def futures_depth_stream(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины)."""
        url = self._generate_stream_url(type="depth", url=self._BASE_FUTURES_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def futures_mark_price(
        self, callback: TCallbackType, interval: MarkPriceUpdateSpeed = "1s"
    ) -> TWebsocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров."""
        if interval == "1s":
            type = f"!markPrice@arr@{interval}"
        else:
            type = "!markPrice@arr"
        url = self._generate_stream_url(type=type, url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_symbol_mark_price(
        self,
        callback: TCallbackType,
        symbol: str,
        interval: MarkPriceUpdateSpeed = "1s",
    ) -> TWebsocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров."""
        if interval == "1s":
            type = f"markPrice@{interval}"
        else:
            type = "markPrice"
        url = self._generate_stream_url(type=type, url=self._BASE_FUTURES_URL, symbol=symbol)
        return self._websocket_cls(callback=callback, url=url)

    def futures_continuous_klines(
        self,
        callback: TCallbackType,
        pair: str,
        contract_type: ContinuousContractType,
        interval: FuturesTimeframe,
    ) -> TWebsocket:
        """Создает вебсокет для получения свечей по непрерывным контрактам (continuous contract)."""
        url = self._generate_stream_url(
            type=f"{pair.lower()}_{contract_type}@continuousKline_{interval}",
            url=self._BASE_FUTURES_URL,
        )
        return self._websocket_cls(callback=callback, url=url)

    def liquidation_order(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения ликвидационных ордеров по символу."""
        url = self._generate_stream_url(
            type="forceOrder", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def all_liquidation_orders(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения всех ликвидационных ордеров по рынку."""
        url = self._generate_stream_url(type="!forceOrder@arr", url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_composite_index(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Создает вебсокет для получения информации по композитному индексу (Не работает на 2025.09.07)."""
        url = self._generate_stream_url(
            type="compositeIndex", url=self._BASE_FUTURES_URL, symbol=symbol
        )
        return self._websocket_cls(callback=callback, url=url)

    def futures_contract_info(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения информации о контрактах (Contract Info Stream)."""
        url = self._generate_stream_url(type="!contractInfo", url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_multi_assets_index(self, callback: TCallbackType) -> TWebsocket:
        """Создает вебсокет для получения индекса активов в режиме Multi-Assets Mode."""
        url = self._generate_stream_url(type="!assetIndex@arr", url=self._BASE_FUTURES_URL)
        return self._websocket_cls(callback=callback, url=url)

    def futures_user_data_stream(self, callback: TCallbackType) -> TUserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных."""
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return self._user_websocket_cls(callback=callback, client=self.client, type="FUTURES")
