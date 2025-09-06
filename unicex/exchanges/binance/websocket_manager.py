from unicex.abc import IWebsocketManager
from unicex.base import BaseSyncWebsocket
from unicex.enums import Timeframe


class BinanceWebsocketManager(IWebsocketManager):
    """Менеджер вебсокетов для Binance."""

    def klines(self, symbol: str, timeframe: Timeframe) -> BaseSyncWebsocket:
        """Возвращает вебсокет для получения свечей."""
        ...


class UniBinanceWsManager:
    """Унифицированный менеджер вебсокетов для Binance."""

    ...
