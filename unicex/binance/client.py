__all__ = ["BinanceClient"]

import hashlib
import hmac
import json
import time
from typing import Any, Literal
from urllib.parse import urlencode

from unicex.abstract import BaseSyncClient

from .types import FuturesTimeframes, SpotTimeframes


class _BaseBinanceClient:
    """Базовый класс для клиентов Binance API."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self) -> dict:
        """Возвращает заголовки для запросов к Binance API."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",  # noqa
        }
        if self._api_key:  # type: ignore
            headers["X-MBX-APIKEY"] = self._api_key  # type: ignore
        return headers

    def _hmac_signature(self, query_string: str) -> str:
        if not self._api_secret:  # type: ignore
            raise ValueError("API Secret required for private endpoints")
        m = hmac.new(
            self._api_secret.encode("utf-8"),  # type: ignore
            query_string.encode("utf-8"),
            hashlib.sha256,
        )
        return m.hexdigest()

    @staticmethod
    def encoded_string(query: dict) -> str:
        """123."""
        # todo Не работает со вложенными структурами (словари, списки)
        query = {
            k: json.dumps(v, separators=(",", ":")) if isinstance(v, list | dict) else v
            for k, v in query.items()
        }
        return urlencode(query, True)

    def _prepare_signed_request(
        self, params: dict | None = None, data: dict | None = None
    ) -> tuple[dict | None, dict | None]:
        """Подготавливает подписанный запрос добавляя timestamp и signature."""
        if not self._api_key or not self._api_secret:  # type: ignore
            raise ValueError("API Key and Secret required for signed endpoints")

        timestamp = int(time.time() * 1000)

        # Создаем копию параметров чтобы не мутировать оригинальные
        signed_params = (params or {}).copy()
        signed_data = (data or {}).copy()

        # Добавляем timestamp и recvWindow
        if signed_params:
            signed_params["timestamp"] = timestamp
            signed_params["recvWindow"] = self._RECV_WINDOW
            # Генерируем подпись для параметров
            query_string = self.encoded_string(signed_params)
            signed_params["signature"] = self._hmac_signature(query_string)
        else:
            signed_data["timestamp"] = timestamp
            signed_data["recvWindow"] = self._RECV_WINDOW
            query_string = self.encoded_string(signed_data)
            # Генерируем подпись для тела запроса
            signed_data["signature"] = self._hmac_signature(query_string)
        return signed_params, signed_data

    def _make_signed_request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет подписанный запрос к приватным эндпоинтам."""
        signed_params, signed_data = self._prepare_signed_request(params, data)
        headers = self._get_headers()

        return self._make_request(  # type: ignore
            method=method, url=url, params=signed_params, data=signed_data, headers=headers
        )


class BinanceClient(BaseSyncClient, _BaseBinanceClient):
    """Клиент для работы с Binance API."""

    # ========== PUBLIC ENDPOINTS ==========

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

    def futures_mark_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение ставки финансирования и цены маркировки.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/premiumIndex"
        params = self.filter_params({"symbol": symbol})

        return self._make_request("GET", url, params=params)

    # ========== PRIVATE ENDPOINTS (USER_DATA & TRADE) ==========

    def account(self) -> dict:
        """Получение информации об аккаунте (балансы, комиссии и т.д.).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/account-endpoints#account-information-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/account"
        return self._make_signed_request("GET", url)

    def futures_account(self) -> dict:
        """Получение информации об аккаунте фьючерсов.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Account-Information-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/account"
        return self._make_signed_request("GET", url)

    def futures_balance(self) -> list[dict]:
        """Получение баланса фьючерсного аккаунта.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/balance"
        return self._make_signed_request("GET", url)

    def all_orders(
        self,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех ордеров (активных, отмененных, исполненных) для символа.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#all-orders-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/allOrders"
        params = self.filter_params(
            {
                "symbol": symbol,
                "orderId": order_id,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit,
            }
        )
        return self._make_signed_request("GET", url, params=params)

    def futures_order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на фьючерсном рынке.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Cancel-Order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        data = self.filter_params(
            {
                "symbol": symbol,
                "orderId": order_id,
                "origClientOrderId": orig_client_order_id,
            }
        )
        return self._make_signed_request("DELETE", url, data=data)

    def order_cancel(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
    ) -> dict:
        """Отмена активного ордера на спот-рынке.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#cancel-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        data = self.filter_params(
            {
                "symbol": symbol,
                "orderId": order_id,
                "origClientOrderId": orig_client_order_id,
                "newClientOrderId": new_client_order_id,
            }
        )
        return self._make_signed_request("DELETE", url, data=data)

    def order_create(
        self,
        symbol: str,
        side: Literal["BUY", "SELL"],
        type: Literal[
            "LIMIT",
            "MARKET",
            "STOP_LOSS",
            "STOP_LOSS_LIMIT",
            "TAKE_PROFIT",
            "TAKE_PROFIT_LIMIT",
            "LIMIT_MAKER",
        ],
        quantity: float | None = None,
        quote_order_qty: float | None = None,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: Literal["GTC", "IOC", "FOK"] | None = None,
        new_client_order_id: str | None = None,
        iceberg_qty: float | None = None,
        new_order_resp_type: Literal["ACK", "RESULT", "FULL"] | None = None,
        self_trade_prevention_mode: Literal["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"]
        | None = None,
    ) -> dict:
        """Создание нового ордера на спот-рынке.

        Security: TRADE (подпись требуется)
        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#new-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        data = self.filter_params(
            {
                "symbol": symbol,
                "side": side,
                "type": type,
                "quantity": quantity,
                "quoteOrderQty": quote_order_qty,
                "price": price,
                "stopPrice": stop_price,
                "timeInForce": time_in_force,
                "newClientOrderId": new_client_order_id,
                "icebergQty": iceberg_qty,
                "newOrderRespType": new_order_resp_type,
                "selfTradePreventionMode": self_trade_prevention_mode,
            }
        )
        return self._make_signed_request("POST", url, data=data)
