__all__ = ["Client"]


import json
import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с MEXC Spot API."""

    _BASE_SPOT_URL: str = "https://api.mexc.com"
    """Базовый URL для REST API MEXC."""

    _BASE_FUTURES_URL: str = "https://api.mexc.com"
    """Базовый URL для фьючерсного REST API MEXC (с 2026-01-19; `contract.mexc.com` — старый домен)."""

    _RECV_WINDOW: str = "5000"
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, signed: bool = False) -> dict:
        """Формирует заголовки запроса."""
        headers = {"Content-Type": "application/json"}
        if signed:
            if not self._api_key:
                raise NotAuthorized("API key is required for private endpoints.")
            headers["X-MEXC-APIKEY"] = self._api_key
        return headers

    def _generate_signature(self, payload: dict) -> str:
        """Генерирует подпись на основе данных запроса."""
        if not self.is_authorized():
            raise NotAuthorized("Api key and api secret is required to private endpoints")

        query_string = dict_to_query_string(payload)
        return generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
            "hex",
        )

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Mexc API.

        Если signed=True, формируется подпись для приватных endpoint'ов:
            - Если переданы params — подпись добавляется в параметры запроса.
            - Если передан data — подпись добавляется в тело запроса.

        Если signed=False, запрос отправляется как публичный.

        Параметры:
            method (`str`): HTTP метод ("GET", "POST", "DELETE" и т.д.).
            url (`str`): Полный URL эндпоинта Mexc API.
            params (`dict | None`): Query-параметры.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        # Фильтруем параметры
        payload = filter_params(params) if params else {}

        # Генериуем подпись, если запрос авторизованый
        if signed:
            # Генерируем подпись
            payload["timestamp"] = int(time.time() * 1000)
            payload["recvWindow"] = self._RECV_WINDOW
            payload["signature"] = self._generate_signature(payload)

        # Формируем заголовки запроса
        headers = self._get_headers(signed=signed)

        return await super()._make_request(
            method=method,
            url=url,
            params=payload,
            headers=headers,
        )

    async def _make_futures_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Выполняет приватный запрос к фьючерсному API MEXC.

        Подпись: hex(HMAC-SHA256(secret, apiKey + Request-Time + paramString)), где
        paramString — отсортированная query string для GET/DELETE и JSON-тело для POST.
        Заголовки: `ApiKey`, `Request-Time`, `Signature`, `Recv-Window`.

        Параметры:
            method (`str`): HTTP метод.
            endpoint (`str`): Путь эндпоинта (например, `/api/v1/private/order/create`).
            params (`dict | None`): Query-параметры (GET/DELETE).
            data (`dict | list | None`): Тело запроса (POST).

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        if not self.is_authorized():
            raise NotAuthorized("Api key and api secret is required to private endpoints")

        query = filter_params(params) if params else {}
        query = {k: str(v).lower() if isinstance(v, bool) else v for k, v in sorted(query.items())}
        if isinstance(data, dict):
            data = filter_params(data)
        body = json.dumps(data, separators=(",", ":")) if data is not None else ""
        param_string = body if method == "POST" else "&".join(f"{k}={v}" for k, v in query.items())

        timestamp = str(int(time.time() * 1000))
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[arg-type]
            f"{self._api_key}{timestamp}{param_string}",
            "hex",
        )
        headers = {
            "ApiKey": self._api_key,
            "Request-Time": timestamp,
            "Signature": signature,
            "Recv-Window": self._RECV_WINDOW,
            "Content-Type": "application/json",
        }
        return await BaseClient._make_request(
            self,
            method=method,
            url=self._BASE_FUTURES_URL + endpoint,
            params=query,
            data=body if method == "POST" else None,
            headers=headers,
        )

    async def request(self, method: RequestMethod, url: str, params: dict, signed: bool) -> dict:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (RequestMethod): Метод запроса (GET, POST, PUT, DELETE).
            url (str): URL эндпоинта.
            params (dict): Параметры запроса.
            signed (bool): Флаг, указывающий, требуется ли подпись запроса.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(method=method, url=url, params=params, signed=signed)

    # topic: Market
    async def ping(self) -> dict:
        """Проверка соединения с REST API.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#test-connectivity
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ping")

    async def server_time(self) -> dict:
        """Получение текущего серверного времени.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#check-server-time
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/time")

    async def default_symbols(self) -> dict:
        """Получение списка торговых пар по умолчанию.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#api-default-symbol
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/defaultSymbols")

    async def exchange_info(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> dict:
        """Получение торговых правил биржи и информации о символах.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#exchange-information
        """
        params = {
            "symbol": symbol,
            "symbols": symbols,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/exchangeInfo", params=params
        )

    async def depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение стакана цен по торговой паре.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#order-book
        """
        params = {
            "symbol": symbol,
            "limit": limit,
        }

        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/depth", params=params)

    async def trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение списка последних сделок.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#recent-trades-list
        """
        params = {
            "symbol": symbol,
            "limit": limit,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/trades", params=params
        )

    async def agg_trades(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение агрегированных сделок по символу.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#compressedaggregate-trades-list
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/aggTrades", params=params
        )

    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечных данных по торговой паре.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#klinecandlestick-data
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/klines", params=params
        )

    async def avg_price(self, symbol: str) -> dict:
        """Получение средней цены символа за последние минуты.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#current-average-price
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/avgPrice", params=params
        )

    async def ticker_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цены за 24 часа.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#24hr-ticker-price-change-statistics
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/ticker/24hr", params=params
        )

    async def ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение текущей цены символа.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-price-ticker
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/ticker/price", params=params
        )

    async def ticker_book_ticker(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лучших цен и объемов в стакане.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#symbol-order-book-ticker
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/ticker/bookTicker", params=params
        )

    async def symbol_offline(self) -> dict:
        """Получение списка делистнутых спотовых символов.

        https://www.mexc.com/api-docs/spot-v3/market-data-endpoints
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/symbol/offline")

    async def announcements(
        self, language: str | None = None, page: int | None = None, limit: int | None = None
    ) -> dict:
        """Получение объявлений биржи (`limit` — от 10, иначе ошибка 600).

        https://www.mexc.com/api-docs/spot-v3/change-log
        """
        params = {"language": language, "page": page, "limit": limit}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/announcements", params=params
        )

    # topic: Spot Account/Trade
    async def kyc_status(self) -> dict:
        """Получение статуса верификации KYC.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-kyc-status
        """
        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/kyc/status", signed=True
        )

    async def uid(self) -> dict:
        """Получение UID аккаунта.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-uid
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/uid", signed=True)

    async def self_symbols(self) -> dict:
        """Получение списка торговых пар, доступных через API аккаунта.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#user-api-default-symbol
        """
        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/selfSymbols", signed=True
        )

    async def test_order(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike | None = None,
        quote_order_quantity: NumberLike | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stp_mode: str | None = None,
    ) -> dict:
        """Проверка создания нового ордера без отправки на биржу.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#test-new-order
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "quoteOrderQty": quote_order_quantity,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/order/test", params=params, signed=True
        )

    async def create_order(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike | None = None,
        quote_order_quantity: NumberLike | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stp_mode: str | None = None,
    ) -> dict:
        """Создание нового ордера.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "quoteOrderQty": quote_order_quantity,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/order", params=params, signed=True
        )

    async def batch_orders(self, batch_orders: list[dict]) -> dict | list[dict]:
        """Создание нескольких ордеров одновременно.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#batch-orders
        """
        params = {"batchOrders": batch_orders}

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/batchOrders", params=params, signed=True
        )

    async def cancel_order(
        self,
        symbol: str,
        order_id: str | None = None,
        orig_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
    ) -> dict:
        """Отмена активного ордера.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-order
        """
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
        }

        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/order", params=params, signed=True
        )

    async def cancel_open_orders(self, symbol: str | list[str]) -> list[dict]:
        """Отмена всех открытых ордеров по символу.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#cancel-all-open-orders-on-a-symbol
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/openOrders", params=params, signed=True
        )

    async def query_order(
        self,
        symbol: str,
        order_id: str | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-order
        """
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/order", params=params, signed=True
        )

    async def open_orders(self, symbol: str | None = None) -> list[dict]:
        """Получение списка открытых ордеров.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#current-open-orders
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/openOrders", params=params, signed=True
        )

    async def all_orders(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение списка всех ордеров аккаунта по символу.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#all-orders
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/allOrders", params=params, signed=True
        )

    async def account(self) -> dict:
        """Получение информации об аккаунте.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-information
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/account", signed=True)

    async def my_trades(
        self,
        symbol: str,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение списка сделок аккаунта по символу.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#account-trade-list
        """
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/myTrades", params=params, signed=True
        )

    async def enable_mx_deduct(self, mx_deduct_enable: bool) -> dict:
        """Включение или отключение списания комиссий в MX.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#enable-mx-deduct
        """
        params = {"mxDeductEnable": mx_deduct_enable}

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/mxDeduct/enable", params=params, signed=True
        )

    async def mx_deduct_status(self) -> dict:
        """Получение статуса списания комиссий в MX.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-mx-deduct-status
        """
        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/mxDeduct/enable", signed=True
        )

    async def trade_fee(self, symbol: str) -> dict:
        """Получение комиссий по символу.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-symbol-commission
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/tradeFee", params=params, signed=True
        )

    async def create_strategy_group(self, trade_group_name: str) -> dict:
        """Создание стратегии STP.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#create-stp-strategy-group
        """
        params = {"tradeGroupName": trade_group_name}

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/strategy/group", params=params, signed=True
        )

    async def strategy_group(self, trade_group_name: str) -> dict:
        """Получение информации о стратегии STP.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#query-stp-strategy-group
        """
        params = {"tradeGroupName": trade_group_name}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/strategy/group", params=params, signed=True
        )

    async def delete_strategy_group(self, trade_group_id: str) -> dict:
        """Удаление стратегии STP.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#delete-stp-strategy-group
        """
        params = {"tradeGroupId": trade_group_id}

        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/strategy/group", params=params, signed=True
        )

    async def add_strategy_group_uid(self, uid: str | list[str], trade_group_id: str) -> dict:
        """Добавление UID в стратегию STP.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#add-uid-to-stp-strategy-group
        """
        params = {
            "uid": uid,
            "tradeGroupId": trade_group_id,
        }

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/strategy/group/uid", params=params, signed=True
        )

    async def delete_strategy_group_uid(self, uid: str | list[str], trade_group_id: str) -> dict:
        """Удаление UID из стратегии STP.

        https://www.mexc.com/api-docs/spot-v3/spot-account-trade#delete-uid-to-stp-strategy-group
        """
        params = {
            "uid": uid,
            "tradeGroupId": trade_group_id,
        }

        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/strategy/group/uid", params=params, signed=True
        )

    async def cancel_all_orders(self) -> dict:
        """Отмена всех активных ордеров по всем символам.

        https://www.mexc.com/api-docs/spot-v3/change-log
        """
        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/order/all", signed=True
        )

    async def api_key_info(self, access_key: str | None = None) -> dict:
        """Получение информации об API-ключе (права, IP whitelist, срок действия).

        https://www.mexc.com/api-docs/spot-v3/change-log
        """
        params = {"accessKey": access_key}

        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/apiKeyInfo", params=params, signed=True
        )

    async def api_key_info_update(
        self, apikey: str, ip_white_list: str | None = None, note: str | None = None
    ) -> dict:
        """Изменение IP whitelist и заметки API-ключа.

        https://www.mexc.com/api-docs/spot-v3/change-log
        """
        params = {"apikey": apikey, "ipWhiteList": ip_white_list, "note": note}

        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/apiKeyInfo", params=params, signed=True
        )

    # topic: Websocket User Data Streams

    async def create_listen_key(self) -> dict:
        """Создание listen key для пользовательского вебсокета.

        https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#generate-listen-key
        """
        return await self._make_request(
            "POST", self._BASE_SPOT_URL + "/api/v3/userDataStream", signed=True
        )

    async def listen_keys(self) -> dict:
        """Получение списка актуальных listen key.

        https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#get-valid-listen-keys
        """
        return await self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/userDataStream", signed=True
        )

    async def renew_listen_key(self, listen_key: str) -> dict:
        """Продление срока действия listen key.

        https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#extend-listen-key-validity
        """
        params = {"listenKey": listen_key}

        return await self._make_request(
            "PUT", self._BASE_SPOT_URL + "/api/v3/userDataStream", params=params, signed=True
        )

    async def close_listen_key(self, listen_key: str) -> dict:
        """Закрытие listen key для пользовательского вебсокета.

        https://www.mexc.com/api-docs/spot-v3/websocket-user-data-streams#close-listen-key
        """
        params = {"listenKey": listen_key}

        return await self._make_request(
            "DELETE", self._BASE_SPOT_URL + "/api/v3/userDataStream", params=params, signed=True
        )

    # topic: Futures Market endpoints

    async def futures_server_time(self) -> dict:
        """Получение текущего серверного времени фьючерсного API.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request("GET", self._BASE_FUTURES_URL + "/api/v1/contract/ping")

    async def futures_contract_detail(self, symbol: str | None = None) -> dict:
        """Получение информации о фьючерсных контрактах.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/detail", params=params
        )

    async def futures_support_currencies(self) -> dict:
        """Получение списка поддерживаемых для перевода валют.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/support_currencies"
        )

    async def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение данных рыночного стакана по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {"limit": limit}

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/depth/{symbol}", params=params
        )

    async def futures_depth_commits(self, symbol: str, limit: int) -> dict:
        """Получение моментального снимка стакана по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET",
            self._BASE_FUTURES_URL + f"/api/v1/contract/depth_commits/{symbol}/{limit}",
        )

    async def futures_index_price(self, symbol: str) -> dict:
        """Получение индикативной цены контракта.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/index_price/{symbol}"
        )

    async def futures_fair_price(self, symbol: str) -> dict:
        """Получение справедливой цены контракта.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/fair_price/{symbol}"
        )

    async def futures_funding_rate(self, symbol: str | None = None) -> dict:
        """Получение текущей ставки финансирования (без `symbol` — по всем контрактам).

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        path = (
            f"/api/v1/contract/funding_rate/{symbol}" if symbol else "/api/v1/contract/funding_rate"
        )
        return await self._make_request("GET", self._BASE_FUTURES_URL + path)

    async def futures_kline(
        self,
        symbol: str,
        interval: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> dict:
        """Получение свечных данных по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints#k-line-data
        """
        params = {
            "interval": interval,
            "start": start,
            "end": end,
        }

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/kline/{symbol}", params=params
        )

    async def futures_index_price_kline(
        self,
        symbol: str,
        interval: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> dict:
        """Получение свечей индикативной цены контракта.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {
            "interval": interval,
            "start": start,
            "end": end,
        }

        return await self._make_request(
            "GET",
            self._BASE_FUTURES_URL + f"/api/v1/contract/kline/index_price/{symbol}",
            params=params,
        )

    async def futures_fair_price_kline(
        self,
        symbol: str,
        interval: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> dict:
        """Получение свечей справедливой цены контракта.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {
            "interval": interval,
            "start": start,
            "end": end,
        }

        return await self._make_request(
            "GET",
            self._BASE_FUTURES_URL + f"/api/v1/contract/kline/fair_price/{symbol}",
            params=params,
        )

    async def futures_deals(self, symbol: str, limit: int | None = None) -> dict:
        """Получение последних сделок по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {"limit": limit}

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/deals/{symbol}", params=params
        )

    async def futures_ticker(self, symbol: str | None = None) -> dict:
        """Получение текущих параметров тренда по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints#get-contract-trend-data
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/ticker", params=params
        )

    async def futures_risk_reverse(self) -> dict:
        """Получение текущих балансов страхового фонда.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/risk_reverse"
        )

    async def futures_risk_reverse_history(
        self,
        symbol: str,
        page_num: int,
        page_size: int,
    ) -> dict:
        """Получение истории баланса страхового фонда по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {
            "symbol": symbol,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/risk_reverse/history", params=params
        )

    async def futures_funding_rate_history(
        self,
        symbol: str,
        page_num: int,
        page_size: int,
    ) -> dict:
        """Получение истории ставок финансирования по контракту.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        params = {
            "symbol": symbol,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/funding_rate/history", params=params
        )

    async def futures_contract_detail_country(self, symbol: str | None = None) -> dict:
        """Получение ограничений контрактов по странам (макс. плечо и т.п.).

        https://www.mexc.com/api-docs/futures/update-log
        """
        params = {"symbol": symbol}

        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + "/api/v1/contract/detail/country", params=params
        )

    # topic: Futures Account and trading endpoints

    async def futures_account_assets(self) -> dict:
        """Получение сведений по всем валютам фьючерсного аккаунта.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request("GET", "/api/v1/private/account/assets")

    async def futures_account_asset(self, currency: str) -> dict:
        """Получение баланса по одной валюте фьючерсного аккаунта.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request("GET", f"/api/v1/private/account/asset/{currency}")

    # topic: Futures trading endpoints

    async def futures_order_create(
        self,
        symbol: str,
        vol: NumberLike,
        side: int,
        type: int,
        open_type: int,
        price: NumberLike | None = None,
        leverage: int | None = None,
        position_id: int | None = None,
        external_oid: str | None = None,
        stop_loss_price: NumberLike | None = None,
        take_profit_price: NumberLike | None = None,
        loss_trend: int | None = None,
        profit_trend: int | None = None,
        price_protect: int | None = None,
        position_mode: int | None = None,
        reduce_only: bool | None = None,
        stp_mode: int | None = None,
        market_ceiling: bool | None = None,
        vol_way: int | None = None,
    ) -> dict:
        """Создание ордера на фьючерсах.

        `vol` — в контрактах (`vol_way=2` — в базовом активе). `side`: 1 открыть лонг,
        2 закрыть шорт, 3 открыть шорт, 4 закрыть лонг. `type`: 1 лимит, 2 post-only,
        3 IOC, 4 FOK, 5 рыночный, 6 рыночный→лимит. `open_type`: 1 изолированная, 2 кросс.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {
            "symbol": symbol,
            "price": price,
            "vol": vol,
            "leverage": leverage,
            "side": side,
            "type": type,
            "openType": open_type,
            "positionId": position_id,
            "externalOid": external_oid,
            "stopLossPrice": stop_loss_price,
            "takeProfitPrice": take_profit_price,
            "lossTrend": loss_trend,
            "profitTrend": profit_trend,
            "priceProtect": price_protect,
            "positionMode": position_mode,
            "reduceOnly": reduce_only,
            "stpMode": stp_mode,
            "marketCeiling": market_ceiling,
            "volWay": vol_way,
        }

        return await self._make_futures_request("POST", "/api/v1/private/order/create", data=data)

    async def futures_orders_create_batch(self, orders: list[dict]) -> dict:
        """Пакетное создание ордеров на фьючерсах (поля — как в `futures_order_create`, camelCase).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = [filter_params(order) for order in orders]

        return await self._make_futures_request(
            "POST", "/api/v1/private/order/submit_batch", data=data
        )

    async def futures_order_cancel(self, order_ids: list[int | str]) -> dict:
        """Отмена ордеров по ID (до 50 за запрос).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request(
            "POST", "/api/v1/private/order/cancel", data=list(order_ids)
        )

    async def futures_order_cancel_with_external(self, symbol: str, external_oid: str) -> dict:
        """Отмена ордера по внешнему ID.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {"symbol": symbol, "externalOid": external_oid}

        return await self._make_futures_request(
            "POST", "/api/v1/private/order/cancel_with_external", data=data
        )

    async def futures_orders_cancel_all(self, symbol: str | None = None) -> dict:
        """Отмена всех ордеров (по символу или всех).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {"symbol": symbol}

        return await self._make_futures_request(
            "POST", "/api/v1/private/order/cancel_all", data=data
        )

    async def futures_order_change_limit(
        self, order_id: int | str, price: NumberLike, vol: NumberLike
    ) -> dict:
        """Изменение цены и объёма лимитного ордера.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {"orderId": order_id, "price": price, "vol": vol}

        return await self._make_futures_request(
            "POST", "/api/v1/private/order/change_limit_order", data=data
        )

    async def futures_order_get(self, order_id: int | str) -> dict:
        """Получение ордера по ID.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request("GET", f"/api/v1/private/order/get/{order_id}")

    async def futures_order_get_external(self, symbol: str, external_oid: str) -> dict:
        """Получение ордера по внешнему ID.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request(
            "GET", f"/api/v1/private/order/external/{symbol}/{external_oid}"
        )

    async def futures_orders_batch_query(self, order_ids: list[int | str]) -> dict:
        """Получение ордеров по списку ID (до 50).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {"order_ids": ",".join(map(str, order_ids))}

        return await self._make_futures_request(
            "GET", "/api/v1/private/order/batch_query", params=params
        )

    async def futures_orders_open(
        self, symbol: str | None = None, page_num: int | None = None, page_size: int | None = None
    ) -> dict:
        """Получение активных ордеров (с 2025-12-02 вместо `order/open_orders`).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        path = "/api/v1/private/order/list/open_orders"
        if symbol:
            path += f"/{symbol}"
        params = {"page_num": page_num, "page_size": page_size}

        return await self._make_futures_request("GET", path, params=params)

    async def futures_orders_history(
        self,
        symbol: str | None = None,
        states: str | None = None,
        category: str | None = None,
        side: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        """Получение истории ордеров.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {
            "symbol": symbol,
            "states": states,
            "category": category,
            "side": side,
            "start_time": start_time,
            "end_time": end_time,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_futures_request(
            "GET", "/api/v1/private/order/list/history_orders", params=params
        )

    async def futures_order_deals(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        """Получение истории исполнений (сделок) по ордерам.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {
            "symbol": symbol,
            "start_time": start_time,
            "end_time": end_time,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_futures_request(
            "GET", "/api/v1/private/order/list/order_deals/v3", params=params
        )

    async def futures_order_deal_details(self, order_id: int | str) -> dict:
        """Получение исполнений по ордеру.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request(
            "GET", f"/api/v1/private/order/deal_details/{order_id}"
        )

    async def futures_open_order_total_count(self) -> dict:
        """Получение количества активных ордеров.

        https://www.mexc.com/api-docs/futures/update-log
        """
        return await self._make_futures_request(
            "GET", "/api/v1/private/order/open_order_total_count"
        )

    async def futures_positions_open(
        self, symbol: str | None = None, position_id: int | None = None
    ) -> dict:
        """Получение открытых позиций.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {"symbol": symbol, "positionId": position_id}

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/open_positions", params=params
        )

    async def futures_positions_history(
        self,
        symbol: str | None = None,
        type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        """Получение истории позиций.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {
            "symbol": symbol,
            "type": type,
            "start_time": start_time,
            "end_time": end_time,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/list/history_positions", params=params
        )

    async def futures_funding_records(
        self,
        symbol: str | None = None,
        position_id: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> dict:
        """Получение истории списаний фандинга.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {
            "symbol": symbol,
            "position_id": position_id,
            "page_num": page_num,
            "page_size": page_size,
        }

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/funding_records", params=params
        )

    async def futures_leverage(self, symbol: str) -> dict:
        """Получение плеча по контракту.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {"symbol": symbol}

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/leverage", params=params
        )

    async def futures_change_leverage(
        self,
        leverage: int,
        position_id: int | None = None,
        open_type: int | None = None,
        symbol: str | None = None,
        position_type: int | None = None,
    ) -> dict:
        """Изменение плеча (по позиции или по символу с `open_type`/`position_type`).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {
            "positionId": position_id,
            "leverage": leverage,
            "openType": open_type,
            "symbol": symbol,
            "positionType": position_type,
        }

        return await self._make_futures_request(
            "POST", "/api/v1/private/position/change_leverage", data=data
        )

    async def futures_position_mode(self) -> dict:
        """Получение режима позиций (1 hedge, 2 one-way).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request("GET", "/api/v1/private/position/position_mode")

    async def futures_change_position_mode(self, position_mode: int) -> dict:
        """Изменение режима позиций (1 hedge, 2 one-way).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {"positionMode": position_mode}

        return await self._make_futures_request(
            "POST", "/api/v1/private/position/change_position_mode", data=data
        )

    async def futures_change_margin(self, position_id: int, amount: NumberLike, type: str) -> dict:
        """Изменение маржи позиции (`type`: ADD / SUB).

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        data = {"positionId": position_id, "amount": amount, "type": type}

        return await self._make_futures_request(
            "POST", "/api/v1/private/position/change_margin", data=data
        )

    async def futures_close_all_positions(self) -> dict:
        """Закрытие всех открытых позиций.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_futures_request("POST", "/api/v1/private/position/close_all")

    async def futures_change_multi_asset_mode(self, is_multi_asset_mode: bool) -> dict:
        """Включение/выключение мультиактивного режима.

        https://www.mexc.com/api-docs/futures/update-log
        """
        flag = "true" if is_multi_asset_mode else "false"
        return await self._make_futures_request(
            "POST", f"/api/v1/private/multiAssets/changeMultiAssetMode/{flag}"
        )

    async def futures_subaccount_leverage(self, sub_account: str, symbol: str) -> dict:
        """Получение плеча субаккаунта по контракту.

        https://www.mexc.com/api-docs/futures/update-log
        """
        params = {"subAccount": sub_account, "symbol": symbol}

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/leverage/subaccount", params=params
        )

    async def futures_subaccount_position_mode(self, sub_account: str) -> dict:
        """Получение режима позиций субаккаунта.

        https://www.mexc.com/api-docs/futures/update-log
        """
        params = {"subAccount": sub_account}

        return await self._make_futures_request(
            "GET", "/api/v1/private/position/position_mode/subaccount", params=params
        )

    async def futures_tiered_fee_rate(self, symbol: str | None = None) -> dict:
        """Получение ступенчатых комиссий.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        params = {"symbol": symbol}

        return await self._make_futures_request(
            "GET", "/api/v1/private/account/tiered_fee_rate/v2", params=params
        )
