__all__ = ["WebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from unicex._base import Websocket
from unicex.exceptions import NotAuthorized

from .client import Client
from .user_websocket import UserWebsocket

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, котоыре прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _generate_stream_url(
        self,
        type: str,
        url: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        require_symbol: bool = False,
    ) -> str:
        """Генерирует URL для вебсокета Binance. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (`str`): Тип вебсокета.
            url (`str`): Базовый URL для вебсокета.
            symbol (`str | None`): Символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для подписки.
            require_symbol (`bool`): Требуется ли символ для подписки.

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
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#trade-streams

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

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#aggregate-trade-streams

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
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#klinecandlestick-streams-for-utc

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            interval (`str`): Временной интервал свечей.
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
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины).

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#diff-depth-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str | None`): Скорость обновления стакана ("1000ms" | "100ms"). По умолчанию "1000ms".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="depth" + f"@{update_speed}" if update_speed == "100ms" else "",
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

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#individual-symbol-mini-ticker-stream

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
        """Создает вебсокет для получения мини-статистики всех тикеров за последние 24 ч.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#individual-symbol-mini-ticker-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!miniTicker@arr", url=self._BASE_SPOT_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def symbol_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для расширенной статистики тикера за последние 24 часа.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#individual-symbol-ticker-streams

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

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#all-market-tickers-stream

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
        window: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения статистики тикера за указанное окно времени.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#individual-symbol-rolling-window-statistics-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            window (`str`): Размер окна статистики.
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

    def rolling_window_ticker(self, callback: CallbackType, window: str) -> Websocket:
        """Создает вебсокет для получения статистики всех тикеров за указанное окно времени.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#all-market-rolling-window-statistics-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            window (`str`): Размер окна статистики.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type=f"!ticker_{window}@arr", url=self._BASE_SPOT_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def avg_price(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения среднего прайса (Average Price).

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#average-price

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

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#individual-symbol-book-ticker-streams

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

    def partial_book_depth(
        self,
        callback: CallbackType,
        levels: str,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана глубиной N уровней.

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#partial-book-depth-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            levels (`str`): Глубина стакана (уровни).
            update_speed (`str | None`): Скорость обновления стакана ("100ms" | "1000ms"). По умолчанию: "1000ms".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"depth{levels}" + f"@{update_speed}" if update_speed else "",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def diff_depth(
        self,
        callback: CallbackType,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины).

        https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams#diff-depth-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str | None`): Скорость обновления стакана ("100ms" | "1000ms"). По умолчанию: "1000ms".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="depth" + f"@{update_speed}" if update_speed else "",
            url=self._BASE_SPOT_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def user_data_stream(self, callback: CallbackType) -> UserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных.

        https://developers.binance.com/docs/binance-spot-api-docs/user-data-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `UserWebsocket`: Объект для управления вебсокет соединением.
        """
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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams

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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams

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
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Kline-Candlestick-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`str`): Временной интервал свечей.
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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Individual-Symbol-Mini-Ticker-Stream

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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Mini-Tickers-Stream

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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Individual-Symbol-Ticker-Streams

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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Tickers-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!ticker@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_book_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по символам.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Individual-Symbol-Book-Ticker-Streams

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

    def futures_book_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по символам.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Book-Tickers-Stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!bookTicker", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_partial_book_depth(
        self,
        callback: CallbackType,
        symbol: str | None,
        levels: str,
        update_speed: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана глубиной N уровней.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Partial-Book-Depth-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            levels (`str`): Глубина стакана (уровни).
            update_speed (`str`): Скорость обновления стакана (100ms | 500ms | None). По умолчанию - 250ms.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type=f"depth{levels}" + f"@{update_speed}" if update_speed else "",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_diff_depth(
        self,
        callback: CallbackType,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Diff-Book-Depth-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str`): Скорость обновления стакана (100ms | 500ms | None). По умолчанию - 250ms.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="depth" + f"@{update_speed}" if update_speed else "",
            url=self._BASE_FUTURES_URL,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_mark_price(
        self, callback: CallbackType, update_speed: str | None = None
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate для всех тикеров.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream-for-All-market

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str`): Частота обновления ("1s" или пусто). По умолчанию "3s".

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="!markPrice" + f"@{update_speed}" if update_speed else "",
            url=self._BASE_FUTURES_URL,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_mark_price(
        self,
        callback: CallbackType,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate по символам.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Mark-Price-Stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str`): Частота обновления ("1s" или пусто). По умолчанию "3s".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="markPrice" + f"@{update_speed}" if update_speed else "",
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
        contract_type: str,
        interval: str,
    ) -> Websocket:
        """Создает вебсокет для получения свечей по непрерывным контрактам (continuous contract).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Continuous-Contract-Kline-Candlestick-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            pair (`str`): Название пары.
            contract_type (`str`): Тип контракта.
            interval (`str`): Временной интервал свечей..

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
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

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams

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
        """Создает вебсокет для получения всех ликвидационных ордеров по рынку.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/All-Market-Liquidation-Order-Streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!forceOrder@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_composite_index(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения информации по композитному индексу.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Composite-Index-Symbol-Information-Streams

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
        """Создает вебсокет для получения информации о контрактах (Contract Info Stream).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Contract-Info-Stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!contractInfo", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_multi_assets_index(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения индекса активов в режиме Multi-Assets Mode.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Multi-Assets-Mode-Asset-Index

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!assetIndex@arr", url=self._BASE_FUTURES_URL)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_user_data_stream(self, callback: CallbackType) -> UserWebsocket:
        """Создает вебсокет для получения информации о пользовательских данных.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams

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
