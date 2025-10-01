__all__ = ["WebsocketManager"]


from collections.abc import Awaitable, Callable
from typing import Any

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для BTSE."""
