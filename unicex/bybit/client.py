__all__ = ["BybitClient"]

import json
import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature

from .types import Category, FuturesCategory, OrderType, Side, Timeframe


class _BaseBybitClient(BaseClient):
    """Базовый класс для клиентов Bybit API."""

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

    def _make_request(
        self,
        method: RequestMethod,
        url: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bybit API с поддержкой подписи.

        Если signed=True, формируется подпись для приватных endpoint'ов.
        Если signed=False, запрос отправляется как обычный публичный, через
        базовый _make_request без обработки подписи.

        Параметры:
            method (str): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            url (str): Полный URL эндпоинта Bybit API.
            signed (bool): Нужно ли подписывать запрос.
            params (dict | None): Параметры запроса. Передаются в body, если запрос типа "POST", иначе в query_params

        Возвращает:
            dict: Ответ в формате JSON.
        """
        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}

        # Генерируем временную метку
        timestamp = str(int(time.time() * 1000))

        # Проверяем нужно ли подписывать запрос
        if not signed:
            headers = self._get_headers(timestamp)
            return super()._make_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            )

        # Проверяем наличие апи ключей для подписи запроса
        if not self._api_key or not self._api_secret:
            raise NotAuthorized("Api key is required to private endpoints")

        # Формируем payload
        payload = params

        # Генерируем строку для подписи
        # Источник: https://github.com/bybit-exchange/api-usage-examples/blob/master/V5_demo/api_demo/Encryption_HMAC.py
        dumped_payload = json.dumps(payload)
        prepared_query_string = timestamp + self._api_key + self._RECV_WINDOW + dumped_payload
        signature = generate_hmac_sha256_signature(self._api_secret, prepared_query_string)

        # Генерируем заголовки (вкл. в себя подпись и апи ключ)
        headers = self._get_headers(timestamp, signature)

        if method == "POST":  # Отправляем параметры в тело запроса
            return super()._make_request(
                method=method,
                url=url,
                json=payload,
                headers=headers,
            )
        else:  # Иначе параметры добавляем к query string
            return super()._make_request(
                method=method,
                url=url,
                params=payload,
                headers=headers,
            )


class BybitClient(_BaseBybitClient):
    """Клиент для работы с Bybit API (REST v5)."""

    # ==========================================================================
    # MARKET DATA (Public)
    # ==========================================================================

    def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        url = self._BASE_URL + "/v5/market/time"
        return self._make_request("GET", url)

    def instruments_info(
        self,
        category: Category,
        symbol: str | None = None,
        status: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Информация об инструментах торговли.

        https://bybit-exchange.github.io/docs/v5/market/instrument
        """
        url = self._BASE_URL + "/v5/market/instruments-info"
        params = {
            "category": category,
            "symbol": symbol,
            "status": status,
            "baseCoin": base_coin,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, params=params)

    def tickers(
        self,
        category: Category,
        symbol: str | None = None,
        base_coin: str | None = None,
        exp_date: str | None = None,
    ) -> dict:
        """Тикеры (вкл. 24h stats и last price).

        https://bybit-exchange.github.io/docs/v5/market/tickers
        """
        url = self._BASE_URL + "/v5/market/tickers"
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "expDate": exp_date,
        }

        return self._make_request("GET", url, params=params)

    def mark_price_kline(
        self,
        category: Category,
        symbol: str,
        interval: Timeframe,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Свечи по mark price.

        https://bybit-exchange.github.io/docs/v5/market/mark-kline
        """
        url = self._BASE_URL + "/v5/market/mark-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def index_price_kline(
        self,
        category: Category,
        symbol: str,
        interval: Timeframe,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Свечи по index price.

        https://bybit-exchange.github.io/docs/v5/market/index-kline
        """
        url = self._BASE_URL + "/v5/market/index-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def premium_index_price_kline(
        self,
        category: Category,
        symbol: str,
        interval: Timeframe,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Свечи по premium index price.

        https://bybit-exchange.github.io/docs/v5/market/premium-index-kline
        """
        url = self._BASE_URL + "/v5/market/premium-index-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def klines(
        self,
        symbol: str,
        interval: Timeframe,
        category: Category,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи.

        https://bybit-exchange.github.io/docs/v5/market/kline
        """
        url = self._BASE_URL + "/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def recent_trades(
        self,
        category: Category,
        symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Последние сделки.

        https://bybit-exchange.github.io/docs/v5/market/recent-trade
        """
        url = self._BASE_URL + "/v5/market/recent-trade"
        params = {"category": category, "symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def orderbook(
        self,
        category: Category,
        symbol: str,
        limit: int | None = None,
    ) -> dict:
        """Стакан ордеров (Order Book).

        https://bybit-exchange.github.io/docs/v5/market/orderbook
        """
        url = self._BASE_URL + "/v5/market/orderbook"
        params = {"category": category, "symbol": symbol, "limit": limit}

        return self._make_request("GET", url, params=params)

    def funding_history(
        self,
        category: Category,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """История фондирования.

        https://bybit-exchange.github.io/docs/v5/market/funding
        """
        url = self._BASE_URL + "/v5/market/funding/history"
        params = {
            "category": category,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def open_interest(
        self,
        category: Category,
        symbol: str | None = None,
        interval_time: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Открытый интерес.

        https://bybit-exchange.github.io/docs/v5/market/open-interest
        """
        url = self._BASE_URL + "/v5/market/open-interest"
        params = {
            "category": category,
            "symbol": symbol,
            "intervalTime": interval_time,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return self._make_request("GET", url, params=params)

    def insurance(self, coin: str | None = None) -> dict:
        """Данные страхового фонда.

        https://bybit-exchange.github.io/docs/v5/market/insurance
        """
        url = self._BASE_URL + "/v5/market/insurance"
        params = {"coin": coin}

        return self._make_request("GET", url, params=params)

    def risk_limit(self, category: Category, symbol: str | None = None) -> dict:
        """Лимиты риска по инструментам.

        https://bybit-exchange.github.io/docs/v5/market/risk-limit
        """
        url = self._BASE_URL + "/v5/market/risk-limit"
        params = {"category": category, "symbol": symbol}

        return self._make_request("GET", url, params=params)

    def delivery_price(self, category: Category, symbol: str) -> dict:
        """Delivery price (для опционов/фьючерсов).

        https://bybit-exchange.github.io/docs/v5/market/delivery-price
        """
        url = self._BASE_URL + "/v5/market/delivery-price"
        params = {"category": category, "symbol": symbol}

        return self._make_request("GET", url, params=params)

    # ==========================================================================
    # ORDER (Private)
    # ==========================================================================

    def create_order(
        self,
        category: Category,
        symbol: str,
        side: Side,
        orderType: OrderType,
        qty: str,
        price: str | None = None,
        timeInForce: str | None = None,
        orderLinkId: str | None = None,
        isLeverage: int | None = None,
        orderFilter: str | None = None,
        triggerPrice: str | None = None,
        triggerDirection: int | None = None,
        marketUnit: str | None = None,
        slippageToleranceType: str | None = None,
        slippageTolerance: str | None = None,
        triggerBy: str | None = None,
        orderIv: str | None = None,
        positionIdx: int | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        tpslMode: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
        reduceOnly: bool | None = None,
        closeOnTrigger: bool | None = None,
        smpType: str | None = None,
        mmp: bool | None = None,
    ) -> dict:
        """Создание ордера.

        https://bybit-exchange.github.io/docs/v5/order/create-order
        """
        url = self._BASE_URL + "/v5/order/create"
        params = {
            "category": category,
            "symbol": symbol,
            "side": side,
            "orderType": orderType,
            "qty": qty,
            "price": price,
            "timeInForce": timeInForce,
            "orderLinkId": orderLinkId,
            "isLeverage": isLeverage,
            "orderFilter": orderFilter,
            "triggerPrice": triggerPrice,
            "triggerDirection": triggerDirection,
            "marketUnit": marketUnit,
            "slippageToleranceType": slippageToleranceType,
            "slippageTolerance": slippageTolerance,
            "triggerBy": triggerBy,
            "orderIv": orderIv,
            "positionIdx": positionIdx,
            "takeProfit": takeProfit,
            "stopLoss": stopLoss,
            "tpTriggerBy": tpTriggerBy,
            "slTriggerBy": slTriggerBy,
            "tpslMode": tpslMode,
            "tpLimitPrice": tpLimitPrice,
            "slLimitPrice": slLimitPrice,
            "tpOrderType": tpOrderType,
            "slOrderType": slOrderType,
            "reduceOnly": reduceOnly,
            "closeOnTrigger": closeOnTrigger,
            "smpType": smpType,
            "mmp": mmp,
        }

        return self._make_request("POST", url, True, params=params)

    def amend_order(
        self,
        category: Category,
        symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        qty: str | None = None,
        price: str | None = None,
        triggerPrice: str | None = None,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        triggerBy: str | None = None,
        tpslMode: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
        orderIv: str | None = None,
        reduceOnly: bool | None = None,
        closeOnTrigger: bool | None = None,
        smpType: str | None = None,
        mmp: bool | None = None,
    ) -> dict:
        """Изменение ордера.

        https://bybit-exchange.github.io/docs/v5/order/amend-order
        """
        url = self._BASE_URL + "/v5/order/amend"
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": orderId,
            "orderLinkId": orderLinkId,
            "qty": qty,
            "price": price,
            "triggerPrice": triggerPrice,
            "takeProfit": takeProfit,
            "stopLoss": stopLoss,
            "tpTriggerBy": tpTriggerBy,
            "slTriggerBy": slTriggerBy,
            "triggerBy": triggerBy,
            "tpslMode": tpslMode,
            "tpLimitPrice": tpLimitPrice,
            "slLimitPrice": slLimitPrice,
            "tpOrderType": tpOrderType,
            "slOrderType": slOrderType,
            "orderIv": orderIv,
            "reduceOnly": reduceOnly,
            "closeOnTrigger": closeOnTrigger,
            "smpType": smpType,
            "mmp": mmp,
        }

        return self._make_request("POST", url, True, params=params)

    def cancel_order(
        self,
        category: Category,
        symbol: str,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
    ) -> dict:
        """Отмена ордера.

        https://bybit-exchange.github.io/docs/v5/order/cancel-order
        """
        url = self._BASE_URL + "/v5/order/cancel"
        params = {
            "category": category,
            "symbol": symbol,
            "orderId": orderId,
            "orderLinkId": orderLinkId,
            "orderFilter": orderFilter,
        }

        return self._make_request("POST", url, True, params=params)

    def cancel_all_orders(
        self,
        category: Category,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        orderFilter: str | None = None,
        stopOrderType: str | None = None,
    ) -> dict:
        """Отмена всех ордеров.

        https://bybit-exchange.github.io/docs/v5/order/cancel-all
        """
        url = self._BASE_URL + "/v5/order/cancel-all"
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderFilter": orderFilter,
            "stopOrderType": stopOrderType,
        }

        return self._make_request("POST", url, True, params=params)

    def open_orders(
        self,
        category: Category,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        orderId: str | None = None,
        orderLinkId: str | None = None,
        orderFilter: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Список открытых ордеров.

        https://bybit-exchange.github.io/docs/v5/order/open-order
        """
        url = self._BASE_URL + "/v5/order/realtime"
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderId": orderId,
            "orderLinkId": orderLinkId,
            "orderFilter": orderFilter,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, True, params=params)

    def order_history(
        self,
        category: Category,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История ордеров.

        https://bybit-exchange.github.io/docs/v5/order/order-list
        """
        url = self._BASE_URL + "/v5/order/history"
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "orderId": order_id,
            "orderLinkId": order_link_id,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, signed=True, params=params)

    def batch_create_orders(self, category: Category, request: list[dict]) -> dict:
        """Пакетное создание ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-place
        """
        url = self._BASE_URL + "/v5/order/batch-create"
        params = {"category": category, "request": request}

        return self._make_request("POST", url, True, params=params)

    def batch_amend_orders(self, category: Category, request: list[dict]) -> dict:
        """Пакетное изменение ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-amend
        """
        url = self._BASE_URL + "/v5/order/batch-amend"
        params = {"category": category, "request": request}

        return self._make_request("POST", url, True, params=params)

    def batch_cancel_orders(self, category: Category, request: list[dict]) -> dict:
        """Пакетная отмена ордеров.

        https://bybit-exchange.github.io/docs/v5/order/batch-cancel
        """
        url = self._BASE_URL + "/v5/order/batch-cancel"
        params = {"category": category, "request": request}

        return self._make_request("POST", url, True, params=params)

    # ==========================================================================
    # POSITION (Private)
    # ==========================================================================

    def positions(
        self,
        category: Category,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Список позиций.

        https://bybit-exchange.github.io/docs/v5/position/list
        """
        url = self._BASE_URL + "/v5/position/list"
        params = {
            "category": category,
            "symbol": symbol,
            "baseCoin": base_coin,
            "settleCoin": settle_coin,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, True, params=params)

    def set_leverage(
        self,
        category: FuturesCategory,
        symbol: str,
        buy_leverage: str,
        sell_leverage: str,
    ) -> dict:
        """Установить кредитное плечо.

        https://bybit-exchange.github.io/docs/v5/position/leverage
        """
        url = self._BASE_URL + "/v5/position/set-leverage"
        params = {
            "category": category,
            "symbol": symbol,
            "buyLeverage": buy_leverage,
            "sellLeverage": sell_leverage,
        }

        return self._make_request("POST", url, True, params=params)

    def switch_isolated(
        self,
        category: FuturesCategory,
        symbol: str,
        tradeMode: int,
        buyLeverage: str | None = None,
        sellLeverage: str | None = None,
    ) -> dict:
        """Переключение режима маржи (cross/isolated).

        https://bybit-exchange.github.io/docs/v5/position/switch-isolated
        """
        url = self._BASE_URL + "/v5/position/switch-isolated"
        params = {
            "category": category,
            "symbol": symbol,
            "tradeMode": tradeMode,
            "buyLeverage": buyLeverage,
            "sellLeverage": sellLeverage,
        }

        return self._make_request("POST", url, True, params=params)

    def set_tpsl_mode(
        self,
        category: FuturesCategory,
        symbol: str,
        tpSlMode: str,
    ) -> dict:
        """Режим TP/SL (partial/full).

        https://bybit-exchange.github.io/docs/v5/position/tpsl-mode
        """
        url = self._BASE_URL + "/v5/position/set-tpsl-mode"
        params = {"category": category, "symbol": symbol, "tpSlMode": tpSlMode}

        return self._make_request("POST", url, True, params=params)

    def set_trading_stop(
        self,
        category: FuturesCategory,
        symbol: str,
        takeProfit: str | None = None,
        stopLoss: str | None = None,
        trailingStop: str | None = None,
        tpTriggerBy: str | None = None,
        slTriggerBy: str | None = None,
        positionIdx: int | None = None,
        tpslMode: str | None = None,
        tpLimitPrice: str | None = None,
        slLimitPrice: str | None = None,
        tpOrderType: str | None = None,
        slOrderType: str | None = None,
    ) -> dict:
        """Установка TP/SL/Trailing Stop.

        https://bybit-exchange.github.io/docs/v5/position/trading-stop
        """
        url = self._BASE_URL + "/v5/position/trading-stop"
        params = {
            "category": category,
            "symbol": symbol,
            "takeProfit": takeProfit,
            "stopLoss": stopLoss,
            "trailingStop": trailingStop,
            "tpTriggerBy": tpTriggerBy,
            "slTriggerBy": slTriggerBy,
            "positionIdx": positionIdx,
            "tpslMode": tpslMode,
            "tpLimitPrice": tpLimitPrice,
            "slLimitPrice": slLimitPrice,
            "tpOrderType": tpOrderType,
            "slOrderType": slOrderType,
        }

        return self._make_request("POST", url, True, params=params)

    def set_risk_limit(
        self,
        category: FuturesCategory,
        symbol: str,
        riskId: int,
        positionIdx: int | None = None,
    ) -> dict:
        """Установка лимита риска.

        https://bybit-exchange.github.io/docs/v5/position/set-risk-limit
        """
        url = self._BASE_URL + "/v5/position/set-risk-limit"
        params = {
            "category": category,
            "symbol": symbol,
            "riskId": riskId,
            "positionIdx": positionIdx,
        }

        return self._make_request("POST", url, True, params=params)

    def set_auto_add_margin(
        self,
        category: FuturesCategory,
        symbol: str,
        autoAddMargin: int,
        positionIdx: int | None = None,
    ) -> dict:
        """Auto add margin (вкл/выкл).

        https://bybit-exchange.github.io/docs/v5/position/auto-add-margin
        """
        url = self._BASE_URL + "/v5/position/set-auto-add-margin"
        params = {
            "category": category,
            "symbol": symbol,
            "autoAddMargin": autoAddMargin,
            "positionIdx": positionIdx,
        }

        return self._make_request("POST", url, True, params=params)

    def switch_position_mode(self, category: FuturesCategory, symbol: str, mode: int) -> dict:
        """Hedge (двунаправленный) / One-way режим.

        https://bybit-exchange.github.io/docs/v5/position/switch-mode
        """
        url = self._BASE_URL + "/v5/position/switch-mode"
        params = {"category": category, "symbol": symbol, "mode": mode}

        return self._make_request("POST", url, True, params=params)

    # ==========================================================================
    # ACCOUNT (Private)
    # ==========================================================================

    def wallet_balance(
        self,
        accountType: str,
        coin: str | None = None,
    ) -> dict:
        """Баланс кошелька.

        https://bybit-exchange.github.io/docs/v5/account/wallet-balance
        """
        url = self._BASE_URL + "/v5/account/wallet-balance"
        params = {"accountType": accountType, "coin": coin}

        return self._make_request("GET", url, True, params=params)

    def fee_rate(
        self, category: Category, symbol: str | None = None, base_coin: str | None = None
    ) -> dict:
        """Торговые комиссии (ваши персональные).

        https://bybit-exchange.github.io/docs/v5/account/fee-rate
        """
        url = self._BASE_URL + "/v5/account/fee-rate"
        params = {"category": category, "symbol": symbol, "baseCoin": base_coin}

        return self._make_request("GET", url, True, params=params)

    def transaction_log(
        self,
        accountType: str,
        category: str | None = None,
        currency: str | None = None,
        base_coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Транзакционный лог (сводка движений средств).

        https://bybit-exchange.github.io/docs/v5/account/transaction-log
        """
        url = self._BASE_URL + "/v5/account/transaction-log"
        params = {
            "accountType": accountType,
            "category": category,
            "currency": currency,
            "baseCoin": base_coin,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, True, params=params)

    def set_margin_mode(
        self,
        setMarginMode: int,
        productType: str,
    ) -> dict:
        """Unified Margin / Portfolio Margin переключение режима (если доступно).

        https://bybit-exchange.github.io/docs/v5/account/set-margin-mode
        """
        url = self._BASE_URL + "/v5/account/set-margin-mode"
        params = {"setMarginMode": setMarginMode, "productType": productType}

        return self._make_request("POST", url, True, params=params)

    def set_fee_rate(
        self,
        symbol: str,
        takerFeeRate: str | None = None,
        makerFeeRate: str | None = None,
    ) -> dict:
        """(Для брокеров/привилегий) Настройка своей комиссии — если доступно.

        https://bybit-exchange.github.io/docs/v5/account/fee-rate
        """
        url = self._BASE_URL + "/v5/account/set-fee-rate"
        params = {
            "symbol": symbol,
            "takerFeeRate": takerFeeRate,
            "makerFeeRate": makerFeeRate,
        }

        return self._make_request("POST", url, True, params=params)

    # ==========================================================================
    # ASSET / WALLET (Private)
    # ==========================================================================

    def deposit_withdraw_status(
        self,
        coin: str | None = None,
    ) -> dict:
        """Статус депозита/вывода по монетам.

        https://bybit-exchange.github.io/docs/v5/asset/coin-info
        """
        url = self._BASE_URL + "/v5/asset/coin/query-info"
        params = {"coin": coin}

        return self._make_request("GET", url, True, params=params)

    def deposit_list(
        self,
        coin: str | None = None,
        chainType: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Список депозитов.

        https://bybit-exchange.github.io/docs/v5/asset/deposit
        """
        url = self._BASE_URL + "/v5/asset/deposit/query-record"
        params = {
            "coin": coin,
            "chainType": chainType,
            "startTime": start_time,
            "endTime": end_time,
            "cursor": cursor,
            "limit": limit,
        }

        return self._make_request("GET", url, True, params=params)

    def withdraw_list(
        self,
        coin: str | None = None,
        withdrawType: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Список выводов.

        https://bybit-exchange.github.io/docs/v5/asset/withdraw
        """
        url = self._BASE_URL + "/v5/asset/withdraw/query-record"
        params = {
            "coin": coin,
            "withdrawType": withdrawType,
            "startTime": start_time,
            "endTime": end_time,
            "cursor": cursor,
            "limit": limit,
        }

        return self._make_request("GET", url, True, params=params)

    def internal_transfer(
        self,
        transferId: str,
        coin: str,
        amount: str,
        fromAccountType: str,
        toAccountType: str,
    ) -> dict:
        """Внутренний перевод между счетами.

        https://bybit-exchange.github.io/docs/v5/asset/transfer
        """
        url = self._BASE_URL + "/v5/asset/transfer/inter-transfer"
        params = {
            "transferId": transferId,
            "coin": coin,
            "amount": amount,
            "fromAccountType": fromAccountType,
            "toAccountType": toAccountType,
        }

        return self._make_request("POST", url, True, params=params)

    def query_internal_transfer(
        self,
        transferId: str | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Запрос статуса внутренних переводов.

        https://bybit-exchange.github.io/docs/v5/asset/transfer
        """
        url = self._BASE_URL + "/v5/asset/transfer/query-inter-transfer-list"
        params = {"transferId": transferId, "cursor": cursor, "limit": limit}

        return self._make_request("GET", url, True, params=params)

    def withdraw(
        self,
        coin: str,
        chain: str,
        address: str,
        amount: str,
        tag: str | None = None,
        requestId: str | None = None,
        timestamp: int | None = None,
        forceChain: int | None = None,
        accountType: str | None = None,
    ) -> dict:
        """Создание заявки на вывод.

        https://bybit-exchange.github.io/docs/v5/asset/withdraw
        """
        url = self._BASE_URL + "/v5/asset/withdraw/create"
        params = {
            "coin": coin,
            "chain": chain,
            "address": address,
            "amount": amount,
            "tag": tag,
            "requestId": requestId,
            "timestamp": timestamp,
            "forceChain": forceChain,
            "accountType": accountType,
        }

        return self._make_request("POST", url, True, params=params)

    def cancel_withdraw(self, withdrawId: str) -> dict:
        """Отмена вывода.

        https://bybit-exchange.github.io/docs/v5/asset/withdraw
        """
        url = self._BASE_URL + "/v5/asset/withdraw/cancel"
        params = {"withdrawId": withdrawId}

        return self._make_request("POST", url, True, params=params)

    def deposit_address(
        self, coin: str, chainType: str | None = None, accountType: str | None = None
    ) -> dict:
        """Адрес депозита.

        https://bybit-exchange.github.io/docs/v5/asset/deposit-address
        """
        url = self._BASE_URL + "/v5/asset/deposit/query-address"
        params = {"coin": coin, "chainType": chainType, "accountType": accountType}

        return self._make_request("GET", url, True, params=params)

    # ==========================================================================
    # SPOT MARGIN (Private)
    # ==========================================================================

    def spot_margin_switch(self, spotMarginMode: int) -> dict:
        """Вкл/выкл Spot Margin Trading.

        https://bybit-exchange.github.io/docs/v5/spot-margin/switch
        """
        url = self._BASE_URL + "/v5/spot-margin/switch"
        params = {"spotMarginMode": spotMarginMode}

        return self._make_request("POST", url, True, params=params)

    def spot_margin_borrow_history(
        self,
        coin: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """История заимствований (Spot Margin).

        https://bybit-exchange.github.io/docs/v5/spot-margin/borrow-history
        """
        url = self._BASE_URL + "/v5/spot-margin/borrow-history"
        params = {
            "coin": coin,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "cursor": cursor,
        }

        return self._make_request("GET", url, True, params=params)

    # ==========================================================================
    # OPTIONS (Public/Private) — базовые рыночные данные
    # ==========================================================================

    def options_delivery_price(self, symbol: str) -> dict:
        """Delivery price для опциона.

        https://bybit-exchange.github.io/docs/v5/market/delivery-price
        """
        url = self._BASE_URL + "/v5/market/delivery-price"
        params = {"category": "option", "symbol": symbol}

        return self._make_request("GET", url, params=params)

    # ==========================================================================
    # COPY TRADING / BROKER / LOAN
    # ==========================================================================

    def broker_earnings(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Доходы брокера (если аккаунт поддерживает).

        https://bybit-exchange.github.io/docs/v5/broker/...
        """
        url = self._BASE_URL + "/v5/broker/earnings"
        params = {"startTime": start_time, "endTime": end_time, "cursor": cursor, "limit": limit}

        return self._make_request("GET", url, True, params=params)

    def institutional_loan_list(
        self, status: str | None = None, cursor: str | None = None, limit: int | None = None
    ) -> dict:
        """Список займов (Institutional Loan).

        https://bybit-exchange.github.io/docs/v5/loan/...
        """
        url = self._BASE_URL + "/v5/loan/query-list"
        params = {"status": status, "cursor": cursor, "limit": limit}

        return self._make_request("GET", url, True, params=params)
