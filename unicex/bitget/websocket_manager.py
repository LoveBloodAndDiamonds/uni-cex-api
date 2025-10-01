__all__ = ["WebsocketManager"]


import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Bitget."""

    _BASE_URL: str = "wss://ws.bitget.com/v2/ws/public"
    """Базовый URL для вебсокета."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Bitget.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, котоыре прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = {"ping_message": "ping", **ws_kwargs}

    def _generate_subscription_message(
        self,
        topic: str,
        market_type: Literal["SPOT", "USDT-FUTURES"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> list[str]:
        """Сформировать сообщение для подписки на вебсокет.

        Параметры:
            topic (`str`): Канал подписки (например: "ticker", "candle1m", "depth").
            market_type (`"SPOT" | "USDT-FUTURES"`): Тип рынка для подписки.
            symbol (`str | None`): Торговая пара. Нельзя использовать одновременно с `symbols`.
            symbols (`Sequence[str] | None`): Список торговых пар. Нельзя использовать одновременно с `symbol`.

        Возвращает:
            `str`: JSON-строка с сообщением для подписки на вебсокет.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        streams: list[dict] = [
            {
                "instType": market_type,
                "channel": topic,
                "instId": ticker.upper(),
            }
            for ticker in tickers  # type: ignore
        ]

        return [json.dumps({"op": "subscribe", "args": streams})]

    def trade(
        self,
        callback: CallbackType,
        market_type: Literal["SPOT", "USDT-FUTURES"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        https://www.bitget.com/api-doc/spot/websocket/public/Trades-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            market_type (`Literal["SPOT", "USDT-FUTURES"]`): Тип рынка.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subsription_messages = self._generate_subscription_message(
            topic="trade",
            market_type=market_type,
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=subsription_messages,
            **self._ws_kwargs,
        )

    def ticker(
        self,
        callback: CallbackType,
        market_type: Literal["SPOT", "USDT-FUTURES"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения тикеров.

        https://www.bitget.com/api-doc/spot/websocket/public/Tickers-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            market_type (`Literal["SPOT", "USDT-FUTURES"]`): Тип рынка.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            topic="ticker",
            market_type=market_type,
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def candlestick(
        self,
        callback: CallbackType,
        market_type: Literal["SPOT", "USDT-FUTURES"],
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных свечей (candlestick).

        https://www.bitget.com/api-doc/spot/websocket/public/Candlesticks-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            market_type (`Literal["SPOT", "USDT-FUTURES"]`): Тип рынка.
            interval (`str`): Интервал свечи, например "1m", "1H", "1Dutc".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        topic = f"candle{interval}"
        subscription_messages = self._generate_subscription_message(
            topic=topic,
            market_type=market_type,
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def depth(
        self,
        callback: CallbackType,
        market_type: Literal["SPOT", "USDT-FUTURES"],
        depth_type: str = "books",
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных глубины рынка (order book).

        https://www.bitget.com/api-doc/spot/websocket/public/Depth-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            market_type (`Literal["SPOT", "USDT-FUTURES"]`): Тип рынка.
            depth_type (`str`): Тип глубины: "books", "books1", "books5", "books15".
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            topic=depth_type,
            market_type=market_type,
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def auction(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения информации о Call Auction.

        https://www.bitget.com/api-doc/spot/websocket/public/Auction-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            topic="auction",
            market_type="SPOT",
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )
