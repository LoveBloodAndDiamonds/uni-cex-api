__all__ = ["Client"]

import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Bybit API."""

    _BASE_URL: str = "https://api.bybit.com"
    """Базовый URL для REST API Bybit."""

    _RECV_WINDOW: str = "5000"
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, timestamp: str, signature: str | None = None) -> dict:
        """Возвращает заголовки для запросов к Bybit API.

        Параметры:
            timestamp (str): Временная метка запроса в миллисекундах.
            signature (str | None): Подпись запроса, если запрос авторизированый.
        """
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if signature:
            headers["X-BAPI-API-KEY"] = self._api_key  # type: ignore
            headers["X-BAPI-SIGN-TYPE"] = "2"
            headers["X-BAPI-SIGN"] = signature
            headers["X-BAPI-RECV-WINDOW"] = self._RECV_WINDOW
            headers["X-BAPI-TIMESTAMP"] = timestamp
        return headers

    def _generate_signature(self, timestamp: str, payload: dict) -> str:
        """Генерация подписи.

        Источник: https://github.com/bybit-exchange/api-usage-examples/blob/master/V5_demo/api_demo/Encryption_HMAC.py
        """
        # Проверяем наличие апи ключей для подписи запроса
        if not self._api_key or not self._api_secret:
            raise NotAuthorized("API key and secret are required to private endpoints.")

        dumped_payload = json.dumps(payload)
        prepared_query_string = timestamp + self._api_key + self._RECV_WINDOW + dumped_payload
        return generate_hmac_sha256_signature(self._api_secret, prepared_query_string)

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bybit API с поддержкой подписи.

        Если signed=True, формируется подпись для приватных endpoint'ов.
        Если signed=False, запрос отправляется как обычный публичный, через
        базовый _make_request без обработки подписи.

        Параметры:
            method (str): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            endpoint (str): URL эндпоинта Bybit API.
            params (dict | None): Параметры запроса. Передаются в body, если запрос типа "POST", иначе в query_params
            signed (bool): Нужно ли подписывать запрос.

        Возвращает:
            dict: Ответ в формате JSON.
        """
        # Составляем URL для запроса
        url = self._BASE_URL + endpoint

        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}

        # Генерируем временную метку
        timestamp = str(int(time.time() * 1000))

        # Проверяем нужно ли подписывать запрос
        if not signed:
            headers = self._get_headers(timestamp)
            return await super()._make_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            )

        # Формируем payload
        payload = params

        # Генерируем строку для подписи
        signature = self._generate_signature(timestamp, payload)

        # Генерируем заголовки (вкл. в себя подпись и апи ключ)
        headers = self._get_headers(timestamp, signature)

        if method == "POST":  # Отправляем параметры в тело запроса
            return await super()._make_request(
                method=method,
                url=url,
                data=payload,
                headers=headers,
            )
        else:  # Иначе параметры добавляем к query string
            return await super()._make_request(
                method=method,
                url=url,
                params=payload,
                headers=headers,
            )

    async def request(
        self, method: RequestMethod, endpoint: str, params: dict, signed: bool
    ) -> dict:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (RequestMethod): Метод запроса (GET, POST, PUT, DELETE).
            endpoint (str): URL эндпоинта.
            params (dict): Параметры запроса.
            signed (bool): Флаг, указывающий, требуется ли подпись запроса.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(
            method=method, endpoint=endpoint, params=params, signed=signed
        )

    # topic: market

    async def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        return await self._make_request("GET", "/v5/market/time")

    async def klines(
        self,
        symbol: str,
        interval: str,
        category: Literal["spot", "linear", "inverse"],
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи.

        https://bybit-exchange.github.io/docs/v5/market/kline
        """
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/kline", params=params)

    async def mark_price_klines(
        self,
        symbol: str,
        interval: str,
        category: Literal["linear", "inverse"] | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи цены маркировки (mark price).

        https://bybit-exchange.github.io/docs/v5/market/mark-kline
        """
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/mark-price-kline", params=params)

    async def index_price_klines(
        self,
        symbol: str,
        interval: str,
        category: Literal["linear", "inverse"] | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи индекса (index price).

        https://bybit-exchange.github.io/docs/v5/market/index-kline
        """
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/index-price-kline", params=params)

    async def premium_index_price_klines(
        self,
        symbol: str,
        interval: str,
        category: Literal["linear"] | None = None,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи премиального индекса (premium index).

        https://bybit-exchange.github.io/docs/v5/market/premium-index-kline
        """
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/v5/market/premium-index-price-kline", params=params
        )

    async def instruments_info(
        self,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        status: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Информация об инструментах.

        https://bybit-exchange.github.io/docs/v5/market/instrument
        """
        params = {
            "category": category,
            "symbol": symbol,
            "status": status,
            "baseCoin": base_coin,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/market/instruments-info", params=params)

    async def orderbook(
        self,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Книга ордеров (глубина рынка).

        https://bybit-exchange.github.io/docs/v5/market/orderbook
        """
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/orderbook", params=params)

    async def rpi_orderbook(
        self,
        symbol: str,
        limit: int,
        category: Literal["spot", "linear", "inverse"] | None = None,
    ) -> dict:
        """Книга ордеров RPI.

        https://bybit-exchange.github.io/docs/v5/market/rpi-orderbook
        """
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/rpi_orderbook", params=params)

    async def tickers(
        self,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        exp_date: str | None = None,
    ) -> dict:
        """Тикеры (снимок цен и объёмов).

        https://bybit-exchange.github.io/docs/v5/market/tickers
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "expDate": exp_date,
        }

        return await self._make_request("GET", "/v5/market/tickers", params=params)

    async def funding_rate_history(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """История ставок финансирования.

        https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
        """
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/funding/history", params=params)

    async def recent_trades(
        self,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        option_type: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Недавние публичные сделки.

        https://bybit-exchange.github.io/docs/v5/market/recent-trade
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "optionType": option_type,
            "limit": limit,
        }

        return await self._make_request("GET", "/v5/market/recent-trade", params=params)

    async def open_interest(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        interval_time: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Открытый интерес по символу.

        https://bybit-exchange.github.io/docs/v5/market/open-interest
        """
        params = {
            "category": category,
            "symbol": symbol,
            "intervalTime": interval_time,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/market/open-interest", params=params)

    async def historical_volatility(
        self,
        category: Literal["option"],
        base_coin: str | None = None,
        quote_coin: str | None = None,
        period: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict:
        """Историческая волатильность (опционы).

        https://bybit-exchange.github.io/docs/v5/market/iv
        """
        params = {
            "category": category,
            "baseCoin": base_coin,
            "quoteCoin": quote_coin,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._make_request("GET", "/v5/market/historical-volatility", params=params)

    async def insurance_pool(
        self,
        coin: str | None = None,
    ) -> dict:
        """Данные страхового пула.

        https://bybit-exchange.github.io/docs/v5/market/insurance
        """
        params = {
            "coin": coin,
        }

        return await self._make_request("GET", "/v5/market/insurance", params=params)

    async def risk_limit(
        self,
        category: Literal["linear", "inverse"],
        symbol: str | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Параметры лимита риска.

        https://bybit-exchange.github.io/docs/v5/market/risk-limit
        """
        params = {
            "category": category,
            "symbol": symbol,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/market/risk-limit", params=params)

    async def delivery_price(
        self,
        category: Literal["linear", "inverse", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Цена поставки (delivery price).

        https://bybit-exchange.github.io/docs/v5/market/delivery-price
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/market/delivery-price", params=params)

    async def new_delivery_price(
        self,
        category: Literal["option"],
        base_coin: str,
        settle_coin: str | None = None,
    ) -> dict:
        """Исторические цены поставки (опционы).

        https://bybit-exchange.github.io/docs/v5/market/new-delivery-price
        """
        params = {
            "category": category,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
        }

        return await self._make_request("GET", "/v5/market/new-delivery-price", params=params)

    async def long_short_ratio(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Лонг/шорт соотношение.

        https://bybit-exchange.github.io/docs/v5/market/long-short-ratio
        """
        params = {
            "category": category,
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/market/account-ratio", params=params)

    async def index_price_components(
        self,
        index_name: str,
    ) -> dict:
        """Компоненты индексной цены.

        https://bybit-exchange.github.io/docs/v5/market/index-components
        """
        params = {
            "indexName": index_name,
        }

        return await self._make_request("GET", "/v5/market/index-price-components", params=params)

    async def order_price_limit(
        self,
        symbol: str,
        category: Literal["spot", "linear", "inverse"] | None = None,
    ) -> dict:
        """Лимиты цен для ордеров.

        https://bybit-exchange.github.io/docs/v5/market/order-price-limit
        """
        params = {
            "category": category,
            "symbol": symbol,
        }

        return await self._make_request("GET", "/v5/market/price-limit", params=params)

    async def adl_alert(
        self,
        symbol: str | None = None,
    ) -> dict:
        """Уведомления ADL и информация страхового пула.

        https://bybit-exchange.github.io/docs/v5/market/adl-alert
        """
        params = {
            "symbol": symbol,
        }

        return await self._make_request("GET", "/v5/market/adlAlert", params=params)

    async def fee_group_info(
        self,
        product_type: Literal["contract"],
        group_id: str | None = None,
    ) -> dict:
        """Структура групп комиссий и ставки.

        https://bybit-exchange.github.io/docs/v5/market/fee-group-info
        """
        params = {
            "productType": product_type,
            "groupId": group_id,
        }

        return await self._make_request("GET", "/v5/market/fee-group-info", params=params)

    # topic: trade

    async def create_order(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        is_leverage: int | None = None,
        market_unit: str | None = None,
        slippage_tolerance_type: str | None = None,
        slippage_tolerance: str | None = None,
        price: str | None = None,
        trigger_direction: int | None = None,
        order_filter: str | None = None,
        trigger_price: str | None = None,
        trigger_by: str | None = None,
        order_iv: str | None = None,
        time_in_force: str | None = None,
        position_idx: int | None = None,
        order_link_id: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        reduce_only: bool | None = None,
        close_on_trigger: bool | None = None,
        smp_type: str | None = None,
        mmp: bool | None = None,
        tpsl_mode: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
    ) -> dict:
        """Создание ордера.

        https://bybit-exchange.github.io/docs/v5/order/create-order
        """
        params = {
            "category": category,
            "symbol": symbol,
            "isLeverage": is_leverage,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "marketUnit": market_unit,
            "slippageToleranceType": slippage_tolerance_type,
            "slippageTolerance": slippage_tolerance,
            "price": price,
            "triggerDirection": trigger_direction,
            "orderFilter": order_filter,
            "triggerPrice": trigger_price,
            "triggerBy": trigger_by,
            "orderIv": order_iv,
            "timeInForce": time_in_force,
            "positionIdx": position_idx,
            "orderLinkId": order_link_id,
            "takeProfit": take_profit,
            "stopLoss": stop_loss,
            "tpTriggerBy": tp_trigger_by,
            "slTriggerBy": sl_trigger_by,
            "reduceOnly": reduce_only,
            "closeOnTrigger": close_on_trigger,
            "smpType": smp_type,
            "mmp": mmp,
            "tpslMode": tpsl_mode,
            "tpLimitPrice": tp_limit_price,
            "slLimitPrice": sl_limit_price,
            "tpOrderType": tp_order_type,
            "slOrderType": sl_order_type,
        }

        return await self._make_request("POST", "/v5/order/create", params=params, signed=True)

    async def amend_order(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_iv: str | None = None,
        trigger_price: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        tpsl_mode: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        trigger_by: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
    ) -> dict:
        """Изменение параметров ордера.

        https://bybit-exchange.github.io/docs/v5/order/amend-order
        """
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "orderIv": order_iv,
            "triggerPrice": trigger_price,
            "qty": qty,
            "price": price,
            "tpslMode": tpsl_mode,
            "takeProfit": take_profit,
            "stopLoss": stop_loss,
            "tpTriggerBy": tp_trigger_by,
            "slTriggerBy": sl_trigger_by,
            "triggerBy": trigger_by,
            "tpLimitPrice": tp_limit_price,
            "slLimitPrice": sl_limit_price,
        }

        return await self._make_request("POST", "/v5/order/amend", params=params, signed=True)

    async def cancel_order(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_filter: str | None = None,
    ) -> dict:
        """Отмена ордера.

        https://bybit-exchange.github.io/docs/v5/order/cancel-order
        """
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "orderFilter": order_filter,
        }

        return await self._make_request("POST", "/v5/order/cancel", params=params, signed=True)

    async def open_orders(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        open_only: int | None = None,
        order_filter: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Открытые и закрытые ордера (реaltime).

        https://bybit-exchange.github.io/docs/v5/order/open-order
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "openOnly": open_only,
            "orderFilter": order_filter,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/order/realtime", params=params, signed=True)

    async def cancel_all_orders(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        order_filter: str | None = None,
        stop_order_type: str | None = None,
    ) -> dict:
        """Отмена всех открытых ордеров.

        https://bybit-exchange.github.io/docs/v5/order/cancel-all
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderFilter": order_filter,
            "stopOrderType": stop_order_type,
        }

        return await self._make_request("POST", "/v5/order/cancel-all", params=params, signed=True)

    async def order_history(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_filter: str | None = None,
        order_status: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История ордеров.

        https://bybit-exchange.github.io/docs/v5/order/order-list
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "orderFilter": order_filter,
            "orderStatus": order_status,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/order/history", params=params, signed=True)

    async def trade_history(
        self,
        category: Literal["linear", "inverse", "spot", "option"],
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        base_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        exec_type: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История сделок (execution list).

        https://bybit-exchange.github.io/docs/v5/order/execution
        """
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "baseCoin": base_coin,
            "startTime": start_time,
            "endTime": end_time,
            "execType": exec_type,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/execution/list", params=params, signed=True)

    async def create_orders_batch(
        self,
        category: Literal["linear", "option", "spot", "inverse"],
        request: list[dict[str, Any]],
    ) -> dict:
        """Массовое создание ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-place
        """
        params = {
            "category": category,
            "request": request,
        }

        return await self._make_request(
            "POST", "/v5/order/create-batch", params=params, signed=True
        )

    async def amend_orders_batch(
        self,
        category: Literal["linear", "option", "spot", "inverse"],
        request: list[dict[str, Any]],
    ) -> dict:
        """Массовое изменение ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-amend
        """
        params = {
            "category": category,
            "request": request,
        }

        return await self._make_request("POST", "/v5/order/amend-batch", params=params, signed=True)

    async def cancel_orders_batch(
        self,
        category: Literal["linear", "option", "spot", "inverse"],
        request: list[dict[str, Any]],
    ) -> dict:
        """Массовая отмена ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-cancel
        """
        params = {
            "category": category,
            "request": request,
        }

        return await self._make_request(
            "POST", "/v5/order/cancel-batch", params=params, signed=True
        )

    async def spot_borrow_quota(
        self,
        category: Literal["spot"],
        symbol: str,
        side: str,
    ) -> dict:
        """Доступная квота заимствования (Spot).

        https://bybit-exchange.github.io/docs/v5/order/spot-borrow-quota
        """
        params = {
            "category": category,
            "symbol": symbol,
            "side": side,
        }

        return await self._make_request(
            "GET", "/v5/order/spot-borrow-check", params=params, signed=True
        )

    async def set_disconnect_cancel_all(
        self,
        time_window: int,
        product: Literal["OPTIONS", "DERIVATIVES", "SPOT"] | None = None,
    ) -> dict:
        """Настройка DCP (отмена ордеров при разрыве соединения).

        https://bybit-exchange.github.io/docs/v5/order/dcp
        """
        params = {
            "product": product,
            "timeWindow": time_window,
        }

        return await self._make_request(
            "POST", "/v5/order/disconnected-cancel-all", params=params, signed=True
        )

    async def pre_check_order(
        self,
        category: Literal["linear", "inverse", "option"],
        symbol: str,
        side: str,
        order_type: str,
        qty: str,
        price: str | None = None,
        trigger_direction: int | None = None,
        trigger_price: str | None = None,
        trigger_by: str | None = None,
        order_iv: str | None = None,
        time_in_force: str | None = None,
        position_idx: int | None = None,
        order_link_id: str | None = None,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        reduce_only: bool | None = None,
        close_on_trigger: bool | None = None,
        smp_type: str | None = None,
        mmp: bool | None = None,
        tpsl_mode: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
    ) -> dict:
        """Предварительная проверка ордера (IMR/MMR).

        https://bybit-exchange.github.io/docs/v5/order/pre-check-order
        """
        params = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": qty,
            "price": price,
            "triggerDirection": trigger_direction,
            "triggerPrice": trigger_price,
            "triggerBy": trigger_by,
            "orderIv": order_iv,
            "timeInForce": time_in_force,
            "positionIdx": position_idx,
            "orderLinkId": order_link_id,
            "takeProfit": take_profit,
            "stopLoss": stop_loss,
            "tpTriggerBy": tp_trigger_by,
            "slTriggerBy": sl_trigger_by,
            "reduceOnly": reduce_only,
            "closeOnTrigger": close_on_trigger,
            "smpType": smp_type,
            "mmp": mmp,
            "tpslMode": tpsl_mode,
            "tpLimitPrice": tp_limit_price,
            "slLimitPrice": sl_limit_price,
            "tpOrderType": tp_order_type,
            "slOrderType": sl_order_type,
        }

        return await self._make_request("POST", "/v5/order/pre-check", params=params, signed=True)

    # topic: position

    async def position_info(
        self,
        category: Literal["linear", "inverse", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Информация по позициям в реальном времени.

        https://bybit-exchange.github.io/docs/v5/position
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request("GET", "/v5/position/list", params=params, signed=True)

    async def set_leverage(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        buy_leverage: str,
        sell_leverage: str,
    ) -> dict:
        """Установка плеча для символа.

        https://bybit-exchange.github.io/docs/v5/position/leverage
        """
        params = {
            "category": category,
            "symbol": symbol,
            "buyLeverage": buy_leverage,
            "sellLeverage": sell_leverage,
        }

        return await self._make_request(
            "POST", "/v5/position/set-leverage", params=params, signed=True
        )

    async def switch_isolated_margin(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        trade_mode: int,
        buy_leverage: str,
        sell_leverage: str,
    ) -> dict:
        """Переключение кросс/изолированной маржи для символа.

        https://bybit-exchange.github.io/docs/v5/position/cross-isolate
        """
        params = {
            "category": category,
            "symbol": symbol,
            "tradeMode": trade_mode,
            "buyLeverage": buy_leverage,
            "sellLeverage": sell_leverage,
        }

        return await self._make_request(
            "POST", "/v5/position/switch-isolated", params=params, signed=True
        )

    async def switch_position_mode(
        self,
        category: Literal["linear", "inverse"],
        mode: int,
        symbol: str | None = None,
        coin: str | None = None,
    ) -> dict:
        """Переключение режима позиций (one-way/hedge).

        https://bybit-exchange.github.io/docs/v5/position/position-mode
        """
        params = {
            "category": category,
            "symbol": symbol,
            "coin": coin,
            "mode": mode,
        }

        return await self._make_request(
            "POST", "/v5/position/switch-mode", params=params, signed=True
        )

    async def set_trading_stop(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        tpsl_mode: str,
        position_idx: int,
        take_profit: str | None = None,
        stop_loss: str | None = None,
        trailing_stop: str | None = None,
        tp_trigger_by: str | None = None,
        sl_trigger_by: str | None = None,
        active_price: str | None = None,
        tp_size: str | None = None,
        sl_size: str | None = None,
        tp_limit_price: str | None = None,
        sl_limit_price: str | None = None,
        tp_order_type: str | None = None,
        sl_order_type: str | None = None,
    ) -> dict:
        """Установка TP/SL/Trailing Stop для позиции.

        https://bybit-exchange.github.io/docs/v5/position/trading-stop
        """
        params = {
            "category": category,
            "symbol": symbol,
            "tpslMode": tpsl_mode,
            "positionIdx": position_idx,
            "takeProfit": take_profit,
            "stopLoss": stop_loss,
            "trailingStop": trailing_stop,
            "tpTriggerBy": tp_trigger_by,
            "slTriggerBy": sl_trigger_by,
            "activePrice": active_price,
            "tpSize": tp_size,
            "slSize": sl_size,
            "tpLimitPrice": tp_limit_price,
            "slLimitPrice": sl_limit_price,
            "tpOrderType": tp_order_type,
            "slOrderType": sl_order_type,
        }

        return await self._make_request(
            "POST", "/v5/position/trading-stop", params=params, signed=True
        )

    async def set_auto_add_margin(
        self,
        category: Literal["linear"],
        symbol: str,
        auto_add_margin: int,
        position_idx: int | None = None,
    ) -> dict:
        """Включить/выключить авто-добавление маржи (изолированная позиция).

        https://bybit-exchange.github.io/docs/v5/position/auto-add-margin
        """
        params = {
            "category": category,
            "symbol": symbol,
            "autoAddMargin": auto_add_margin,
            "positionIdx": position_idx,
        }

        return await self._make_request(
            "POST", "/v5/position/set-auto-add-margin", params=params, signed=True
        )

    async def add_margin(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        margin: str,
        position_idx: int | None = None,
    ) -> dict:
        """Ручное добавление/уменьшение маржи (изолированная позиция).

        https://bybit-exchange.github.io/docs/v5/position/manual-add-margin
        """
        params = {
            "category": category,
            "symbol": symbol,
            "margin": margin,
            "positionIdx": position_idx,
        }

        return await self._make_request(
            "POST", "/v5/position/add-margin", params=params, signed=True
        )

    async def closed_pnl(
        self,
        category: Literal["linear", "inverse", "option"],
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История закрытой прибыли/убытка (PnL).

        https://bybit-exchange.github.io/docs/v5/position/close-pnl
        """
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/position/closed-pnl", params=params, signed=True
        )

    async def closed_option_positions(
        self,
        category: Literal["option"],
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Закрытые опционные позиции.

        https://bybit-exchange.github.io/docs/v5/position/close-position
        """
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/position/get-closed-positions", params=params, signed=True
        )

    async def move_positions(
        self,
        from_uid: str,
        to_uid: str,
        legs: list[dict[str, Any]],
    ) -> dict:
        """Перемещение позиций между учетными записями.

        https://bybit-exchange.github.io/docs/v5/position/move-position
        """
        params = {
            "fromUid": from_uid,
            "toUid": to_uid,
            "list": legs,
        }

        return await self._make_request(
            "POST", "/v5/position/move-positions", params=params, signed=True
        )

    async def move_position_history(
        self,
        category: Literal["linear", "spot", "option"] | None = None,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        status: str | None = None,
        block_trade_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История перемещения позиций.

        https://bybit-exchange.github.io/docs/v5/position/move-position-history
        """
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "status": status,
            "blockTradeId": block_trade_id,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/position/move-history", params=params, signed=True
        )

    async def confirm_pending_mmr(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
    ) -> dict:
        """Подтверждение нового уровня риска (MMR) для снятия reduceOnly.

        https://bybit-exchange.github.io/docs/v5/position/confirm-mmr
        """
        params = {
            "category": category,
            "symbol": symbol,
        }

        return await self._make_request(
            "POST", "/v5/position/confirm-pending-mmr", params=params, signed=True
        )

    async def set_tpsl_mode(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        tp_sl_mode: str,
    ) -> dict:
        """Установка режима TP/SL по умолчанию для символа.

        https://bybit-exchange.github.io/docs/v5/position/tpsl-mode
        """
        params = {
            "category": category,
            "symbol": symbol,
            "tpSlMode": tp_sl_mode,
        }

        return await self._make_request(
            "POST", "/v5/position/set-tpsl-mode", params=params, signed=True
        )

    async def set_risk_limit(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        risk_id: int,
        position_idx: int | None = None,
    ) -> dict:
        """Установка лимита риска позиции.

        https://bybit-exchange.github.io/docs/v5/position/set-risk-limit
        """
        params = {
            "category": category,
            "symbol": symbol,
            "riskId": risk_id,
            "positionIdx": position_idx,
        }

        return await self._make_request(
            "POST", "/v5/position/set-risk-limit", params=params, signed=True
        )

    # topic: pre-upgrade

    async def pre_upgrade_order_history(
        self,
        category: Literal["linear", "inverse", "option", "spot"],
        symbol: str | None = None,
        base_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_filter: str | None = None,
        order_status: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История ордеров до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/order-list
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "orderFilter": order_filter,
            "orderStatus": order_status,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/order/history", params=params, signed=True
        )

    async def pre_upgrade_trade_history(
        self,
        category: Literal["linear", "inverse", "option", "spot"],
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        base_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        exec_type: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История сделок до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/execution
        """
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "baseCoin": base_coin,
            "startTime": start_time,
            "endTime": end_time,
            "execType": exec_type,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/execution/list", params=params, signed=True
        )

    async def pre_upgrade_closed_pnl(
        self,
        category: Literal["linear", "inverse"],
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Закрытый PnL до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/close-pnl
        """
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/position/closed-pnl", params=params, signed=True
        )

    async def pre_upgrade_transaction_log(
        self,
        category: Literal["linear", "option"],
        base_coin: str | None = None,
        type: str | None = None,  # noqa: A003 - API param name
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Транзакционный лог USDC деривативов до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/transaction-log
        """
        params = {
            "category": category,
            "baseCoin": base_coin,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/account/transaction-log", params=params, signed=True
        )

    async def pre_upgrade_delivery_record(
        self,
        category: Literal["option"],
        symbol: str | None = None,
        exp_date: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Опционные записи поставок до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/delivery
        """
        params = {
            "category": category,
            "symbol": symbol,
            "expDate": exp_date,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/asset/delivery-record", params=params, signed=True
        )

    async def pre_upgrade_settlement_record(
        self,
        category: Literal["linear"],
        symbol: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Сессионные расчёты USDC Perpetual до апгрейда аккаунта.

        https://bybit-exchange.github.io/docs/v5/pre-upgrade/settlement
        """
        params = {
            "category": category,
            "symbol": symbol,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/pre-upgrade/asset/settlement-record", params=params, signed=True
        )

    # topic: account

    async def wallet_balance(
        self,
        account_type: Literal["UNIFIED", "CONTRACT", "SPOT"],
        coin: str | None = None,
    ) -> dict:
        """Баланс кошелька и активы по монетам.

        https://bybit-exchange.github.io/docs/v5/account/wallet-balance
        """
        params = {
            "accountType": account_type,
            "coin": coin,
        }

        return await self._make_request(
            "GET", "/v5/account/wallet-balance", params=params, signed=True
        )

    async def transferable_amount(
        self,
        coin_name: str,
    ) -> dict:
        """Доступная к переводу сумма (Unified).

        https://bybit-exchange.github.io/docs/v5/account/unified-trans-amnt
        """
        params = {
            "coinName": coin_name,
        }

        return await self._make_request("GET", "/v5/account/withdrawal", params=params, signed=True)

    async def upgrade_to_unified_account(self) -> dict:
        """Апгрейд до Unified аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/upgrade-unified-account
        """
        return await self._make_request(
            "POST", "/v5/account/upgrade-to-uta", params={}, signed=True
        )

    async def borrow_history(
        self,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История заимствований (проценты).

        https://bybit-exchange.github.io/docs/v5/account/borrow-history
        """
        params = {
            "currency": currency,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/account/borrow-history", params=params, signed=True
        )

    async def quick_repayment(
        self,
        coin: str | None = None,
    ) -> dict:
        """Погашение обязательств Unified аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/repay-liability
        """
        params = {
            "coin": coin,
        }

        return await self._make_request(
            "POST", "/v5/account/quick-repayment", params=params, signed=True
        )

    async def set_collateral_coin(
        self,
        coin: str,
        collateral_switch: Literal["ON", "OFF"],
    ) -> dict:
        """Настройка монеты как залога.

        https://bybit-exchange.github.io/docs/v5/account/set-collateral
        """
        params = {
            "coin": coin,
            "collateralSwitch": collateral_switch,
        }

        return await self._make_request(
            "POST", "/v5/account/set-collateral-switch", params=params, signed=True
        )

    async def set_collateral_coin_batch(
        self,
        request: list[dict[str, Any]],
    ) -> dict:
        """Пакетная настройка монет как залога.

        https://bybit-exchange.github.io/docs/v5/account/batch-set-collateral
        """
        params = {
            "request": request,
        }

        return await self._make_request(
            "POST", "/v5/account/set-collateral-switch-batch", params=params, signed=True
        )

    async def collateral_info(
        self,
        currency: str | None = None,
    ) -> dict:
        """Информация о залоге (процентные ставки, коэффициенты и пр.).

        https://bybit-exchange.github.io/docs/v5/account/collateral-info
        """
        params = {
            "currency": currency,
        }

        return await self._make_request(
            "GET", "/v5/account/collateral-info", params=params, signed=True
        )

    async def coin_greeks(
        self,
        base_coin: str | None = None,
    ) -> dict:
        """Текущие греческие параметры аккаунта по базовым монетам.

        https://bybit-exchange.github.io/docs/v5/account/coin-greeks
        """
        params = {
            "baseCoin": base_coin,
        }

        return await self._make_request("GET", "/v5/asset/coin-greeks", params=params, signed=True)

    async def fee_rate(
        self,
        category: Literal["spot", "linear", "inverse", "option"],
        symbol: str | None = None,
        base_coin: str | None = None,
    ) -> dict:
        """Торговые комиссии аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/fee-rate
        """
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
        }

        return await self._make_request("GET", "/v5/account/fee-rate", params=params, signed=True)

    async def account_info(self) -> dict:
        """Информация об аккаунте (режимы маржи и т.п.).

        https://bybit-exchange.github.io/docs/v5/account/account-info
        """
        return await self._make_request("GET", "/v5/account/info", params={}, signed=True)

    async def dcp_info(self) -> dict:
        """Конфигурация DCP аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/dcp-info
        """
        return await self._make_request("GET", "/v5/account/query-dcp-info", params={}, signed=True)

    async def transaction_log(
        self,
        account_type: Literal["UNIFIED"] | None = None,
        category: Literal["spot", "linear", "option", "inverse"] | None = None,
        currency: str | None = None,
        base_coin: str | None = None,
        type: str | None = None,  # noqa: A003 - API param name
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Транзакционный лог Unified аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/transaction-log
        """
        params = {
            "accountType": account_type,
            "category": category,
            "currency": currency,
            "baseCoin": base_coin,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/account/transaction-log", params=params, signed=True
        )

    async def contract_transaction_log(
        self,
        currency: str | None = None,
        base_coin: str | None = None,
        type: str | None = None,  # noqa: A003 - API param name
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Транзакционный лог деривативного кошелька.

        https://bybit-exchange.github.io/docs/v5/account/contract-transaction-log
        """
        params = {
            "currency": currency,
            "baseCoin": base_coin,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return await self._make_request(
            "GET", "/v5/account/contract-transaction-log", params=params, signed=True
        )

    async def smp_group(self) -> dict:
        """Получить SMP group ID.

        https://bybit-exchange.github.io/docs/v5/account/smp-group
        """
        return await self._make_request("GET", "/v5/account/smp-group", params={}, signed=True)

    async def set_margin_mode(
        self,
        set_margin_mode: Literal["ISOLATED_MARGIN", "REGULAR_MARGIN", "PORTFOLIO_MARGIN"],
    ) -> dict:
        """Установить режим маржи аккаунта.

        https://bybit-exchange.github.io/docs/v5/account/set-margin-mode
        """
        params = {
            "setMarginMode": set_margin_mode,
        }

        return await self._make_request(
            "POST", "/v5/account/set-margin-mode", params=params, signed=True
        )

    async def set_spot_hedging(
        self,
        set_hedging_mode: Literal["ON", "OFF"],
    ) -> dict:
        """Включить/выключить спотовый hedging в Portfolio margin.

        https://bybit-exchange.github.io/docs/v5/account/set-spot-hedge
        """
        params = {
            "setHedgingMode": set_hedging_mode,
        }

        return await self._make_request(
            "POST", "/v5/account/set-hedging-mode", params=params, signed=True
        )

    async def set_limit_price_action(
        self,
        category: Literal["linear", "inverse", "spot"],
        modify_enable: bool,
    ) -> dict:
        """Настройка поведения при выходе лимитной цены за границы.

        https://bybit-exchange.github.io/docs/v5/account/set-price-limit
        """
        params = {
            "category": category,
            "modifyEnable": modify_enable,
        }

        return await self._make_request(
            "POST", "/v5/account/set-limit-px-action", params=params, signed=True
        )

    async def user_setting_config(self) -> dict:
        """Получить конфигурацию поведения для лимитных цен.

        https://bybit-exchange.github.io/docs/v5/account/get-user-setting-config
        """
        return await self._make_request(
            "GET", "/v5/account/user-setting-config", params={}, signed=True
        )

    async def set_mmp(
        self,
        base_coin: str,
        window: str,
        frozen_period: str,
        qty_limit: str,
        delta_limit: str,
    ) -> dict:
        """Настроить Market Maker Protection (MMP).

        https://bybit-exchange.github.io/docs/v5/account/set-mmp
        """
        params = {
            "baseCoin": base_coin,
            "window": window,
            "frozenPeriod": frozen_period,
            "qtyLimit": qty_limit,
            "deltaLimit": delta_limit,
        }

        return await self._make_request(
            "POST", "/v5/account/mmp-modify", params=params, signed=True
        )

    async def reset_mmp(
        self,
        base_coin: str,
    ) -> dict:
        """Сбросить состояние MMP (разморозить).

        https://bybit-exchange.github.io/docs/v5/account/reset-mmp
        """
        params = {
            "baseCoin": base_coin,
        }

        return await self._make_request("POST", "/v5/account/mmp-reset", params=params, signed=True)

    async def mmp_state(
        self,
        base_coin: str,
    ) -> dict:
        """Статус MMP.

        https://bybit-exchange.github.io/docs/v5/account/get-mmp-state
        """
        params = {
            "baseCoin": base_coin,
        }

        return await self._make_request("GET", "/v5/account/mmp-state", params=params, signed=True)
