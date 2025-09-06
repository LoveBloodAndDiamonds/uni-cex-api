__all__ = ["BybitClient"]

import json
import time
from typing import Any

from unicex.abstract import BaseSyncClient
from unicex.exceptions import MissingApiKey
from unicex.types import RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature

from .types import FuturesProductType, FuturesTimeframe, OrderType, ProductType, Side


class _BaseBybitClient(BaseSyncClient):
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
            raise MissingApiKey("Api key is required to private endpoints")

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
    """Клиент для работы с Bybit API."""

    # ========== PUBLIC ENDPOINTS ==========

    def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        url = self._BASE_URL + "/v5/market/time"

        return self._make_request("GET", url)

    def instruments_info(
        self,
        category: ProductType,
        symbol: str | None = None,
        status: str | None = None,
        base_coin: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Получение информации об инструментах торговли.

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
        category: ProductType,
        symbol: str | None = None,
        base_coin: str | None = None,
        exp_date: str | None = None,
    ) -> dict:
        """Получение информации о тикерах. В т.ч. статистику за 24 ч. и последнюю цену.

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

    def klines(
        self,
        symbol: str,
        interval: FuturesTimeframe,
        category: ProductType,
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение исторических свечей.

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

    # ========== PRIVATE ENDPOINTS ==========

    def order_history(
        self,
        category: ProductType,
        symbol: str | None = None,
        base_coin: str | None = None,
        settle_coin: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict:
        """Получение истории ордеров.

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

    def create_order(
        self,
        category: ProductType,
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

    def set_leverage(
        self,
        category: FuturesProductType,
        symbol: str,
        buy_leverage: str,
        sell_leverage: str,
    ) -> dict:
        """Установить кредитное плечо для позиции.

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

    # ========== WALLET ENDPOINTS ==========
