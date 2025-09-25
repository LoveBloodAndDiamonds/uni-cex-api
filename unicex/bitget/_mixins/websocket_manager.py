__all__ = ["WebsocketManagerMixin"]

import json
from collections.abc import Sequence
from typing import Literal


class WebsocketManagerMixin:
    """Миксин для менеджеров вебсокетов Bitget."""

    _BASE_URL: str = "wss://ws.bitget.com/v2/ws/public"
    """Базовый URL для вебсокета."""

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
