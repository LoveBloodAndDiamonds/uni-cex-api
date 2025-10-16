__all__ = ["ExchangeInfo"]


import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Binance."""

    exchange_name = "Binance"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        exchange_info = await Client(session).exchange_info()
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in exchange_info["symbols"]:
            filters = {
                flt["filterType"]: flt
                for flt in symbol_info.get("filters", [])
                if "filterType" in flt
            }
            price_filter = filters["PRICE_FILTER"]
            lot_size_filter = filters["LOT_SIZE"]
            tickers_info[symbol_info["symbol"]] = TickerInfoItem(
                tick_step=float(price_filter["tickSize"]),
                tick_precision=None,
                size_step=float(lot_size_filter["stepSize"]),
                size_precision=None,
                contract_size=1,
            )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        exchange_info = await Client(session).futures_exchange_info()
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in exchange_info["symbols"]:
            filters = {
                flt["filterType"]: flt
                for flt in symbol_info.get("filters", [])
                if "filterType" in flt
            }
            price_filter = filters["PRICE_FILTER"]
            lot_size_filter = filters["LOT_SIZE"]
            tickers_info[symbol_info["symbol"]] = TickerInfoItem(
                tick_step=float(price_filter["tickSize"]),
                tick_precision=None,
                size_step=float(lot_size_filter["stepSize"]),
                size_precision=None,
                contract_size=1,
            )

        cls._futures_tickers_info = tickers_info
