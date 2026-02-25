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
        # У Gate список пар очень большой, поэтому даем больше времени на ответ и чтение.
        client = Client(session, timeout=60, max_retries=5, retry_delay=0.5)
        currency_pairs = await client.currency_pairs()
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
            except Exception as e:
                cls._logger.error(
                    f"{type(e)} creating TickerInfoItem for element={symbol_info}: {e}"
                )

        cls._tickers_info = tickers_info

    @classmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        client = Client(session, timeout=60, max_retries=5, retry_delay=0.5)
        contracts = await client.futures_contracts("usdt")
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
            except Exception as e:
                cls._logger.error(f"{type(e)} creating TickerInfoItem for element={contract}: {e}")

        cls._futures_tickers_info = tickers_info
