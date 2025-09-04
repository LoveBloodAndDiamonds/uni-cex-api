__all__ = ["BinanceClient"]

import json
from typing import Literal

from unicex.abstract import BaseSyncClient

from .types import FuturesTimeframes, SpotTimeframes


class _BaseBinanceClient:
    """Базовый класс для клиентов Binance API."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""


class BinanceClient(BaseSyncClient, _BaseBinanceClient):
    """Клиент для работы с Binance API."""

    def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#test-connectivity
        """
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ping")

    def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api#api-description
        """
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/ping")

    def exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information
        """
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/exchangeInfo")

    def futures_exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#api-description
        """
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/exchangeInfo")

    def depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/depth", params=params)

    def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book#request-parameters
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/depth", params=params)

    def trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#recent-trades-list
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/trades", params=params)

    def futures_trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Recent-Trades-List
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/trades", params=params)

    def historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Исторические сделки.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#old-trade-lookup
        """
        params = self.filter_params({"symbol": symbol, "limit": limit, "fromId": from_id})
        return self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/historicalTrades", params=params
        )

    def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Old-Trades-Lookup
        """
        params = self.filter_params({"symbol": symbol, "limit": limit, "fromId": from_id})
        return self._make_request(
            "GET", self._BASE_FUTURES_URL + "/fapi/v1/historicalTrades", params=params
        )

    def ticker_24h(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        type: Literal["FULL", "MINI"] | None = None,
    ) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics
        """
        params = self.filter_params({"symbol": symbol, "type": type})
        if symbols is not None:
            params["symbols"] = json.dumps(symbols, separators=(",", ":"))
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ticker/24hr", params=params)

    def futures_ticker_24h(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/24hr"
        params = self.filter_params({"symbol": symbol})
        return self._make_request("GET", url, params=params)

    def ticker_price(
        self, symbol: str | None = None, symbols: list[str] | None = None
    ) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-price-ticker
        """
        params = self.filter_params({"symbol": symbol})
        if symbols is not None:
            params["symbols"] = json.dumps(symbols, separators=(",", ":"))
        url = self._BASE_SPOT_URL + "/api/v3/ticker/price"
        return self._make_request("GET", url, params=params)

    def futures_ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker-v2
        """
        params = self.filter_params({"symbol": symbol})
        return self._make_request(
            "GET", self._BASE_FUTURES_URL + "/fapi/v2/ticker/price", params=params
        )

    def open_interest(self, symbol: str) -> dict:
        """Получение открытого интереса тикера.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openInterest"
        params = {"symbol": symbol}
        return self._make_request(method="GET", url=url, params=params)

    def klines(
        self,
        symbol: str,
        interval: SpotTimeframes,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
        """
        url = self._BASE_SPOT_URL + "/api/v3/klines"
        params = self.filter_params(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "timeZone": time_zone,
                "limit": limit,
            }
        )

        return self._make_request("GET", url, params=params)

    def futures_klines(
        self,
        symbol: str,
        interval: FuturesTimeframes,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/klines"
        params = self.filter_params(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit,
            }
        )

        return self._make_request("GET", url, params=params)
