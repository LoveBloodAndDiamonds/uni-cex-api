__all__ = [
    "IUniWebsocketManager",
]

from abc import ABC, abstractmethod

from unicex.base import BaseSyncWebsocket

from .uni_client import ISyncUniClient


class IUniWebsocketManager(ABC):
    """Интерфейс для реализации менеджера вебсокетов."""

    def __init__(self, client: ISyncUniClient | None = None) -> None:
        """Инициализирует менеджер вебсокетов."""
        self._client = client

    # @abstractmethod
    # def trades(self, *args, **kwargs) -> BaseSyncWebsocket:
    #     """Возвращает вебсокет для получения сделок."""

    # @abstractmethod
    # def aggtrades(self, *args, **kwargs) -> BaseSyncWebsocket:
    #     """Возвращает вебсокет для получения аггрегированных сделок."""

    @abstractmethod
    def klines(self, *args, **kwargs) -> BaseSyncWebsocket:
        """Возвращает вебсокет для получения свечей."""
