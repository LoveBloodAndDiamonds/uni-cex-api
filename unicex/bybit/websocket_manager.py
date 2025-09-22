import json
from collections.abc import Callable, Sequence

from unicex._abc import IWebsocketManager
from unicex.enums import MarketType, Timeframe

from .websocket import BybitWebsocket


class BybitWebsocketManager(IWebsocketManager):
    """Менеджер вебсокетов для Bybit."""

    _BASE_PUBLIC_URL: str = "wss://ws.bitget.com/v2/ws/public"
    _BASE_PRIVATE_URL: str = "wss://stream.bybit.com/v5/private"

    _DEFAULT_RUN_KWARGS = {"ping_payload": json.dumps({"req_id": "100001", "op": "ping"})}

    def klines(
        self,
        market_type: MarketType,
        callback: Callable,
        tickers: Sequence[str],
        timeframe: Timeframe,
    ) -> BybitWebsocket:
        """Возвращает вебсокет для получения свечей."""
        ws = BybitWebsocket(url=self._BASE_PUBLIC_URL, run_kwargs=self._DEFAULT_RUN_KWARGS)
        return ws
