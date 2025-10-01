__all__ = ["WebsocketManager"]


import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для <Exchange>."""
