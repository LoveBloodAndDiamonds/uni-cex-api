__all__ = ["BinanceClient"]

import time
from typing import Any, Literal

from unicex.abstract import BaseSyncClient
from unicex.exceptions import MissingApiKey
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature

from .types import (
    FuturesTimeframe,
    NewOrderRespType,
    OrderType,
    SelfTradePreventionMode,
    Side,
    SpotTimeframe,
    TimeInForce,
)


class _BaseBinanceClient(BaseSyncClient):
    """Базовый класс для клиентов Binance API."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self) -> dict:
        """Возвращает заголовки для запросов к Binance API."""
        headers = {"Accept": "application/json"}
        if self._api_key:  # type: ignore
            headers["X-MBX-APIKEY"] = self._api_key  # type: ignore
        return headers

    def _make_request(
        self,
        method: RequestMethod,
        url: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Binance API с поддержкой подписи.

        Если signed=True, формируется подпись для приватных endpoint'ов:
            - Если переданы params — подпись добавляется в параметры запроса.
            - Если передан data — подпись добавляется в тело запроса.

        Если signed=False, запрос отправляется как обычный публичный, через
        базовый _make_request без обработки подписи.

        Параметры:
            method (str): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            url (str): Полный URL эндпоинта Binance API.
            signed (bool): Нужно ли подписывать запрос.
            params (dict | None): Параметры запроса для query string.
            data (dict | None): Параметры запроса для тела запроса.

        Возвращает:
            dict: Ответ в формате JSON.
        """
        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}
        data = filter_params(data) if data else {}

        # Проверяем нужно ли подписывать запрос
        if not signed:
            return super()._make_request(
                method=method,
                url=url,
                params=params,
                data=data,
            )

        # Проверяем наличие апи ключей для подписи запроса
        if not self._api_key or not self._api_secret:
            raise MissingApiKey("Api key is required to private endpoints")

        # Формируем payload
        payload = {}
        if params:
            payload.update(params)
        if data:
            payload.update(data)

        # Добавляем обязательные поля для подписи
        payload["timestamp"] = int(time.time() * 1000)
        payload["recvWindow"] = self._RECV_WINDOW

        # Генерируем строку для подписи
        query_string = dict_to_query_string(payload)
        signature = generate_hmac_sha256_signature(self._api_secret, query_string)
        payload["signature"] = signature

        # Генерируем заголовки
        headers = self._get_headers()

        if data:  # Если есть тело запроса — подпись туда
            return super()._make_request(
                method=method,
                url=url,
                data=payload,
                headers=headers,
            )
        else:  # Иначе подпись добавляем к query string
            return super()._make_request(
                method=method,
                url=url,
                params=payload,
                headers=headers,
            )


class BinanceClient(_BaseBinanceClient):
    """Клиент для работы с Binance API."""

    # ========== PUBLIC ENDPOINTS ==========

    def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#test-connectivity
        """
        url = self._BASE_SPOT_URL + "/api/v3/ping"

        return self._make_request("GET", url)

    def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ping"

        return self._make_request("GET", url)

    def exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information
        """
        url = self._BASE_SPOT_URL + "/api/v3/exchangeInfo"

        return self._make_request("GET", url)

    def futures_exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/exchangeInfo"

        return self._make_request("GET", url)

    def depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book
        """
        url = self._BASE_SPOT_URL + "/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book#request-parameters
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/depth"
        params = {"symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#recent-trades-list
        """
        url = self._BASE_SPOT_URL + "/api/v3/trades"
        params = {"symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def futures_trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Recent-Trades-List
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/trades"
        params = {"symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Исторические сделки.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#old-trade-lookup
        """
        url = self._BASE_SPOT_URL + "/api/v3/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return self._make_request("GET", url, params=params)

    def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Old-Trades-Lookup
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return self._make_request("GET", url, params=params)

    def ticker_24h(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        type: Literal["FULL", "MINI"] | None = None,
    ) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/24hr"
        params = {"symbol": symbol, "type": type, "symbols": symbols}

        return self._make_request("GET", url, params=params)

    def futures_ticker_24h(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/24hr"
        params = {"symbol": symbol}

        return self._make_request("GET", url, params=params)

    def ticker_price(
        self, symbol: str | None = None, symbols: list[str] | None = None
    ) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-price-ticker
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/price"
        params = {"symbol": symbol, "symbols": symbols}

        return self._make_request("GET", url, params=params)

    def futures_ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker-v2
        """
        url = self._BASE_FUTURES_URL + "/fapi/v2/ticker/price"
        params = {"symbol": symbol}

        return self._make_request("GET", url, params=params)

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
        interval: SpotTimeframe,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
        """
        url = self._BASE_SPOT_URL + "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "timeZone": time_zone,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def futures_klines(
        self,
        symbol: str,
        interval: FuturesTimeframe,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def futures_mark_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение ставки финансирования и цены маркировки.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/premiumIndex"
        params = {"symbol": symbol}

        return self._make_request("GET", url, params=params)

    # ========== PRIVATE ENDPOINTS ==========

    def account(self) -> dict:
        """Получение информации об аккаунте (балансы, комиссии и т.д.).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/account-endpoints#account-information-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/account"

        return self._make_request("GET", url, True)

    def futures_account(self) -> dict:
        """Получение информации об аккаунте фьючерсов.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Account-Information-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/account"
        return self._make_request("GET", url, True)

    def futures_balance(self) -> list[dict]:
        """Получение баланса фьючерсного аккаунта.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/balance"

        return self._make_request("GET", url, True)

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
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return self._make_request("GET", url, True, params=params)

    def futures_order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на фьючерсном рынке.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Cancel-Order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        data = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return self._make_request("DELETE", url, data=data)

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
        data = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
        }

        return self._make_request("DELETE", url, True, data=data)

    def order_create(
        self,
        symbol: str,
        side: Side,
        type: OrderType,
        quantity: float | None = None,
        quote_order_qty: float | None = None,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: TimeInForce | None = None,
        new_client_order_id: str | None = None,
        iceberg_qty: float | None = None,
        new_order_resp_type: NewOrderRespType | None = None,
        self_trade_prevention_mode: SelfTradePreventionMode | None = None,
    ) -> dict:
        """Создание нового ордера на спот-рынке.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#new-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        data = {
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

        return self._make_request("POST", url, True, data=data)
