__all__ = ["IUniWebsocketManager"]

from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex.enums import Exchange, Timeframe
from unicex.types import LoggerLike

from .adapter import Adapter
from .client import Client
from .uni_client import UniClient
from .websocket_manager import WebsocketManager

type CallbackType = Callable[[Any], Awaitable[None]]


class UniWebsocketManager(IUniWebsocketManager):
    """Реализация менеджера асинхронных унифицированных вебсокетов."""

    def __init__(
        self,
        client: Client | UniClient | None = None,
        logger: LoggerLike | None = None,
        **ws_kwargs: Any,
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (`Client | UniClient | None`): Клиент Bybit или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
            ws_kwargs (`dict[str, Any]`): Дополнительные параметры инициализации, которые будут переданы WebsocketManager/Websocket.
        """
        super().__init__(client=client, logger=logger)
        self._websocket_manager = WebsocketManager(self._client, **ws_kwargs)  # type: ignore
        self._adapter = Adapter()

    def _is_service_message(self, raw_msg: Any) -> bool:
        if raw_msg.get("op") == "subscribe":
            return True
        return False

    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.kline(
            callback=self._make_wrapper(self._adapter.Klines_message, callback),
            category="spot",
            interval=timeframe.to_exchange_format(Exchange.BYBIT),  # type: ignore
            symbol=symbol,
            symbols=symbols,
        )

    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.kline(
            callback=self._make_wrapper(self._adapter.Klines_message, callback),
            category="linear",
            interval=timeframe.to_exchange_format(Exchange.BYBIT),  # type: ignore
            symbol=symbol,
            symbols=symbols,
        )

    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.trade(
            callback=self._make_wrapper(self._adapter.trades_message, callback),
            category="spot",
            symbol=symbol,
            symbols=symbols,
        )

    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self.trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore

    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.trade(
            callback=self._make_wrapper(self._adapter.trades_message, callback),
            category="linear",
            symbol=symbol,
            symbols=symbols,
        )

    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self.futures_trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore

    def liquidations(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.all_liquidation(
            callback=self._make_wrapper(self._adapter.liquidations_message, callback),
            category="linear",
            symbol=symbol,
            symbols=symbols,
        )

    def futures_best_bid_ask(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        return self._websocket_manager.orderbook(
            callback=self._make_wrapper(self._adapter.best_bid_ask_message, callback),
            category="linear",
            depth=1,
            symbol=symbol,
            symbols=symbols,
        )

    def futures_partial_book_depth(
        self,
        callback: CallbackType,
        limit: int,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        allowed_levels = {1, 50, 200, 1000}
        if limit not in allowed_levels:
            raise ValueError("Parameter `limit` must be one of: 1, 50, 200, 1000")

        wrapped_adapter = self._adapter.partial_book_depth_message()

        return self._websocket_manager.orderbook(
            callback=self._make_wrapper(wrapped_adapter, callback),
            category="linear",
            depth=limit,  # type: ignore
            symbol=symbol,
            symbols=symbols,
        )
