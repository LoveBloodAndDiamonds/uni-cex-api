__all__ = ["WebsocketManager"]


import gzip
import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

import orjson

from unicex._base import Websocket
from unicex.utils import validate_single_symbol_args

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для BingX."""

    _BASE_SPOT_URL: str = "wss://open-api-ws.bingx.com/market"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://open-api-swap.bingx.com/swap-market"
    """Базовый URL для вебсокета на фьючерсы."""

    class _BingXGzipDecoder:
        """Класс для декодирования gzip-сообщений WebSocket от BingX."""

        def decode(self, message: Any) -> dict | Literal["ping"]:
            if isinstance(message, bytes):
                try:
                    message = gzip.decompress(message).decode("utf-8")
                except OSError:
                    message = message.decode("utf-8")

            if message == "Ping":
                return "ping"

            return orjson.loads(message)

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для BingX.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _get_url(self, market_type: Literal["SPOT", "FUTURES"]) -> str:
        """Возвращает URL для указанного типа рынка."""
        if market_type == "SPOT":
            return self._BASE_SPOT_URL
        if market_type == "FUTURES":
            return self._BASE_FUTURES_URL
        raise ValueError(f"Unsupported market type: {market_type}")

    def _generate_subscription_messages(
        self,
        data_types: Sequence[str],
        req_id: str | None = None,
    ) -> list[str]:
        """Сформировать сообщения для подписки на вебсокет.

        Параметры:
            data_types (`Sequence[str]`): Список топиков для подписки.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `list[str]`: Список JSON-строк с сообщениями для подписки.
        """
        messages = []
        for data_type in data_types:
            message = {"reqType": "sub", "dataType": data_type}
            if req_id:
                message["id"] = req_id
            messages.append(json.dumps(message))
        return messages

    def trade(
        self,
        callback: CallbackType,
        market_type: Literal["SPOT", "FUTURES"],
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        req_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Subscribe%20to%20Tick-by-Tick%20Trades

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            market_type (`Literal["SPOT", "FUTURES"]`): Тип рынка.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            req_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        validate_single_symbol_args(symbol, symbols)

        tickers = [symbol] if symbol else symbols
        data_types = [f"{ticker.upper()}@trade" for ticker in tickers]  # type: ignore[arg-type]

        subscription_messages = self._generate_subscription_messages(data_types, req_id)
        return Websocket(
            callback=callback,
            url=self._get_url(market_type),
            subscription_messages=subscription_messages,
            decoder=self._BingXGzipDecoder,
            pong_message="Pong",
            **self._ws_kwargs,
        )
