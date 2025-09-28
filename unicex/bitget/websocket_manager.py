__all__ = ["WebsocketManager"]


import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Binance."""

    _BASE_URL: str = "wss://ws.bitget.com/v2/ws/public"
    """Базовый URL для вебсокета."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

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
    ) -> str:
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

        return json.dumps({"op": "subscribe", "args": streams})

    def trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        https://www.bitget.com/api-doc/spot/websocket/public/Trades-Channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subsription_message = self._generate_subscription_message(
            topic="trade",
            market_type="SPOT",
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=[subsription_message],
            **self._ws_kwargs,
        )
