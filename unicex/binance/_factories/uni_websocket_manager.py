# pyright: reportArgumentType=false
# Отключили pyright для строчек типа:
# ```python
# return self._websocket_cls(callback=callback, url=url)
# ```
# Потому что мы знаем, что в фабрики будем передавать только SyncWebsocket+SyncCallback, или
# AsyncWebsocket+AsyncCallback, а вот pytight допускает, что это может быть не так.

__all__ = ["UniWebsocketManagerFactory"]

from collections.abc import Awaitable, Callable
from logging import getLogger
from typing import Any, Generic, TypeVar

from unicex._abc import IUniWebsocketManager
from unicex._base import Websocket
from unicex._base.asyncio import Websocket as AsyncWebsocket
from unicex.enums import Exchange, Timeframe

from ..adapter import Adapter
from ..asyncio import Client as AsyncClient
from ..asyncio import UniClient as AsyncUniClient
from ..asyncio import WebsocketManager as AsyncWebsocketManager
from ..sync import Client, UniClient, WebsocketManager

TClient = TypeVar("TClient", Client, AsyncClient)
TUniClient = TypeVar("TUniClient", UniClient, AsyncUniClient)
TWebsocket = TypeVar("TWebsocket", Websocket, AsyncWebsocket)
TWebsocketManager = TypeVar("TWebsocketManager", WebsocketManager, AsyncWebsocketManager)
type SyncCallback = Callable[[Any], None]
type AsyncCallback = Callable[[Any], Awaitable[None]]
TCallbackType = TypeVar("TCallbackType", SyncCallback, AsyncCallback)


class UniWebsocketManagerFactory(
    Generic[TClient, TUniClient, TWebsocketManager, TWebsocket, TCallbackType],
    IUniWebsocketManager,
):
    """Фабрика унифицированного менеджера вебсокетов Binance (sync/async)."""

    def __init__(
        self,
        websocket_manager_cls: type[TWebsocketManager],
        sync: bool = True,
        client: TClient | TUniClient | None = None,
    ) -> None:
        """Инициализирует фабрику унифицированного менеджера вебсокетов."""
        if isinstance(client, UniClient | AsyncUniClient):
            self._client = client.client
        else:
            self._client = client
        self._sync = sync
        self._websocket_manager = websocket_manager_cls(self._client)  # type: ignore[call-arg]
        self._adapter = Adapter()
        self._logger = getLogger(__name__)

    def _make_wrapper(
        self, adapter_func: Callable[[dict], Any], callback: TCallbackType
    ) -> TCallbackType:
        """Создает обертку над callback, применяя адаптер к сырым сообщениям."""
        if self._sync:

            def _wrapper(raw_msg: dict) -> None:  # type: ignore[override]
                try:
                    adapted = adapter_func(raw_msg)
                except Exception as e:  # noqa: BLE001
                    self._logger.error(f"Failed to adapt message: {e}")
                    return
                callback(adapted)  # type: ignore[misc]

            return _wrapper  # type: ignore[return-value]

        else:

            async def _wrapper(raw_msg: dict) -> None:  # type: ignore[override]
                try:
                    adapted = adapter_func(raw_msg)
                except Exception as e:  # noqa: BLE001
                    self._logger.error(f"Failed to adapt message: {e}")
                    return
                await callback(adapted)  # type: ignore[misc]

            return _wrapper  # type: ignore[return-value]

    def klines(self, callback: TCallbackType, symbol: str, timeframe: Timeframe) -> TWebsocket:
        """Открывает соединение для получения свечей и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.klines_message, callback)
        return self._websocket_manager.klines(
            callback=wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore[arg-type]
        )

    def futures_klines(
        self, callback: TCallbackType, symbol: str, timeframe: Timeframe
    ) -> TWebsocket:
        """Открывает соединение фьючерсов для получения свечей и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_klines_message, callback)
        return self._websocket_manager.futures_klines(  # type: ignore[return-value]
            callback=wrapper,
            symbol=symbol,
            interval=timeframe.to_exchange_format(Exchange.BINANCE),  # type: ignore[arg-type]
        )

    def trades(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Открывает соединение для получения сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.trades_message, callback)
        return self._websocket_manager.trade(callback=wrapper, symbol=symbol)  # type: ignore[return-value]

    def aggtrades(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Открывает соединение для получения агрегированных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.aggtrades_message, callback)
        return self._websocket_manager.agg_trade(callback=wrapper, symbol=symbol)  # type: ignore[return-value]

    def futures_trades(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Открывает соединение для получения фьючерсных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_trades_message, callback)
        return self._websocket_manager.futures_trade(  # type: ignore[return-value]
            callback=wrapper, symbol=symbol
        )

    def futures_aggtrades(self, callback: TCallbackType, symbol: str) -> TWebsocket:
        """Открывает соединение для получения фьючерсных агрегированных сделок и адаптирует сообщения."""
        wrapper = self._make_wrapper(self._adapter.futures_aggtrades_message, callback)
        return self._websocket_manager.futures_agg_trade(  # type: ignore[return-value]
            callback=wrapper, symbol=symbol
        )
