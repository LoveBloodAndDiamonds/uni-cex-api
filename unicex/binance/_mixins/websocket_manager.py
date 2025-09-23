__all__ = ["WebsocketManagerMixin"]


class WebsocketManagerMixin:
    """Миксин для менеджеров вебсокетов Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""
