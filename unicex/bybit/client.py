__all__ = ["BybitClient"]

from typing import Literal

from unicex.abstract import BaseSyncClient

from .types import FuturesTimeframes, SpotTimeframes


class _BaseBybitClient(BaseSyncClient):
    """Базовый класс для клиентов Bybit API."""

    _BASE_URL: str = "https://api.bybit.com"
    """Базовый URL для REST API Bybit."""


class BybitClient(_BaseBybitClient):
    """Клиент для работы с Bybit API."""

    def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        return self._make_request("GET", self._BASE_URL + "/v5/market/time")

    def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        return self.ping()

    def instruments_info(
        self,
        category: Literal["spot", "linear", "inverse", "option"] = "spot",
        symbol: str | None = None,
        status: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Получение информации об инструментах торговли.

        https://bybit-exchange.github.io/docs/v5/market/instrument
        """
        params = self.filter_params(
            {
                "category": category,
                "symbol": symbol,
                "status": status,
                "baseCoin": base_coin,
                "limit": limit,
                "cursor": cursor,
            }
        )

        return self._make_request(
            "GET", self._BASE_URL + "/v5/market/instruments-info", params=params
        )

    def futures_instruments_info(
        self,
        category: Literal["linear", "inverse"] = "linear",
        symbol: str | None = None,
        status: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Получение информации об инструментах торговли.

        https://bybit-exchange.github.io/docs/v5/market/instrument
        """
        return self.instruments_info(
            category=category,
            symbol=symbol,
            status=status,
            base_coin=base_coin,
            limit=limit,
            cursor=cursor,
        )

    def tickers(
        self,
        category: Literal["spot", "linear", "inverse", "option"] = "spot",
        symbol: str | None = None,
        base_coin: str | None = None,
        exp_date: str | None = None,
    ) -> dict:
        """Получение информации о тикерах. В т.ч. статистику за 24 ч. и последнюю цену.

        https://bybit-exchange.github.io/docs/v5/market/tickers
        """
        params = self.filter_params(
            {
                "category": category,
                "symbol": symbol,
                "baseCoin": base_coin,
                "expDate": exp_date,
            }
        )

        return self._make_request("GET", self._BASE_URL + "/v5/market/tickers", params=params)

    def futures_tickers(
        self,
        category: Literal["linear", "inverse"] = "linear",
        symbol: str | None = None,
        base_coin: str | None = None,
    ) -> dict:
        """Получение информации о тикерах. В т.ч. статистику за 24 ч., ОИ и последнюю цену.

        https://bybit-exchange.github.io/docs/v5/market/tickers
        """
        return self.tickers(category=category, symbol=symbol, base_coin=base_coin)

    def klines(
        self,
        symbol: str,
        interval: SpotTimeframes,
        category: Literal["spot", "linear", "inverse"] = "spot",
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение исторических свечей.

        https://bybit-exchange.github.io/docs/v5/market/kline
        """
        params = self.filter_params(
            {
                "category": category,
                "symbol": symbol,
                "interval": interval,
                "start": start,
                "end": end,
                "limit": limit,
            }
        )

        return self._make_request("GET", self._BASE_URL + "/v5/market/kline", params=params)

    def futures_klines(
        self,
        symbol: str,
        interval: FuturesTimeframes,
        category: Literal["linear", "inverse"] = "linear",
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение исторических свечей.

        https://bybit-exchange.github.io/docs/v5/market/kline
        """
        return self.klines(
            category=category,
            symbol=symbol,
            interval=interval,
            start=start,
            end=end,
            limit=limit,
        )
