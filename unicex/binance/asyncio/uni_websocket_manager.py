__all__ = ["UniWebsocketManager"]

from collections.abc import Awaitable, Callable
from logging import getLogger
from typing import Any

from unicex._abc import IUniWebsocketManager
from unicex._base.asyncio import Websocket
from unicex.enums import Exchange, Timeframe

from ..adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], Awaitable[None]]


class UniWebsocketManager(IUniWebsocketManager):
    """Унифицированный менеджер асинхронных вебсокетов Binance."""

    def __init__(self, client: Client | UniClient | None = None) -> None:
        """Инициализирует унифицированный менеджер вебсокетов."""
        if isinstance(client, UniClient):
            client = client.client
        self._websocket_manager = WebsocketManager(client)
        self._adapter = Adapter()
        self._logger = getLogger(__name__)

    def _make_wrapper(
        self, adapter_func: Callable[[dict], Any], callback: CallbackType
    ) -> CallbackType:
        """Создает обертку над callback, применяя адаптер к сырым сообщениям."""

        async def _wrapper(raw_msg: dict) -> None:
            try:
                adapted = adapter_func(raw_msg)
            except Exception as e:  # noqa: BLE001
                self._logger.error(f"Failed to adapt message: {e}")
                return
            await callback(adapted)

        return _wrapper

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает соединение для получения свечей и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> Websocket:
        """Открывает соединение фьючерсов для получения свечей и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_klines_message, callback)
        return self._websocket_manager.futures_klines(
            callback=wrapper,
            symbol=symbol,
            symbols=symbols,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore
        )

    def trades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Открывает соединение для получения сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def aggtrades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Открывает соединение для получения агрегированных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.aggtrades_message, callback)
        return self._websocket_manager.agg_trade(callback=wrapper, symbol=symbol, symbols=symbols)

    def futures_trades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Открывает соединение для получения фьючерсных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_trades_message, callback)
        return self._websocket_manager.futures_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )

    def futures_aggtrades(
        self, callback: CallbackType, symbol: str | None = None, symbols: list[str] | None = None
    ) -> Websocket:
        """Открывает соединение для получения фьючерсных агрегированных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_aggtrades_message, callback)
        return self._websocket_manager.futures_agg_trade(
            callback=wrapper, symbol=symbol, symbols=symbols
        )
