__all__ = ["WebsocketManager"]

import json
import warnings
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Bybit."""

    _SPOT_URL: str = "wss://stream.bybit.com/v5/public/spot"
    """Базовый URL для вебсокета на спот."""

    _LINEAR_URL: str = "wss://stream.bybit.com/v5/public/linear"
    """Базовый URL для вебсокета на USDT/USDC перпетуалы и фьючерсы."""

    _INVERSE_URL: str = "wss://stream.bybit.com/v5/public/inverse"
    """Базовый URL для вебсокета на инверсные контракты."""

    _OPTION_URL: str = "wss://stream.bybit.com/v5/public/option"
    """Базовый URL для вебсокета на опционы."""

    _PRIVATE_URL: str = "wss://stream.bybit.com/v5/private"
    """Базовый URL для приватных вебсокетов."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Bybit.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _generate_subscription_message(
        self,
        topics: Sequence[str],
        req_id: str | None = None,
    ) -> list[str]:
        """Сформировать сообщение для подписки на вебсокет.

        Параметры:
            topics (`Sequence[str]`): Список топиков для подписки.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `list[str]`: Список JSON строк для отправки.
        """
        message = {"op": "subscribe", "args": list(topics)}
        if req_id:
            message["req_id"] = req_id

        return [json.dumps(message)]

    def _get_url_for_category(
        self, category: Literal["spot", "linear", "inverse", "option", "private"]
    ) -> str:
        """Получить URL для категории.

        Параметры:
            category (`Literal["spot", "linear", "inverse", "option", "private"]`): Категория рынка.

        Возвращает:
            `str`: URL для вебсокета.
        """
        if category == "spot":
            return self._SPOT_URL
        elif category == "linear":
            return self._LINEAR_URL
        elif category == "inverse":
            return self._INVERSE_URL
        elif category == "option":
            return self._OPTION_URL
        elif category == "private":
            return self._PRIVATE_URL
        else:
            raise ValueError(f"Unsupported category: {category}")

    def orderbook(
        self,
        callback: CallbackType,
        category: Literal["spot", "linear", "inverse", "option"],
        depth: Literal[1, 25, 50, 100, 200, 500, 1000] = 1,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных order book.

        https://bybit-exchange.github.io/docs/v5/websocket/public/orderbook

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["spot", "linear", "inverse", "option"]`): Категория рынка.
            depth (`Literal[1, 25, 50, 100, 200, 500, 1000]`): Глубина order book.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"orderbook.{depth}.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def kline(
        self,
        callback: CallbackType,
        category: Literal["spot", "linear", "inverse", "option"],
        interval: Literal[
            "1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"
        ],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных klines (свечей).

        https://bybit-exchange.github.io/docs/v5/websocket/public/kline

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["spot", "linear", "inverse", "option"]`): Категория рынка.
            interval (`Literal["1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"]`): Интервал свечи.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"kline.{interval}.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def trade(
        self,
        callback: CallbackType,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения публичных сделок.

        https://bybit-exchange.github.io/docs/v5/websocket/public/trade

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["spot", "linear", "inverse", "option"]`): Категория рынка.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"publicTrade.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def ticker(
        self,
        callback: CallbackType,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения тикеров.

        https://bybit-exchange.github.io/docs/v5/websocket/public/ticker

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["spot", "linear", "inverse", "option"]`): Категория рынка.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"tickers.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def liquidation(
        self,
        callback: CallbackType,
        category: Literal["linear", "inverse"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных ликвидаций.

        https://bybit-exchange.github.io/docs/v5/websocket/public/liquidation

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["linear", "inverse"]`): Категория рынка (только для деривативов).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        warnings.warn(
            "TDepreicated liquidation stream, please move to All Liquidation Subscribe"
            "to the liquidation stream. Pushes at most one order per second per symbol."
            "As such, this feed does not push all liquidations that occur on Bybit.",
            DeprecationWarning,
            stacklevel=2,
        )

        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"liquidation.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def all_liquidation(
        self,
        callback: CallbackType,
        category: Literal["linear", "inverse"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных ликвидаций.

        https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            category (`Literal["linear", "inverse"]`): Категория рынка (только для деривативов).
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        tickers = [symbol] if symbol else symbols
        topics = [f"allLiquidation.{ticker.upper()}" for ticker in tickers]  # type: ignore

        subscription_messages = self._generate_subscription_message(topics, req_id)
        url = self._get_url_for_category(category)

        return Websocket(
            callback=callback,
            url=url,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )
