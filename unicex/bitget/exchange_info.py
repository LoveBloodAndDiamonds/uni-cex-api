__all__ = ["ExchangeInfo"]

from unicex._abc import IExchangeInfo


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Bitget."""

    @classmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        ...
