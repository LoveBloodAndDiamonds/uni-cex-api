__all__ = ["WebsocketManager"]


import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, Literal

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Gateio."""

    _SPOT_URL = "wss://api.gateio.ws/ws/v4/"
    """Адрес вебсокета для спотового рынка."""

    _FUTURES_URL = "wss://fx-ws.gateio.ws/v4/ws/usdt"
    """Адрес вебсокета для фьючерсного рынка."""

    def _build_message(
        self,
        channel: str,
        payload: list[str],
        event: Literal["subscribe", "unsubscribe"] = "subscribe",
    ) -> str:
        """Формирует JSON сообщение для подписки."""
        return json.dumps(
            {
                "time": int(time.time()),
                "id": int(time.time() * 1e6),
                "channel": channel,
                "event": event,
                "payload": payload,
            }
        )
