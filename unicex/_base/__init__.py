"""Пакет с базовым клиентом для HTTP запросов и базовым вебсокетом."""

__all__ = [
    "BaseClient",
    "Websocket",
]

from .client import BaseClient
from .websocket import Websocket
