__all__ = ["Adapter"]

from typing import Any
from unicex.types import KlineDict
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с <Exchange> API."""

    @staticmethod
    def Klines_message(msg: Any) -> list[KlineDict]: ...

    @staticmethod
    def futures_klines_message(msg: Any) -> list[KlineDict]: ...

    @staticmethod
    def aggtrades_message(msg: Any) -> list[TradeDict]: ...

    @staticmethod
    def futures_aggtrades_message(msg: Any) -> list[TradeDict]: ...

    @staticmethod
    def trades_message(msg: Any) -> list[TradeDict]: ...

    @staticmethod
    def futures_trades_message(msg: Any) -> list[TradeDict]: ...
