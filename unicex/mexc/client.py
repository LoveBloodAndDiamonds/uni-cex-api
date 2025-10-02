__all__ = ["Client"]


import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с MEXC Spot API."""

    _BASE_SPOT_URL: str = "https://api.mexc.com"
    """Базовый URL для REST API MEXC."""

    _BASE_FUTURES_URL: str = "https://contract.mexc.com"
    """Базовый URL для фьючерсного REST API MEXC."""

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
        if not self._api_secret:
            raise NotAuthorized("API secret is required for private endpoints.")

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
        quantity: str | None = None,
        quote_order_quantity: str | None = None,
        price: str | None = None,
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
        quantity: str | None = None,
        quote_order_quantity: str | None = None,
        price: str | None = None,
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

    async def futures_funding_rate(self, symbol: str) -> dict:
        """Получение текущей ставки финансирования контракта.

        https://www.mexc.com/api-docs/futures/market-endpoints
        """
        return await self._make_request(
            "GET", self._BASE_FUTURES_URL + f"/api/v1/contract/funding_rate/{symbol}"
        )

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

    # topic: Futures Account and trading endpoints

    async def futures_account_assets(self) -> dict:
        """Получение сведений по всем валютам фьючерсного аккаунта.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_request(
            "GET",
            self._BASE_FUTURES_URL + "/api/v1/private/account/assets",
            signed=True,
        )

    async def futures_account_asset(self, currency: str) -> dict:
        """Получение баланса по одной валюте фьючерсного аккаунта.

        https://www.mexc.com/api-docs/futures/account-and-trading-endpoints
        """
        return await self._make_request(
            "GET",
            self._BASE_FUTURES_URL + f"/api/v1/private/account/asset/{currency}",
            signed=True,
        )
