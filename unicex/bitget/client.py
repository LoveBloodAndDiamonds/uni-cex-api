__all__ = ["Client"]

import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.types import RequestMethod
from unicex.utils import (
    dict_to_query_string,
    filter_params,
    generate_hmac_sha256_signature,
    sort_params_by_alphabetical_order,
)


class Client(BaseClient):
    """Клиент для работы с Bitget API."""

    _BASE_URL: str = "https://api.bitget.com"
    """Базовый URL для REST API Bitget."""

    def _sign_message(
        self,
        method: RequestMethod,
        endpoint: str,
        params: dict[str, Any] | None,
        body: dict[str, Any] | None,
    ) -> tuple[str, str]:
        """Создает timestamp и signature для приватного запроса.

        Алгоритм:
            - формирует строку prehash из timestamp, метода, endpoint, query и body
            - подписывает строку секретным ключом (HMAC-SHA256)
            - кодирует результат в base64

        Параметры:
            method (`RequestMethod`): HTTP-метод (GET, POST и т.д.).
            endpoint (`str`): Относительный путь эндпоинта (например `/api/spot/v1/account/assets`).
            params (`dict[str, Any] | None`): Query-параметры.
            body (`dict[str, Any] | None`): Тело запроса (для POST/PUT).

        Возвращает:
            tuple:
                - `timestamp (str)`: Временная метка в миллисекундах.
                - `signature (str)`: Подпись в формате base64.
        """
        timestamp = str(int(time.time() * 1000))

        path = f"{endpoint}?{dict_to_query_string(params)}" if params else endpoint
        body_str = json.dumps(body) if body else ""
        prehash = f"{timestamp}{method}{path}{body_str}"
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            prehash,
            "base64",
        )
        return timestamp, signature

    def _get_headers(self, timestamp: str, signature: str) -> dict[str, str]:
        """Возвращает заголовки для REST-запросов Bitget.

        Параметры:
            timestamp (`str`): Временная метка.
            signature (`str`): Подпись (base64).

        Возвращает:
            `dict[str, str]`: Словарь заголовков запроса.
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._api_key:  # type: ignore[attr-defined]
            headers.update(
                {
                    "ACCESS-KEY": self._api_key,  # type: ignore[attr-defined]
                    "ACCESS-PASSPHRASE": self._api_passphrase,  # type: ignore[attr-defined]
                    "ACCESS-TIMESTAMP": timestamp,
                    "ACCESS-SIGN": signature,
                    "locale": "en-US",
                }
            )
        return headers

    def _prepare_request_params(
        self,
        *,
        method: RequestMethod,
        endpoint: str,
        signed: bool,
        params: dict[str, Any] | None,
        body: dict[str, Any] | None = None,
    ) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None, dict[str, str] | None]:
        """Готовит данные для запроса.

        Если signed=True:
            - генерирует timestamp и signature
            - добавляет авторизационные заголовки

        Если signed=False:
            - возвращает только url и переданные параметры.

        Параметры:
            method (`RequestMethod`): HTTP-метод (GET, POST и т.д.).
            endpoint (`str`): Относительный путь эндпоинта.
            signed (`bool`): Нужно ли подписывать запрос.
            params (`dict[str, Any] | None`): Query-параметры.
            body (`dict[str, Any] | None`): Тело запроса.

        Возвращает:
            tuple:
                - `url (str)`: Полный URL для запроса.
                - `params (dict | None)`: Query-параметры.
                - `body (dict | None)`: Тело запроса.
                - `headers (dict | None)`: Заголовки (если signed=True).
        """
        url = f"{self._BASE_URL}{endpoint}"

        # Предобрабатывает параметры запроса и сортирует их в соответствии с требованиями Bitget
        if params:
            params = filter_params(params)
            params = sort_params_by_alphabetical_order(params)

        headers = None
        if signed:
            timestamp, signature = self._sign_message(method, endpoint, params, body)
            headers = self._get_headers(timestamp, signature)
        return url, params, body, headers

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bitget API.

        Если `signed=True`:
            - генерирует `timestamp` и `signature`;
            - добавляет авторизационные заголовки (`ACCESS-KEY`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`, `ACCESS-SIGN`).

        Если `signed=False`:
            - выполняет публичный запрос без подписи.

        Параметры:
            method (`RequestMethod`): HTTP-метод (`"GET"`, `"POST"`, и т. п.).
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/spot/v1/market/tickers"`).
            signed (`bool`): Приватный запрос (с подписью) или публичный. По умолчанию `False`.
            params (`dict[str, Any] | None`): Query-параметры запроса.
            data (`dict[str, Any] | None`): Тело запроса для `POST/PUT`.

        Возвращает:
            `Any`: Ответ API в формате JSON (`dict` или `list`), как вернул сервер.
        """
        url, params, data, headers = self._prepare_request_params(
            method=method,
            endpoint=endpoint,
            signed=signed,
            params=params,
            body=data,
        )
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    async def request(
        self, method: RequestMethod, endpoint: str, params: dict, data: dict, signed: bool
    ) -> dict:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (`RequestMethod`): HTTP-метод (`"GET"`, `"POST"`, и т. п.).
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/spot/v1/market/tickers"`).
            signed (`bool`): Приватный запрос (с подписью) или публичный. По умолчанию `False`.
            params (`dict[str, Any] | None`): Query-параметры запроса.
            data (`dict[str, Any] | None`): Тело запроса для `POST/PUT`.


        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(
            method=method, endpoint=endpoint, params=params, data=data, signed=signed
        )

    # topic: common

    async def get_server_time(self) -> dict:
        """Получение серверного времени.

        https://www.bitget.com/api-doc/common/public/Get-Server-Time
        """
        return await self._make_request("GET", "/api/v2/public/time")

    async def get_trade_rate(
        self,
        symbol: str,
        business: str,
    ) -> dict:
        """Получение торговой ставки (комиссии) для пары.

        https://www.bitget.com/api-doc/common/public/Get-Trade-Rate
        """
        params = {"symbol": symbol, "business": business}

        return await self._make_request("GET", "/api/v2/common/trade-rate", params=params)

    async def get_business_line_all_symbol_trade_rate(
        self,
        business: str,
    ) -> dict:
        """Получение торговых ставок по всем парам для заданной линии.

        https://www.bitget.com/api-doc/common/public/Get-All-Trade-Rate
        """
        params = {"business": business}

        return await self._make_request("GET", "/api/v2/common/all-trade-rate", params=params)

    async def funding_assets(
        self,
        coin: str | None = None,
    ) -> dict:
        """Получение информации о фандинговых активах (балансах).

        https://www.bitget.com/api-doc/common/account/Funding-Assets
        """
        params = {"coin": coin}

        return await self._make_request("GET", "/api/v2/account/funding-assets", params=params)

    async def all_account_balance(self) -> dict:
        """Получение балансов по всем типам аккаунтов.

        https://www.bitget.com/api-doc/common/account/All-Account-Balance
        """
        return await self._make_request("GET", "/api/v2/account/all-account-balance")

    # topic: market

    async def get_coin_info(
        self,
        coin: str | None = None,
    ) -> dict:
        """Получение списка монет (информация по валютам).

        https://www.bitget.com/api-doc/spot/market/Get-Coin-List
        """
        params = {"coin": coin}

        return await self._make_request("GET", "/api/v2/spot/public/coins", params=params)

    async def get_symbol_info(
        self,
        symbol: str | None = None,
    ) -> dict:
        """Получение списка торговых пар / конфигураций символов.

        https://www.bitget.com/api-doc/spot/market/Get-Symbols
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/public/symbols", params=params)

    async def get_vip_fee_rate(self) -> dict:
        """Получение VIP ставок комиссии на спотовом рынке.

        https://www.bitget.com/api-doc/spot/market/Get-VIP-Fee-Rate
        """
        return await self._make_request("GET", "/api/v2/spot/market/vip-fee-rate")

    async def get_ticker_information(
        self,
        symbol: str | None = None,
    ) -> dict:
        """Получение информации по тикерам (все или конкретная пара).

        https://www.bitget.com/api-doc/spot/market/Get-Tickers
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/market/tickers", params=params)

    async def get_merge_depth(
        self,
        symbol: str,
        precision: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение объединённой книги ордеров (merge depth).

        https://www.bitget.com/api-doc/spot/market/Merge-Orderbook
        """
        params = {
            "symbol": symbol,
            "precision": precision,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v2/spot/market/merge-depth", params=params)

    async def get_orderbook_depth(
        self,
        symbol: str,
        type: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение книги ордеров (orderbook depth).

        https://www.bitget.com/api-doc/spot/market/Get-Orderbook
        """
        params = {"symbol": symbol, "type": type, "limit": limit}

        return await self._make_request("GET", "/api/v2/spot/market/orderbook", params=params)

    async def get_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение данных свечей (klines).

        https://www.bitget.com/api-doc/spot/market/Get-Candle-Data
        """
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v2/spot/market/candles", params=params)

    async def get_call_auction_information(
        self,
        symbol: str,
    ) -> dict:
        """Получение аукционной информации (если поддерживается).

        https://www.bitget.com/api-doc/spot/market/Get-Auction
        """
        params = {"symbol": symbol}

        return await self._make_request("GET", "/api/v2/spot/market/auction", params=params)

    async def get_history_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических данных свечей.

        https://www.bitget.com/api-doc/spot/market/Get-History-Candle-Data
        """
        params = {
            "symbol": symbol,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", "/api/v2/spot/market/history-candles", params=params)

    async def get_recent_trades(
        self,
        symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Получение последних совершённых сделок.

        https://www.bitget.com/api-doc/spot/market/Get-Recent-Trades
        """
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", "/api/v2/spot/market/fills", params=params)

    async def get_market_trades(
        self,
        symbol: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
    ) -> dict:
        """Получение исторических сделок на рынке.

        https://www.bitget.com/api-doc/spot/market/Get-Market-Trades
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
        }

        return await self._make_request("GET", "/api/v2/spot/market/fills-history", params=params)

    # topic: trade

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        force: str | None = None,
        price: str | None = None,
        size: str | None = None,
        client_oid: str | None = None,
        trigger_price: str | None = None,
        tpsl_type: str | None = None,
        request_time: str | None = None,
        receive_window: str | None = None,
        stp_mode: str | None = None,
        preset_take_profit_price: str | None = None,
        execute_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        execute_stop_loss_price: str | None = None,
    ) -> dict:
        """Размещение спотового ордера.

        https://www.bitget.com/api-doc/spot/trade/Place-Order
        """
        if order_type == "limit" and not force:
            raise TypeError("force is required for limit order")
        data = {
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "force": force,
            "price": price,
            "size": size,
            "clientOid": client_oid,
            "triggerPrice": trigger_price,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
            "stpMode": stp_mode,
            "presetTakeProfitPrice": preset_take_profit_price,
            "executeTakeProfitPrice": execute_take_profit_price,
            "presetStopLossPrice": preset_stop_loss_price,
            "executeStopLossPrice": execute_stop_loss_price,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/place-order", data=data, signed=True
        )

    async def cancel_an_existing_order_and_send_a_new_order(
        self,
        symbol: str,
        price: str,
        size: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_client_oid: str | None = None,
        preset_take_profit_price: str | None = None,
        execute_take_profit_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        execute_stop_loss_price: str | None = None,
    ) -> dict:
        """Отмена существующего ордера и размещение нового.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Replace-Order
        """
        data = {
            "symbol": symbol,
            "price": price,
            "size": size,
            "orderId": order_id,
            "clientOid": client_oid,
            "newClientOid": new_client_oid,
            "presetTakeProfitPrice": preset_take_profit_price,
            "executeTakeProfitPrice": execute_take_profit_price,
            "presetStopLossPrice": preset_stop_loss_price,
            "executeStopLossPrice": execute_stop_loss_price,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-replace-order", data=data, signed=True
        )

    async def batch_cancel_existing_order_and_send_new_orders(
        self,
        order_list: list[dict],
    ) -> dict:
        """Пакетная отмена существующих ордеров и размещение новых.

        https://www.bitget.com/api-doc/spot/trade/Batch-Cancel-Replace-Order
        """
        data = {"orderList": order_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-replace-order", data=data, signed=True
        )

    async def cancel_order(
        self,
        symbol: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        tpsl_type: str | None = None,
    ) -> dict:
        """Отмена спотового ордера.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Order
        """
        data = {
            "symbol": symbol,
            "orderId": order_id,
            "clientOid": client_oid,
            "tpslType": tpsl_type,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-order", data=data, signed=True
        )

    async def batch_place_orders(
        self,
        symbol: str,
        batch_mode: str | None = None,
        order_list: list[dict] | None = None,
    ) -> dict:
        """Пакетное размещение спотовых ордеров.

        https://www.bitget.com/api-doc/spot/trade/Batch-Place-Orders
        """
        if not order_list:
            raise TypeError("order_list is required")
        data = {"symbol": symbol, "orderList": order_list, "batchMode": batch_mode}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-orders", data=data, signed=True
        )

    async def batch_cancel_orders(
        self,
        symbol: str | None = None,
        batch_mode: str | None = None,
        order_list: list[dict] | None = None,
    ) -> dict:
        """Пакетная отмена спотовых ордеров.

        https://www.bitget.com/api-doc/spot/trade/Batch-Cancel-Orders
        """
        if not order_list:
            raise TypeError("order_list is required")
        data = {"symbol": symbol, "batchMode": batch_mode, "orderList": order_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-order", data=data, signed=True
        )

    async def cancel_order_by_symbol(
        self,
        symbol: str,
    ) -> dict:
        """Отмена всех открытых ордеров по символу.

        https://www.bitget.com/api-doc/spot/trade/Cancel-Symbol-Orders
        """
        data = {"symbol": symbol}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-symbol-order", data=data, signed=True
        )

    async def get_order_info(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> dict:
        """Получение информации об ордере.

        https://www.bitget.com/api-doc/spot/trade/Get-Order-Info
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        params = {
            "orderId": order_id,
            "clientOid": client_oid,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/orderInfo", params=params, signed=True
        )

    async def get_current_orders(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
        order_id: str | None = None,
        tpsl_type: str | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> dict:
        """Получение списка активных (не исполненных) ордеров.

        https://www.bitget.com/api-doc/spot/trade/Get-Unfilled-Orders
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
            "limit": limit,
            "orderId": order_id,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/unfilled-orders", params=params, signed=True
        )

    async def get_history_orders(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = None,
        order_id: str | None = None,
        tpsl_type: str | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> dict:
        """Получение истории ордеров (за последние 90 дней).

        https://www.bitget.com/api-doc/spot/trade/Get-History-Orders
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
            "limit": limit,
            "orderId": order_id,
            "tpslType": tpsl_type,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/history-orders", params=params, signed=True
        )

    async def get_fills(
        self,
        symbol: str | None = None,
        order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict:
        """Получение списка исполненных сделок (fills).

        https://www.bitget.com/api-doc/spot/trade/Get-Fills
        """
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "idLessThan": id_less_than,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/fills", params=params, signed=True
        )

    # topic: trigger

    async def place_plan_order(
        self,
        symbol: str,
        side: str,
        trigger_price: str,
        order_type: str,
        size: str | float,
        trigger_type: str,
        execute_price: str | None = None,
        plan_type: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict:
        """Размещение планового ордера (trigger / conditional order).

        https://www.bitget.com/api-doc/spot/plan/Place-Plan-Order
        """
        data = {
            "symbol": symbol,
            "side": side,
            "triggerPrice": trigger_price,
            "orderType": order_type,
            "size": size,
            "triggerType": trigger_type,
            "executePrice": execute_price,
            "planType": plan_type,
            "clientOid": client_oid,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/spot/trade/place-plan-order", data=data, signed=True
        )

    async def modify_plan_order(
        self,
        trigger_price: str,
        size: str | float,
        order_type: str,
        order_id: str | None = None,
        client_oid: str | None = None,
        execute_price: str | None = None,
    ) -> dict:
        """Изменение планового ордера (trigger order).

        https://www.bitget.com/api-doc/spot/plan/Modify-Plan-Order
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        data = {
            "orderId": order_id,
            "clientOid": client_oid,
            "triggerPrice": trigger_price,
            "executePrice": execute_price,
            "size": size,
            "orderType": order_type,
        }

        return await self._make_request("POST", "/api/v2/spot/trade/modify-plan-order", data=data)

    async def cancel_plan_order(
        self,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict:
        """Отмена планового ордера.

        https://www.bitget.com/api-doc/spot/plan/Cancel-Plan-Order
        """
        if not any([order_id, client_oid]):
            raise TypeError("either order_id or client_oid is required.")
        data = {"orderId": order_id, "clientOid": client_oid}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/cancel-plan-order", data=data, signed=True
        )

    async def get_current_plan_orders(
        self,
        symbol: str,
        limit: int | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict:
        """Получение текущих плановых (trigger) ордеров.

        https://www.bitget.com/api-doc/spot/plan/Get-Current-Plan-Order
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/current-plan-order", params=params, signed=True
        )

    async def get_plan_sub_order(
        self,
        plan_order_id: str,
    ) -> dict:
        """Получение списка суб-ордеров (исполненных частей планового ордера).

        https://www.bitget.com/api-doc/spot/plan/Get-Plan-Sub-Order
        """
        params = {"planOrderId": plan_order_id}

        return await self._make_request(
            "GET", "/api/v2/spot/trade/plan-sub-order", params=params, signed=True
        )

    async def get_history_plan_orders(
        self,
        symbol: str,
        start_time: int,
        end_time: int,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict:
        """Получение истории плановых ордеров (за период).

        https://www.bitget.com/api-doc/spot/plan/Get-History-Plan-Order
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "idLessThan": id_less_than,
        }

        return await self._make_request(
            "GET", "/api/v2/spot/trade/history-plan-order", params=params, signed=True
        )

    async def cancel_plan_orders_in_batch(
        self,
        symbol_list: list[str],
    ) -> dict:
        """Пакетная отмена плановых ордеров по списку символов.

        https://www.bitget.com/api-doc/spot/plan/Batch-Cancel-Plan-Order
        """
        data = {"symbolList": symbol_list}

        return await self._make_request(
            "POST", "/api/v2/spot/trade/batch-cancel-plan-order", data=data, signed=True
        )

    # topic: account

    async def get_account_information(self) -> dict:
        """Получение информации об аккаунте.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Info
        """
        return await self._make_request("GET", "/api/v2/spot/account/info", signed=True)

    async def get_account_assets(
        self,
        coin: str | None = None,
        asset_type: str | None = None,
    ) -> dict:
        """Получение списка активов на спотовом аккаунте.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Assets
        """
        params = {"coin": coin, "assetType": asset_type}

        return await self._make_request(
            "GET", "/api/v2/spot/account/assets", signed=True, params=params
        )

    async def get_sub_account_assets(
        self,
        id_less_than: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение списка активов на спотовом аккаунте.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Assets
        """
        params = {"idLessThan": id_less_than, "limit": limit}

        return await self._make_request(
            "GET", "/api/v2/spot/account/subaccount-assets", signed=True, params=params
        )

    async def modify_deposit_account(
        self,
        account_type: str,
        coin: str,
    ) -> dict:
        """Изменение типа авто-трансфера депозита на спотовом аккаунте.

        https://www.bitget.com/api-doc/spot/account/Modify-Deposit-Account
        """
        params = {"accountType": account_type, "coin": coin}

        return await self._make_request(
            "POST", "/api/v2/spot/wallet/modify-deposit-account", signed=True, params=params
        )

    async def get_account_billd(
        self,
        coin: str | None = None,
        group_type: str | None = None,
        businessType: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        id_less_than: str | None = None,
    ) -> dict:
        """Возвращает счета аккаунта.

        https://www.bitget.com/api-doc/spot/account/Get-Account-Bills
        """
        params = {
            "coin": coin,
            "groupType": group_type,
            "businessType": businessType,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "idLessThan": id_less_than,
        }
        return await self._make_request(
            "GET", "/api/v2/spot/account/bills", signed=True, params=params
        )

    async def transfer(
        self,
        from_type: str,
        to_type: str,
        amount: str | float,
        coin: str,
        symbol: str,
        client_oid: str | None = None,
    ) -> dict:
        """Совершает перевод между типами аккаунтов внутри биржи.

        https://www.bitget.com/api-doc/spot/account/Wallet-Transfer
        """
        params = {
            "fromType": from_type,
            "toType": to_type,
            "amount": amount,
            "coin": coin,
            "symbol": symbol,
            "clientOid": client_oid,
        }
        return await self._make_request(
            "POST", "/api/v2/spot/wallet/transfer", signed=True, params=params
        )

    async def get_transferable_coin_list(
        self,
        from_type: str,
        to_type: str,
    ) -> dict:
        """Получить список монет, которые можно переводить между аккаунтами.

        https://www.bitget.com/api-doc/spot/account/Get-Transfer-Coins
        """
        params = {
            "fromType": from_type,
            "toType": to_type,
        }
        return await self._make_request(
            "GET", "/api/v2/spot/wallet/transfer-coin-info", signed=True, params=params
        )

    async def sub_transfer(
        self,
        from_type: str,
        to_type: str,
        amount: float,
        coin: str,
        symbol: str | None = None,
        client_oid: str | None = None,
        from_user_id: str | None = None,
        to_user_id: str | None = None,
    ) -> None:
        """Перевод между саб-аккаунтами.

        https://www.bitget.com/api-doc/spot/account/Sub-Transfer
        """
        params = {
            "fromType": from_type,
            "toType": to_type,
            "amount": amount,
            "coin": coin,
            "symbol": symbol,
            "clientOid": client_oid,
            "fromUserId": from_user_id,
            "toUserId": to_user_id,
        }
        return await self._make_request(
            "POST", "/api/v2/spot/wallet/subaccount-transfer", signed=True, params=params
        )

    async def withdraw(
        self,
        coin: str,
        transfer_type: str,
        address: str,
        chain: str | None = None,
        inner_to_type: str | None = None,
        area_code: str | None = None,
        tag: str | None = None,
        size: str | float | None = None,
        remark: str | None = None,
        client_oid: str | None = None,
        member_code: str | None = None,
        identity_type: str | None = None,
        company_name: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> dict:
        """Вывод средств с аккаунта.

        https://www.bitget.com/api-doc/spot/account/Wallet-Withdrawal
        """
        params = {
            "coin": coin,
            "transferType": transfer_type,
            "address": address,
            "chain": chain,
            "innerToType": inner_to_type,
            "areaCode": area_code,
            "tag": tag,
            "size": size,
            "remark": remark,
            "clientOid": client_oid,
            "memberCode": member_code,
            "identityType": identity_type,
            "companyName": company_name,
            "firstName": first_name,
            "lastName": last_name,
        }
        return await self._make_request("POST", "/api/v2/spot/wallet/withdrawal", params=params)

    # https://www.bitget.com/api-doc/spot/account/Get-SubAccount-TransferRecords
    # https://www.bitget.com/api-doc/spot/account/Get-Account-TransferRecords
    # https://www.bitget.com/api-doc/spot/account/Switch-Deduct
    # https://www.bitget.com/api-doc/spot/account/Get-Deposit-Address
    # https://www.bitget.com/api-doc/spot/account/Get-SubAccount-Deposit-Address
    # https://www.bitget.com/api-doc/spot/account/Get-Deduct-Info
    # https://www.bitget.com/api-doc/spot/account/Cancel-Withdrawal
    # https://www.bitget.com/api-doc/spot/account/Get-SubAccount-Deposit-Record
    # https://www.bitget.com/api-doc/spot/account/Get-Withdraw-Record
    # https://www.bitget.com/api-doc/spot/account/Get-Deposit-Record
    # https://www.bitget.com/api-doc/spot/account/Upgrade_Account
    # https://www.bitget.com/api-doc/spot/account/Get_Upgrade_Status

    async def futures_vip_fee_rate(self) -> dict:
        """Получение VIP ставок комиссии на фьючерсном рынке.

        https://www.bitget.com/api-doc/contract/market/Get-VIP-Fee-Rate
        """
        return await self._make_request("GET", "/api/v2/mix/market/vip-fee-rate")

    async def futures_interest_rate_history(self, coin: str) -> dict:
        """Получение истории открытого интереса.

        https://www.bitget.com/api-doc/contract/market/Get-Interest-Rate
        """
        return await self._make_request("GET", "/api/v2/mix/market/union-interest-rate-history")

    async def futures_interest_exchange_rate(self) -> dict:
        """Получение тир листа и лимитов монет.

        https://www.bitget.com/api-doc/contract/market/Get-Exchange-Rate
        """
        return await self._make_request("GET", "/api/v2/mix/market/exchange-rate")

    async def futures_discount_rate(self) -> dict:
        """Получение списка скидок на фьючерсный рынок.

        https://www.bitget.com/api-doc/contract/market/Get-Discount-Rate
        """
        return await self._make_request("GET", "/api/v2/mix/market/discount-rate")

    async def futures_get_merge_depth(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        precision: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получить объединённые данные глубины рынка.

        https://www.bitget.com/api-doc/contract/market/Get-Merge-Depth
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "precision": precision,
            "limit": limit,
        }
        return await self._make_request("GET", "/api/v2/mix/market/merge-depth", params=params)

    async def futures_get_ticker(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить данные тикера по инструменту.

        https://www.bitget.com/api-doc/contract/market/Get-Ticker
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
        }
        return await self._make_request("GET", "/api/v2/mix/market/ticker", params=params)

    async def futures_get_all_tickers(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить данные всех тикеров по типу продукта.

        https://www.bitget.com/api-doc/contract/market/Get-All-Symbol-Ticker
        """
        params = {
            "productType": product_type,
        }
        return await self._make_request("GET", "/api/v2/mix/market/tickers", params=params)

    async def futures_get_recent_fills(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        limit: int | None = 100,
    ) -> dict:
        """Получить последние сделки по тикеру.

        https://www.bitget.com/api-doc/contract/market/Get-Recent-Fills
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "limit": limit,
        }
        return await self._make_request("GET", "/api/v2/mix/market/fills", params=params)

    async def futures_get_fills_history(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        limit: int | None = 500,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict:
        """Получить историю сделок за последние 90 дней.

        https://www.bitget.com/api-doc/contract/market/Get-Fills-History
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "limit": limit,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
        }
        return await self._make_request("GET", "/api/v2/mix/market/fills-history", params=params)

    async def futures_get_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        start_time: int | None = None,
        end_time: int | None = None,
        kline_type: str | None = "MARKET",
        limit: int | None = 100,
    ) -> dict:
        """Получить данные свечей по инструменту.

        https://www.bitget.com/api-doc/contract/market/Get-Candle-Data
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "kLineType": kline_type,
            "limit": limit,
        }
        return await self._make_request("GET", "/api/v2/mix/market/candles", params=params)

    async def futures_get_history_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить исторические свечи по инструменту.

        https://www.bitget.com/api-doc/contract/market/Get-History-Candle-Data
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }
        return await self._make_request("GET", "/api/v2/mix/market/history-candles", params=params)

    async def futures_get_history_index_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить исторические свечи по индексу контракта.

        https://www.bitget.com/api-doc/contract/market/Get-History-Index-Candle-Data
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }
        return await self._make_request(
            "GET", "/api/v2/mix/market/history-index-candles", params=params
        )

    async def futures_get_history_mark_candlestick_data(
        self,
        symbol: str,
        granularity: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить исторические свечи по mark price контракта.

        https://www.bitget.com/api-doc/contract/market/Get-History-Mark-Candle-Data
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "granularity": granularity,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }
        return await self._make_request(
            "GET", "/api/v2/mix/market/history-mark-candles", params=params
        )

    async def futures_get_open_interest(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить общий объем открытых позиций по паре.

        https://www.bitget.com/api-doc/contract/market/Get-Open-Interest
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
        }
        return await self._make_request("GET", "/api/v2/mix/market/open-interest", params=params)

    async def futures_get_next_funding_time(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить время следующего расчета контракта.

        https://www.bitget.com/api-doc/contract/market/Get-Symbol-Next-Funding-Time
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
        }
        return await self._make_request("GET", "/api/v2/mix/market/funding-time", params=params)

    async def futures_get_symbol_price(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить цены контракта (рыночную, индексную, марк).

        https://www.bitget.com/api-doc/contract/market/Get-Symbol-Price
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
        }
        return await self._make_request("GET", "/api/v2/mix/market/symbol-price", params=params)

    async def futures_get_history_funding_rate(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        page_size: int | None = None,
        page_no: int | None = None,
    ) -> dict:
        """Получить историю ставок финансирования контракта.

        https://www.bitget.com/api-doc/contract/market/Get-History-Funding-Rate
        """
        params: dict[str, str | int] = {
            "symbol": symbol,
            "productType": product_type,
        }
        if page_size is not None:
            params["pageSize"] = page_size
        if page_no is not None:
            params["pageNo"] = page_no

        return await self._make_request(
            "GET", "/api/v2/mix/market/history-fund-rate", params=params
        )

    async def futures_get_current_funding_rate(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        symbol: str | None = None,
    ) -> dict:
        """Получить текущую ставку финансирования контракта.

        https://www.bitget.com/api-doc/contract/market/Get-Current-Funding-Rate
        """
        params: dict[str, str] = {"productType": product_type}
        if symbol is not None:
            params["symbol"] = symbol

        return await self._make_request(
            "GET", "/api/v2/mix/market/current-fund-rate", params=params
        )

    async def futures_get_contract_oi_limit(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        symbol: str | None = None,
    ) -> dict:
        """Получить лимит открытого интереса контракта.

        https://www.bitget.com/api-doc/contract/market/Get-Contracts-Oi
        """
        params: dict[str, str] = {"productType": product_type}
        if symbol is not None:
            params["symbol"] = symbol

        return await self._make_request("GET", "/api/v2/mix/market/oi-limit", params=params)

    async def futures_get_contracts(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        symbol: str | None = None,
    ) -> dict:
        """Получить детали контрактов.

        https://www.bitget.com/api-doc/contract/market/Get-All-Symbols-Contracts
        """
        params: dict[str, str] = {"productType": product_type}
        if symbol is not None:
            params["symbol"] = symbol

        return await self._make_request("GET", "/api/v2/mix/market/contracts", params=params)

    # topic: futures account

    async def futures_get_single_account(
        self,
        symbol: str,
        margin_coin: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить данные по одному аккаунту фьючерсов.

        https://www.bitget.com/api-doc/contract/account/Get-Single-Account
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/account/account", signed=True, params=params
        )

    async def futures_get_account_list(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить список всех аккаунтов по типу продукта.

        https://www.bitget.com/api-doc/contract/account/Get-Account-List
        """
        params = {"productType": product_type}

        return await self._make_request(
            "GET", "/api/v2/mix/account/accounts", signed=True, params=params
        )

    async def futures_get_subaccount_assets(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить информацию о контрактах всех суб-аккаунтов.

        https://www.bitget.com/api-doc/contract/account/Get-Sub-Account-Contract-Assets
        """
        params = {"productType": product_type}

        return await self._make_request(
            "GET", "/api/v2/mix/account/sub-account-assets", signed=True, params=params
        )

    async def futures_get_interest_history(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        coin: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получить историю начисления процентов по USDT-M фьючерсам.

        https://www.bitget.com/api-doc/contract/account/Interest-History
        """
        params = {
            "productType": product_type,
            "coin": coin,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/account/interest-history", signed=True, params=params
        )

    async def futures_get_est_open_count(
        self,
        symbol: str,
        margin_coin: str,
        open_amount: float,
        open_price: float,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        leverage: int | None = 20,
    ) -> dict:
        """Получить расчетное количество открытых контрактов для пользователя.

        https://www.bitget.com/api-doc/contract/account/Est-Open-Count
        """
        params = {
            "productType": product_type,
            "symbol": symbol,
            "marginCoin": margin_coin,
            "openAmount": open_amount,
            "openPrice": open_price,
            "leverage": leverage,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/account/open-count", signed=True, params=params
        )

    async def futures_set_auto_margin(
        self,
        symbol: str,
        auto_margin: str,
        margin_coin: str,
        hold_side: str,
    ) -> dict:
        """Настроить автоматическое управление маржей для изолированной позиции.

        https://www.bitget.com/api-doc/contract/account/Set-Auto-Margin
        """
        data = {
            "symbol": symbol,
            "autoMargin": auto_margin,
            "marginCoin": margin_coin,
            "holdSide": hold_side,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-auto-margin", signed=True, data=data
        )

    async def futures_set_leverage(
        self,
        symbol: str,
        margin_coin: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        leverage: str | None = None,
        long_leverage: str | None = None,
        short_leverage: str | None = None,
        hold_side: str | None = None,
    ) -> dict:
        """Изменить плечо по указанной позиции.

        https://www.bitget.com/api-doc/contract/account/Change-Leverage
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "leverage": leverage,
            "longLeverage": long_leverage,
            "shortLeverage": short_leverage,
            "holdSide": hold_side,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-leverage", signed=True, data=data
        )

    async def futures_set_all_leverage(
        self,
        leverage: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Изменить плечо для всех позиций указанного продукта.

        https://www.bitget.com/api-doc/contract/account/Change-All-Leverage
        """
        data = {
            "productType": product_type,
            "leverage": leverage,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-all-leverage", signed=True, data=data
        )

    async def futures_adjust_margin(
        self,
        symbol: str,
        margin_coin: str,
        hold_side: str,
        amount: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Добавить или уменьшить маржу для позиции (только для изолированной маржи).

        https://www.bitget.com/api-doc/contract/account/Change-Margin
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "holdSide": hold_side,
            "amount": amount,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-margin", signed=True, data=data
        )

    async def futures_set_asset_mode(
        self,
        asset_mode: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Установить режим управления активами для USDT-M фьючерсов.

        https://www.bitget.com/api-doc/contract/account/Set-Asset-Mode
        """
        data = {
            "productType": product_type,
            "assetMode": asset_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-asset-mode", signed=True, data=data
        )

    async def futures_set_margin_mode(
        self,
        symbol: str,
        margin_coin: str,
        margin_mode: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Изменить режим маржи для позиции (изолированная/кросс).

        https://www.bitget.com/api-doc/contract/account/Change-Margin-Mode
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "marginMode": margin_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-margin-mode", signed=True, data=data
        )

    async def futures_union_convert(
        self,
        coin: str,
        amount: str,
    ) -> dict:
        """Конвертация активов в режиме объединенной маржи.

        https://www.bitget.com/api-doc/contract/account/Union-Convert
        """
        data = {"coin": coin, "amount": amount}

        return await self._make_request(
            "POST", "/api/v2/mix/account/union-convert", signed=True, data=data
        )

    async def futures_change_position_mode(
        self,
        pos_mode: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Изменить режим позиций: одинарный или хедж.

        https://www.bitget.com/api-doc/contract/account/Change-Hold-Mode
        """
        params = {
            "productType": product_type,
            "posMode": pos_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/account/set-position-mode", signed=True, params=params
        )

    async def futures_get_account_bill(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        coin: str | None = None,
        business_type: str | None = None,
        only_funding: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получить выписки по счёту за последние 90 дней.

        https://www.bitget.com/api-doc/contract/account/Get-Account-Bill
        """
        params = {
            "productType": product_type,
            "coin": coin,
            "businessType": business_type,
            "onlyFunding": only_funding,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/account/bill", signed=True, params=params
        )

    async def futures_union_transfer_limits(self, coin: str) -> dict:
        """Получить лимиты перевода для валюты union margin.

        https://www.bitget.com/api-doc/contract/account/Get-Union-Transfer-Limits
        """
        params = {"coin": coin}
        return await self._make_request(
            "GET", "/api/v2/mix/account/transfer-limits", signed=True, params=params
        )

    async def futures_union_config(self) -> dict:
        """Получить параметры конфигурации union margin.

        https://www.bitget.com/api-doc/contract/account/Get-Union-Config
        """
        return await self._make_request("GET", "/api/v2/mix/account/union-config", signed=True)

    async def futures_switch_union_usdt(self) -> dict:
        """Получить квоту USDT для переключения с union margin на single margin.

        https://www.bitget.com/api-doc/contract/account/Get-Switch-Union-USDT
        """
        return await self._make_request("GET", "/api/v2/mix/account/switch-union-usdt", signed=True)

    # topic: futures position

    async def futures_get_position_tier(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить конфигурацию уровней позиций для определённой торговой пары.

        https://www.bitget.com/api-doc/contract/position/Get-Query-Position-Lever
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/market/query-position-lever", signed=True, params=params
        )

    async def futures_get_single_position(
        self,
        symbol: str,
        margin_coin: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить информацию о позиции по одной торговой паре, включая предполагаемую цену ликвидации.

        https://www.bitget.com/api-doc/contract/position/get-single-position
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/position/single-position", signed=True, params=params
        )

    async def futures_get_all_positions(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        margin_coin: str | None = None,
    ) -> dict:
        """Получить информацию обо всех текущих позициях по типу продукта.

        https://www.bitget.com/api-doc/contract/position/get-all-position
        """
        params = {
            "productType": product_type,
            "marginCoin": margin_coin,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/position/all-position", signed=True, params=params
        )

    async def futures_get_adl_rank(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить ADL ранг по позиции аккаунта.

        https://www.bitget.com/api-doc/contract/position/Get-Position-Adl
        """
        params = {"productType": product_type}

        return await self._make_request(
            "GET", "/api/v2/mix/position/adlRank", signed=True, params=params
        )

    async def futures_get_historical_positions(
        self,
        symbol: str | None = None,
        product_type: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получить историю позиций (данные за последние 3 месяца).

        https://www.bitget.com/api-doc/contract/position/Get-History-Position
        """
        params = {
            "symbol": symbol,
            "productType": product_type,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/position/history-position", signed=True, params=params
        )

    # topic: futures trade

    async def futures_place_order(
        self,
        symbol: str,
        margin_mode: str,
        margin_coin: str,
        size: str,
        side: str,
        order_type: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        price: str | None = None,
        trade_side: str | None = None,
        force: str | None = "gtc",
        client_oid: str | None = None,
        reduce_only: str | None = "NO",
        preset_stop_surplus_price: str | None = None,
        preset_stop_loss_price: str | None = None,
        preset_stop_surplus_execute_price: str | None = None,
        preset_stop_loss_execute_price: str | None = None,
        stp_mode: str | None = "none",
    ) -> dict:
        """Разместить ордер на фьючерсном рынке.

        https://www.bitget.com/api-doc/contract/trade/Place-Order
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginMode": margin_mode,
            "marginCoin": margin_coin,
            "size": size,
            "price": price,
            "side": side,
            "tradeSide": trade_side,
            "orderType": order_type,
            "force": force,
            "clientOid": client_oid,
            "reduceOnly": reduce_only,
            "presetStopSurplusPrice": preset_stop_surplus_price,
            "presetStopLossPrice": preset_stop_loss_price,
            "presetStopSurplusExecutePrice": preset_stop_surplus_execute_price,
            "presetStopLossExecutePrice": preset_stop_loss_execute_price,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/place-order", signed=True, data=data
        )

    async def futures_reversal(
        self,
        symbol: str,
        margin_coin: str,
        side: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        size: str | None = None,
        trade_side: str | None = None,
        client_oid: str | None = None,
    ) -> dict:
        """Реверс позиции: закрыть текущую и открыть противоположную.

        https://www.bitget.com/api-doc/contract/trade/Reversal
        """
        data = {
            "symbol": symbol,
            "marginCoin": margin_coin,
            "productType": product_type,
            "size": size,
            "side": side,
            "tradeSide": trade_side,
            "clientOid": client_oid,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/click-backhand", signed=True, data=data
        )

    async def futures_batch_place_order(
        self,
        symbol: str,
        margin_mode: str,
        margin_coin: str,
        order_list: list[dict],
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Разместить пакет ордеров с поддержкой TP/SL.

        https://www.bitget.com/api-doc/contract/trade/Batch-Order
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginMode": margin_mode,
            "marginCoin": margin_coin,
            "orderList": order_list,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/batch-place-order", signed=True, data=data
        )

    async def futures_modify_order(
        self,
        symbol: str,
        margin_coin: str,
        new_client_oid: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        new_size: str | None = None,
        new_price: str | None = None,
        new_preset_stop_surplus_price: str | None = None,
        new_preset_stop_loss_price: str | None = None,
    ) -> dict:
        """Модифицировать существующий ордер: цену, размер и/или TP/SL.

        https://www.bitget.com/api-doc/contract/trade/Modify-Order
        """
        data = {
            "orderId": order_id,
            "clientOid": client_oid,
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "newClientOid": new_client_oid,
            "newSize": new_size,
            "newPrice": new_price,
            "newPresetStopSurplusPrice": new_preset_stop_surplus_price,
            "newPresetStopLossPrice": new_preset_stop_loss_price,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/modify-order", signed=True, data=data
        )

    async def futures_cancel_order(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        margin_coin: str | None = None,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict:
        """Отменить ожидающий ордер.

        https://www.bitget.com/api-doc/contract/trade/Cancel-Order
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "orderId": order_id,
            "clientOid": client_oid,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/cancel-order", signed=True, data=data
        )

    async def futures_batch_cancel_orders(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id_list: list[dict] | None = None,
        symbol: str | None = None,
        margin_coin: str | None = None,
    ) -> dict:
        """Пакетная отмена ордеров по продукту и торговой паре.

        https://www.bitget.com/api-doc/contract/trade/Batch-Cancel-Orders
        """
        data = {
            "productType": product_type,
            "orderIdList": order_id_list,
            "symbol": symbol,
            "marginCoin": margin_coin,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/batch-cancel-orders", signed=True, data=data
        )

    async def futures_flash_close_position(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        symbol: str | None = None,
        hold_side: str | None = None,
    ) -> dict:
        """Закрыть позицию по рыночной цене.

        https://www.bitget.com/api-doc/contract/trade/Flash-Close-Position
        """
        data = {
            "symbol": symbol,
            "holdSide": hold_side,
            "productType": product_type,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/close-positions", signed=True, data=data
        )

    async def futures_get_order_detail(
        self,
        symbol: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict:
        """Получить детали ордера.

        https://www.bitget.com/api-doc/contract/trade/Get-Order-Details
        """
        data = {
            "symbol": symbol,
            "productType": product_type,
            "orderId": order_id,
            "clientOid": client_oid,
        }

        return await self._make_request("GET", "/api/v2/mix/order/detail", signed=True, params=data)

    async def futures_get_order_fills(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        symbol: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить детали исполнения ордера.

        https://www.bitget.com/api-doc/contract/trade/Get-Order-Fills
        """
        params = {
            "productType": product_type,
            "orderId": order_id,
            "symbol": symbol,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/fills", signed=True, params=params
        )

    async def futures_get_fill_history(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        id_less_than: str | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить историю исполнения ордеров.

        https://www.bitget.com/api-doc/contract/trade/Get-Fill-History
        """
        params = {
            "productType": product_type,
            "orderId": order_id,
            "clientOid": client_oid,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "idLessThan": id_less_than,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/fill-history", signed=True, params=params
        )

    async def futures_get_orders_pending(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        symbol: str | None = None,
        status: str | None = None,
        id_less_than: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить все текущие ордера (pending).

        https://www.bitget.com/api-doc/contract/trade/Get-Orders-Pending
        """
        params = {
            "productType": product_type,
            "orderId": order_id,
            "clientOid": client_oid,
            "symbol": symbol,
            "status": status,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/orders-pending", signed=True, params=params
        )

    async def futures_get_orders_history(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        symbol: str | None = None,
        id_less_than: str | None = None,
        order_source: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = 100,
    ) -> dict:
        """Получить историю ордеров (до 90 дней).

        https://www.bitget.com/api-doc/contract/trade/Get-Orders-History
        """
        params = {
            "productType": product_type,
            "orderId": order_id,
            "clientOid": client_oid,
            "symbol": symbol,
            "idLessThan": id_less_than,
            "orderSource": order_source,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/orders-history", signed=True, params=params
        )

    async def futures_cancel_all_orders(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        margin_coin: str | None = None,
        request_time: int | None = None,
        receive_window: int | None = None,
    ) -> dict:
        """Отменить все ордера.

        https://www.bitget.com/api-doc/contract/trade/Cancel-All-Orders
        """
        data = {
            "productType": product_type,
            "marginCoin": margin_coin,
            "requestTime": request_time,
            "receiveWindow": receive_window,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/cancel-all-orders", signed=True, data=data
        )

    # topic: futures trigger order

    async def futures_get_plan_sub_orders(
        self,
        plan_order_id: str,
        plan_type: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
    ) -> dict:
        """Получить исполненные ордера триггерного плана.

        https://www.bitget.com/api-doc/contract/plan/Plan-Sub-Orders
        """
        params = {
            "planOrderId": plan_order_id,
            "productType": product_type,
            "planType": plan_type,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/plan-sub-order", signed=True, params=params
        )

    async def futures_place_tpsl_order(
        self,
        margin_coin: str,
        symbol: str,
        plan_type: str,
        trigger_price: str,
        hold_side: str,
        size: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        trigger_type: str | None = None,
        execute_price: str | None = None,
        range_rate: str | None = None,
        client_oid: str | None = None,
        stp_mode: str | None = None,
    ) -> dict:
        """Разместить TP/SL ордер (take-profit / stop-loss / trailing).

        https://www.bitget.com/api-doc/contract/plan/Place-Tpsl-Order
        """
        data = {
            "marginCoin": margin_coin,
            "productType": product_type,
            "symbol": symbol,
            "planType": plan_type,
            "triggerPrice": trigger_price,
            "triggerType": trigger_type,
            "executePrice": execute_price,
            "holdSide": hold_side,
            "size": size,
            "rangeRate": range_rate,
            "clientOid": client_oid,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/place-tpsl-order", signed=True, data=data
        )

    async def futures_place_pos_tpsl_order(
        self,
        margin_coin: str,
        symbol: str,
        hold_side: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        stop_surplus_trigger_price: str | None = None,
        stop_surplus_size: str | None = None,
        stop_surplus_trigger_type: str | None = None,
        stop_surplus_execute_price: str | None = None,
        stop_loss_trigger_price: str | None = None,
        stop_loss_size: str | None = None,
        stop_loss_trigger_type: str | None = None,
        stop_loss_execute_price: str | None = None,
        stp_mode: str | None = None,
        stop_surplus_client_oid: str | None = None,
        stop_loss_client_oid: str | None = None,
    ) -> dict:
        """Разместить одновременные TP/SL ордера для позиции.

        https://www.bitget.com/api-doc/contract/plan/Place-Pos-Tpsl-Order
        """
        data = {
            "marginCoin": margin_coin,
            "productType": product_type,
            "symbol": symbol,
            "holdSide": hold_side,
            "stopSurplusTriggerPrice": stop_surplus_trigger_price,
            "stopSurplusSize": stop_surplus_size,
            "stopSurplusTriggerType": stop_surplus_trigger_type,
            "stopSurplusExecutePrice": stop_surplus_execute_price,
            "stopLossTriggerPrice": stop_loss_trigger_price,
            "stopLossSize": stop_loss_size,
            "stopLossTriggerType": stop_loss_trigger_type,
            "stopLossExecutePrice": stop_loss_execute_price,
            "stpMode": stp_mode,
            "stopSurplusClientOid": stop_surplus_client_oid,
            "stopLossClientOid": stop_loss_client_oid,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/place-pos-tpsl", signed=True, data=data
        )

    async def futures_place_plan_order(
        self,
        plan_type: str,
        symbol: str,
        margin_mode: str,
        margin_coin: str,
        size: str,
        side: str,
        order_type: str,
        trigger_price: str,
        trigger_type: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        trade_side: str | None = None,
        price: str | None = None,
        callback_ratio: str | None = None,
        client_oid: str | None = None,
        reduce_only: str | None = None,
        stop_surplus_trigger_price: str | None = None,
        stop_surplus_execute_price: str | None = None,
        stop_surplus_trigger_type: str | None = None,
        stop_loss_trigger_price: str | None = None,
        stop_loss_execute_price: str | None = None,
        stop_loss_trigger_type: str | None = None,
        stp_mode: str | None = None,
    ) -> dict:
        """Разместить триггерный или трейлинг ордер с функцией TP/SL.

        https://www.bitget.com/api-doc/contract/plan/Place-Plan-Order
        """
        data = {
            "planType": plan_type,
            "symbol": symbol,
            "productType": product_type,
            "marginMode": margin_mode,
            "marginCoin": margin_coin,
            "size": size,
            "side": side,
            "orderType": order_type,
            "triggerPrice": trigger_price,
            "triggerType": trigger_type,
            "tradeSide": trade_side,
            "price": price,
            "callbackRatio": callback_ratio,
            "clientOid": client_oid,
            "reduceOnly": reduce_only,
            "stopSurplusTriggerPrice": stop_surplus_trigger_price,
            "stopSurplusExecutePrice": stop_surplus_execute_price,
            "stopSurplusTriggerType": stop_surplus_trigger_type,
            "stopLossTriggerPrice": stop_loss_trigger_price,
            "stopLossExecutePrice": stop_loss_execute_price,
            "stopLossTriggerType": stop_loss_trigger_type,
            "stpMode": stp_mode,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/place-plan-order", signed=True, data=data
        )

    async def futures_modify_tpsl_order(
        self,
        margin_coin: str,
        symbol: str,
        trigger_price: str,
        size: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        trigger_type: str | None = None,
        execute_price: str | None = None,
        range_rate: str | None = None,
    ) -> dict:
        """Изменить TP/SL ордер.

        https://www.bitget.com/api-doc/contract/plan/Modify-Tpsl-Order
        """
        data = {
            "orderId": order_id,
            "clientOid": client_oid,
            "marginCoin": margin_coin,
            "productType": product_type,
            "symbol": symbol,
            "triggerPrice": trigger_price,
            "triggerType": trigger_type,
            "executePrice": execute_price,
            "size": size,
            "rangeRate": range_rate,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/modify-tpsl-order", signed=True, data=data
        )

    async def futures_modify_plan_order(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        new_size: str | None = None,
        new_price: str | None = None,
        new_callback_ratio: str | None = None,
        new_trigger_price: str | None = None,
        new_trigger_type: str | None = None,
        new_stop_surplus_trigger_price: str | None = None,
        new_stop_surplus_execute_price: str | None = None,
        new_stop_surplus_trigger_type: str | None = None,
        new_stop_loss_trigger_price: str | None = None,
        new_stop_loss_execute_price: str | None = None,
        new_stop_loss_trigger_type: str | None = None,
    ) -> dict:
        """Изменить триггерный или трейлинг ордер, включая TP/SL.

        https://www.bitget.com/api-doc/contract/plan/Modify-Plan-Order
        """
        data = {
            "orderId": order_id,
            "clientOid": client_oid,
            "productType": product_type,
            "newSize": new_size,
            "newPrice": new_price,
            "newCallbackRatio": new_callback_ratio,
            "newTriggerPrice": new_trigger_price,
            "newTriggerType": new_trigger_type,
            "newStopSurplusTriggerPrice": new_stop_surplus_trigger_price,
            "newStopSurplusExecutePrice": new_stop_surplus_execute_price,
            "newStopSurplusTriggerType": new_stop_surplus_trigger_type,
            "newStopLossTriggerPrice": new_stop_loss_trigger_price,
            "newStopLossExecutePrice": new_stop_loss_execute_price,
            "newStopLossTriggerType": new_stop_loss_trigger_type,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/modify-plan-order", signed=True, data=data
        )

    async def futures_get_pending_plan_orders(
        self,
        plan_type: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        symbol: str | None = None,
        id_less_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получить текущие активные триггерные ордера.

        https://www.bitget.com/api-doc/contract/plan/get-orders-plan-pending
        """
        params = {
            "orderId": order_id,
            "clientOid": client_oid,
            "symbol": symbol,
            "planType": plan_type,
            "productType": product_type,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/orders-plan-pending", signed=True, params=params
        )

    async def futures_cancel_plan_orders(
        self,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id_list: list[dict[str, str]] | None = None,
        symbol: str | None = None,
        margin_coin: str | None = None,
        plan_type: str | None = None,
    ) -> dict:
        """Отменить триггерные ордера по productType, symbol и/или списку orderId.

        https://www.bitget.com/api-doc/contract/plan/Cancel-Plan-Order
        """
        data = {
            "orderIdList": order_id_list,
            "symbol": symbol,
            "productType": product_type,
            "marginCoin": margin_coin,
            "planType": plan_type,
        }

        return await self._make_request(
            "POST", "/api/v2/mix/order/cancel-plan-order", signed=True, data=data
        )

    async def futures_get_plan_orders_history(
        self,
        plan_type: str,
        product_type: Literal["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"] = "USDT-FUTURES",
        order_id: str | None = None,
        client_oid: str | None = None,
        plan_status: str | None = None,
        symbol: str | None = None,
        id_less_than: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получить историю триггерных ордеров.

        https://www.bitget.com/api-doc/contract/plan/orders-plan-history
        """
        params = {
            "orderId": order_id,
            "clientOid": client_oid,
            "planType": plan_type,
            "planStatus": plan_status,
            "symbol": symbol,
            "productType": product_type,
            "idLessThan": id_less_than,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v2/mix/order/orders-plan-history", signed=True, params=params
        )
