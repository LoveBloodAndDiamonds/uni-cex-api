__all__ = ["WebsocketManager"]

import json
import time
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

from unicex._base import Websocket
from unicex.utils import validate_single_symbol_args

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Kucoin."""

    _SPOT_URL: str = "wss://x-push-spot.kucoin.com"
    """Базовый URL для вебсокета на спот."""

    _FUTURES_URL: str = "wss://x-push-futures.kucoin.com"
    """Базовый URL для вебсокета на фьючерсы."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Kucoin.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _get_url(self, trade_type: Literal["SPOT", "FUTURES"]) -> str:
        """Возвращает URL для указанного типа рынка."""
        if trade_type == "SPOT":
            return self._SPOT_URL
        if trade_type == "FUTURES":
            return self._FUTURES_URL
        raise ValueError(f"Unsupported trade type: {trade_type}")

    def _normalize_depth(self, depth: str | int) -> str:
        """Нормализует значение глубины стакана."""
        depth_value = str(depth)
        if depth_value not in {"1", "5", "50", "increment"}:
            raise ValueError("depth must be one of: 1, 5, 50, increment")
        return depth_value

    def _build_subscription_messages(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        depth: str,
        symbols: Sequence[str],
        rpi_filter: Literal[0, 1],
        request_id: str | None = None,
    ) -> list[str]:
        """Формирует сообщения для подписки."""
        base_id = int(time.time() * 1000)
        messages: list[str] = []
        for index, symbol in enumerate(symbols):
            payload = {
                "id": request_id or str(base_id + index),
                "action": "SUBSCRIBE",
                "channel": "obu",
                "tradeType": trade_type,
                "symbol": symbol.upper(),
                "depth": depth,
                "rpiFilter": rpi_filter,
            }
            messages.append(json.dumps(payload))
        return messages

    def orderbook(
        self,
        callback: CallbackType,
        trade_type: Literal["SPOT", "FUTURES"],
        depth: Literal["1", "5", "50", "increment"] | int = "1",
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        rpi_filter: Literal[0, 1] = 0,
        request_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения order book.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            trade_type (`Literal["SPOT", "FUTURES"]`): Тип рынка.
            depth (`Literal["1", "5", "50", "increment"] | int`): Глубина стакана.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            rpi_filter (`Literal[0, 1]`): Фильтр RPI. Доступен только для фьючерсов (depth=5/50).
            request_id (`str | None`): Опциональный идентификатор запроса.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        validate_single_symbol_args(symbol, symbols)

        depth_value = self._normalize_depth(depth)
        if rpi_filter not in (0, 1):
            raise ValueError("rpi_filter must be 0 or 1")
        if trade_type == "SPOT" and rpi_filter == 1:
            raise ValueError("rpi_filter=1 is supported only for FUTURES")
        if rpi_filter == 1 and depth_value not in {"5", "50"}:
            raise ValueError("rpi_filter=1 supports only depth=5 or depth=50")

        tickers = [symbol] if symbol else symbols
        subscription_messages = self._build_subscription_messages(
            trade_type=trade_type,
            depth=depth_value,
            symbols=tickers,  # type: ignore[arg-type]
            rpi_filter=rpi_filter,
            request_id=request_id,
        )
        return Websocket(
            callback=callback,
            url=self._get_url(trade_type),
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )
