__all__ = ["UserWebsocket"]

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from .._base import UserWebsocketMixin
from ..types import AccountType
from .client import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class UserWebsocket(UserWebsocketMixin):
    """Пользовательский вебсокет Binance с авто‑продлением listenKey.

    Поддержка типов аккаунта: "SPOT" и "FUTURES" (USDT‑M фьючерсы).
    """

    def __init__(
        self, callback: Callable[[Any], Awaitable[None]], client: Client, type: AccountType
    ) -> None:
        """Инициализирует асинхронный пользовательский вебсокет для работы с биржей Binance.

        Параметры:
            callback (Callable): Асинхронная функция обратного вызова, которая принимает сообщение с вебсокета.
            client (BinanceClient): Авторизованный клиент Binance.
            type (AccountType): Тип аккаунта ("SPOT" | "FUTURES").
        """
        self._callback = callback
        self._client = client
        self._type = type
