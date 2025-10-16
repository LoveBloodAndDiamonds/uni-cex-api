__all__ = ["ExchangeInfo"]

import aiohttp

from unicex._abc import IExchangeInfo
from unicex.types import TickerInfoItem

from .client import Client


class ExchangeInfo(IExchangeInfo):
    """Предзагружает информацию о тикерах для биржи Gateio."""

    exchange_name = "Gateio"
    """Название биржи, на которой работает класс."""

    @classmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        currency_pairs = await Client(session).currency_pairs()
        tickers_info: dict[str, TickerInfoItem] = {}
        for symbol_info in currency_pairs:
            try:
                tickers_info[symbol_info.get("id")] = TickerInfoItem(
                    tick_precision=int(symbol_info["precision"]),
                    tick_step=None,
                    size_precision=int(symbol_info["amount_precision"]),
                    size_step=None,
                    contract_size=1,
                )
            except ValueError as e:
                cls._logger.trace(
                    f"ValueError on {cls.exchange_name} by {symbol_info['symbol']}: {e}"
                )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        contracts = await Client(session).futures_contracts("usdt")
        tickers_info: dict[str, TickerInfoItem] = {}
        for contract in contracts:
            try:
                tickers_info[contract.get("name")] = TickerInfoItem(
                    tick_precision=None,
                    tick_step=float(contract["order_price_round"]),
                    size_precision=None,
                    size_step=float(contract["quanto_multiplier"]),
                    contract_size=float(contract["quanto_multiplier"]),
                )
            except ValueError as e:
                cls._logger.trace(f"ValueError on {cls.exchange_name} by {contract['name']}: {e}")

        cls._futures_tickers_info = tickers_info
