__all__ = ["UserWebsocketMixin"]


from unicex.exceptions import NotSupported

from ..types import AccountType


class UserWebsocketMixin:
    """Миксин для пользовательского вебсокета Binance. Содержит общий функционал для работы с пользовательским WS API Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    _RENEW_INTERVAL: int = 30 * 60
    """Интервал продления listenKey (сек.)"""

    @classmethod
    def _create_ws_url(cls, type: AccountType, listen_key: str) -> str:
        """Создает URL для подключения к WebSocket."""
        if type == "FUTURES":
            return f"{cls._BASE_FUTURES_URL}/ws/{listen_key}"
        if type == "SPOT":
            return f"{cls._BASE_SPOT_URL}/ws/{listen_key}"
        raise NotSupported(f"Account type '{type}' not supported")
