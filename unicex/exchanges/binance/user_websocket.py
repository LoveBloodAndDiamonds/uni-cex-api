__all__ = [
    "BinanceUserWebsocket",
    "AsyncBinanceUserWebsocket",
]

from .client import AsyncBinanceClient, BinanceClient
from .types import AccountType


class BinanceUserWebsocket:
    """Пользовательский вебсокет для работы с биржей Binance."""

    def __init__(self, client: BinanceClient, type: AccountType) -> None:
        """Инициализирует пользовательский вебсокет для работы с биржей Binance.

        Параметры:
            client (BinanceClient): Клиент для работы с биржей Binance.
            type (AccountType): Тип аккаунта (SPOT, MARGIN, FUTURES).
        """
        self._client = client
        self._type = type


class AsyncBinanceUserWebsocket:
    """Асинхронный пользовательский вебсокет для работы с биржей Binance."""

    def __init__(self, client: AsyncBinanceClient, type: AccountType) -> None:
        """Инициализирует асинхронный пользовательский вебсокет для работы с биржей Binance.

        Параметры:
            client (BinanceClient): Клиент для работы с биржей Binance.
            type (AccountType): Тип аккаунта (SPOT, MARGIN, FUTURES).
        """
        self._client = client
        self._type = type
