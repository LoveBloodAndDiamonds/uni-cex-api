__all__ = ["WebsocketManager"]


from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from unicex._base.asyncio import Websocket
from unicex.exceptions import NotAuthorized

from .._mixins import WebsocketManagerMixin
from ..types import (
    BookDepthLevels,
    ContinuousContractType,
    FuturesTimeframe,
    MarkPriceUpdateSpeed,
    RollingWindowSize,
    SpotTimeframe,
)
from .client import Client
from .user_websocket import UserWebsocket

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager(WebsocketManagerMixin):
    """Менеджер асинхронных вебсокетов для Binance."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, котоыре прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="trade",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def agg_trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения агрегированных сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="aggTrade",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def klines(
        self,
        callback: CallbackType,
        interval: SpotTimeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            interval (`SpotTimeframe`): Временной интервал свечей.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"kline_{interval}",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def depth_stream(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="depth",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def symbol_mini_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для мини‑статистики тикера за последние 24 часа.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="miniTicker",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def mini_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч."""
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_SPOT_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def symbol_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для расширенной статистики тикера за последние 24 часа.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="ticker",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_SPOT_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def symbol_rolling_window_ticker(
        self,
        callback: CallbackType,
        window: RollingWindowSize,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения статистики тикера за указанное окно времени.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            window (`RollingWindowSize`): Размер окна статистики.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"ticker_{window}",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def rolling_window_ticker(self, callback: CallbackType, window: RollingWindowSize) -> Websocket:
        """Создает вебсокет для получения статистики всех тикеров за указанное окно времени."""
        url = self._generate_stream_url(type=f"!ticker_{window}@arr", url=self._BASE_SPOT_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def avg_price(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения среднего прайса (Average Price).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="avgPrice",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def book_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по символам.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="bookTicker",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def book_depth(
        self,
        callback: CallbackType,
        levels: BookDepthLevels,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана глубиной N уровней.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            levels (`BookDepthLevels`): Глубина стакана (уровни).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"depth{levels}",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def user_data_stream(self, callback: CallbackType) -> UserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных."""
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return UserWebsocket(callback=callback, client=self.client, type="SPOT", **self._ws_kwargs)

    def multiplex_socket(self, callback: CallbackType, streams: str) -> Websocket:
        """Создает вебсокет для мультиплексирования нескольких стримов в один.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            streams (`str`): Строка с перечислением стримов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return Websocket(
            callback=callback, url=self._BASE_SPOT_URL + "?" + streams, **self._ws_kwargs
        )

    def futures_trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="trade",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_agg_trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения агрегированных сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="aggTrade",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_klines(
        self,
        callback: CallbackType,
        interval: FuturesTimeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`FuturesTimeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"kline_{interval}",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_mini_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для мини‑статистики тикера за последние 24 часа.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="miniTicker",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_mini_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для расширенной статистики тикера за последние 24 часа.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="ticker",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения расширенной статистики всех тикеров за последние 24 ч.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_book_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по символам.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="bookTicker",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_book_depth(
        self,
        callback: CallbackType,
        symbol: str | None,
        levels: BookDepthLevels,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана глубиной N уровней.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            levels (`BookDepthLevels`): Глубина стакана (уровни).
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"depth{levels}",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_depth_stream(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="depth",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_mark_price(
        self, callback: CallbackType, interval: MarkPriceUpdateSpeed = "1s"
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`MarkPriceUpdateSpeed`): Частота обновления ("1s" или пусто).

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if interval == "1s":
            type = f"!markPrice@arr@{interval}"
        else:
            type = "!markPrice@arr"
        url = self._generate_stream_url(type=type, url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_mark_price(
        self,
        callback: CallbackType,
        interval: MarkPriceUpdateSpeed = "1s",
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate по символам.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`MarkPriceUpdateSpeed`): Частота обновления ("1s" или пусто).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if interval == "1s":
            type = f"markPrice@{interval}"
        else:
            type = "markPrice"
        url = self._generate_stream_url(
            type=type,
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_continuous_klines(
        self,
        callback: CallbackType,
        pair: str,
        contract_type: ContinuousContractType,
        interval: FuturesTimeframe,
    ) -> Websocket:
        """Создает вебсокет для получения свечей по непрерывным контрактам (continuous contract)."""
        url = self._generate_stream_url(
            type=f"{pair.lower()}_{contract_type}@continuousKline_{interval}",
            url=self._BASE_FUTURES_URL,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def liquidation_order(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения ликвидационных ордеров по символам.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="forceOrder",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def all_liquidation_orders(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения всех ликвидационных ордеров по рынку."""
        url = self._generate_stream_url(type="!forceOrder@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_composite_index(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения информации по композитному индексу.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="compositeIndex",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_contract_info(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения информации о контрактах (Contract Info Stream)."""
        url = self._generate_stream_url(type="!contractInfo", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_multi_assets_index(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения индекса активов в режиме Multi-Assets Mode.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!assetIndex@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_user_data_stream(self, callback: CallbackType) -> UserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `UserWebsocket`: Вебсокет для получения информации о пользовательских данных.
        """
        if not self.client or not self.client.is_authorized():
            raise NotAuthorized("You must provide authorized client.")
        return UserWebsocket(
            callback=callback, client=self.client, type="FUTURES", **self._ws_kwargs
        )

    def futures_multiplex_socket(self, callback: CallbackType, streams: str) -> Websocket:
        """Создает вебсокет для мультиплексирования нескольких стримов в один.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            streams (`str`): Строка с перечислением стримов.

        Возвращает:
            `Websocket`: Вебсокет для получения информации о пользовательских данных.
        """
        return Websocket(
            callback=callback, url=self._BASE_FUTURES_URL + "?" + streams, **self._ws_kwargs
        )
