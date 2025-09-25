__all__ = ["WebsocketManager"]


from collections.abc import Awaitable, Callable, Collection
from typing import Any

from unicex._base.asyncio import Websocket

from .._mixins import WebsocketManagerMixin
from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager(WebsocketManagerMixin):
    """Менеджер асинхронных вебсокетов для Binance."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Binance.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, котоыре прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = {"ping_message": "ping", **ws_kwargs}

    def trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Collection[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Collection[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subsription_message = self._generate_subscription_message(
            topic="trade",
            market_type="SPOT",
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_URL,
            subscription_messages=[subsription_message],
            **self._ws_kwargs,
        )
