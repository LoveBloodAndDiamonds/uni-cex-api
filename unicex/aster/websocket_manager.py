__all__ = ["WebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Aster."""

    _BASE_URL: str = "wss://fstream.asterdex.com"
    """Базовый URL для вебсокетов Aster Futures."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Aster.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _generate_stream_url(
        self,
        type: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        require_symbol: bool = False,
    ) -> str:
        """Генерирует URL для вебсокета Aster. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (`str`): Тип стрима.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            require_symbol (`bool`): Требуется ли символ для подписки.

        Возвращает:
            `str`: URL для вебсокета.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if require_symbol and not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")
        if symbol:
            return f"{self._BASE_URL}/ws/{symbol.lower()}@{type}"
        if symbols:
            streams = "/".join(f"{s.lower()}@{type}" for s in symbols)
            return f"{self._BASE_URL}/stream?streams={streams}"
        return f"{self._BASE_URL}/ws/{type}"

    def futures_agg_trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения агрегированных сделок на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#aggregate-trade-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="aggTrade",
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_mark_price(
        self,
        callback: CallbackType,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate по символам на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str | None`): Частота обновления ("1s" или пусто). По умолчанию "3s".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        stream_type = "markPrice" + (f"@{update_speed}" if update_speed else "")
        url = self._generate_stream_url(
            type=stream_type,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_mark_price(
        self, callback: CallbackType, update_speed: str | None = None
    ) -> Websocket:
        """Создает вебсокет для получения mark price и funding rate для всех символов на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price-stream-for-all-markets

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str | None`): Частота обновления ("1s" или пусто). По умолчанию "3s".

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        stream_type = "!markPrice@arr" + (f"@{update_speed}" if update_speed else "")
        url = self._generate_stream_url(type=stream_type)
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_klines(
        self,
        callback: CallbackType,
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#kline-candlestick-streams

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
        """Создает вебсокет для мини‑статистики тикера за последние 24 часа на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#individual-symbol-mini-ticker-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="miniTicker",
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_mini_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для мини‑статистики всех тикеров за последние 24 часа на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-market-mini-tickers-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!miniTicker@arr")
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для расширенной статистики тикера за последние 24 часа на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#individual-symbol-ticker-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="ticker",
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для расширенной статистики всех тикеров за последние 24 часа на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-market-tickers-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!ticker@arr")
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_symbol_book_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по символам на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#individual-symbol-book-ticker-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="bookTicker",
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_book_ticker(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения лучших бид/аск по всем символам на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-book-tickers-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!bookTicker")
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_liquidation_order(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения ликвидационных ордеров по символам на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#liquidation-order-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(
            type="forceOrder",
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(
            callback=callback,
            url=url,
            no_message_reconnect_timeout=60 * 15,
            **self._ws_kwargs,
        )

    def futures_all_liquidation_orders(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения всех ликвидационных ордеров по рынку на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-market-liquidation-order-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        url = self._generate_stream_url(type="!forceOrder@arr")
        return Websocket(
            callback=callback,
            url=url,
            no_message_reconnect_timeout=60 * 15,
            **self._ws_kwargs,
        )

    def futures_partial_book_depth(
        self,
        callback: CallbackType,
        levels: str,
        update_speed: str | None = None,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана глубиной N уровней на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#partial-book-depth-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            levels (`str`): Глубина стакана (уровни).
            update_speed (`str | None`): Скорость обновления стакана ("100ms" | "500ms"). По умолчанию: "250ms".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        stream_type = f"depth{levels}" + (f"@{update_speed}" if update_speed else "")
        url = self._generate_stream_url(
            type=stream_type,
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
        """Создает вебсокет для получения событий изменения стакана (без лимита глубины) на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#diff-book-depth-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            update_speed (`str | None`): Скорость обновления стакана ("100ms" | "500ms"). По умолчанию: "250ms".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        stream_type = "depth" + (f"@{update_speed}" if update_speed else "")
        url = self._generate_stream_url(
            type=stream_type,
            symbol=symbol,
            symbols=symbols,
            require_symbol=True,
        )
        return Websocket(callback=callback, url=url, **self._ws_kwargs)

    def futures_multiplex_socket(self, callback: CallbackType, streams: str) -> Websocket:
        """Создает вебсокет для мультиплексирования нескольких стримов в один на фьючерсах.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            streams (`str`): Строка с перечислением стримов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if streams.startswith("streams="):
            url = f"{self._BASE_URL}/stream?{streams}"
        else:
            url = f"{self._BASE_URL}/stream?streams={streams}"
        return Websocket(callback=callback, url=url, **self._ws_kwargs)
