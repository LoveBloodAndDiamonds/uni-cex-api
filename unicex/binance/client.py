__all__ = ["Client"]

import json
import time
import warnings
from typing import Any, Literal
from urllib.parse import urlencode

from yarl import URL

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature

_SPOT_LISTEN_KEY_REMOVED = (
    "Binance removed spot listenKey endpoints on 2026-02-20 (HTTP 410 Gone). "
    "Use WebsocketManager.user_data_stream(), which subscribes via WebSocket API."
)


class Client(BaseClient):
    """Клиент для работы с Binance API."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, method: RequestMethod) -> dict:
        """Возвращает заголовки для запросов к Binance API."""
        headers = {"Accept": "application/json"}
        if self._api_key:  # type: ignore[attr-defined]
            headers["X-MBX-APIKEY"] = self._api_key  # type: ignore[attr-defined]
        if method in ["POST", "PUT", "DELETE"]:
            headers.update({"Content-Type": "application/x-www-form-urlencoded"})
        return headers

    @staticmethod
    def _normalize_params(params: dict[str, Any]) -> dict[str, Any]:
        """Приводит значения параметров к виду, который ожидает Binance.

        - `bool` → `"true"` / `"false"`;
        - `list` / `dict` → компактный JSON (`symbols=["BTCUSDT","ETHUSDT"]`).
        """
        result = {}
        for k, v in params.items():
            if isinstance(v, bool):
                result[k] = "true" if v else "false"
            elif isinstance(v, list | dict):
                result[k] = json.dumps(v, separators=(",", ":"), ensure_ascii=False)
            else:
                result[k] = v
        return result

    def _sign_query(self, params: dict[str, Any]) -> str:
        """Добавляет `timestamp`/`recvWindow`, подписывает и возвращает готовую query string.

        С 2026-01-15 Binance считает подпись по percent-encoded строке, поэтому
        подписывается ровно та строка, которая уйдёт в запрос.
        """
        if not self.is_authorized():
            raise NotAuthorized("Api key and api secret is required to private endpoints")

        payload = {**params}
        payload["recvWindow"] = self._RECV_WINDOW
        payload["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(payload)
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
            "hex",
        )
        return f"{query_string}&signature={signature}"

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Binance API.

        Если signed=True, к параметрам добавляются `timestamp`, `recvWindow` и подпись.
        Все параметры (и для GET, и для POST/PUT/DELETE) передаются в query string.
        Подписанная строка отправляется как есть (`yarl.URL(..., encoded=True)`),
        чтобы aiohttp не перекодировал её и подпись совпала.

        Параметры:
            method (`str`): HTTP метод ("GET", "POST", "DELETE" и т.д.).
            url (`str`): Полный URL эндпоинта Binance API.
            signed (`bool`): Нужно ли подписывать запрос.
            params (`dict | None`): Query-параметры.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        params = self._normalize_params(filter_params(params) if params else {})

        if not signed:
            return await super()._make_request(
                method=method, url=url, params=params, headers=self._get_headers(method)
            )

        signed_url = URL(f"{url}?{self._sign_query(params)}", encoded=True)
        return await super()._make_request(
            method=method,
            url=signed_url,
            headers=self._get_headers(method),
        )

    async def request(self, method: RequestMethod, url: str, params: dict, signed: bool) -> dict:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (`str`): HTTP метод ("GET", "POST", "DELETE" и т.д.).
            url (`str`): Полный URL эндпоинта Binance API.
            signed (`bool`): Нужно ли подписывать запрос.
            params (`dict | None`): Query-параметры.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(method=method, url=url, params=params, signed=signed)

    # topic: general endpoints

    async def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#test-connectivity
        """
        url = self._BASE_SPOT_URL + "/api/v3/ping"

        return await self._make_request("GET", url)

    async def server_time(self) -> dict:
        """Получение серверного времени.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#check-server-time
        """
        url = self._BASE_SPOT_URL + "/api/v3/time"

        return await self._make_request("GET", url)

    async def exchange_info(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        permissions: str | list[str] | None = None,
        show_permission_sets: bool | None = None,
        symbol_status: str | None = None,
    ) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information
        """
        url = self._BASE_SPOT_URL + "/api/v3/exchangeInfo"
        params = {
            "symbol": symbol,
            "symbols": symbols,
            "permissions": permissions,
            "showPermissionSets": show_permission_sets,
            "symbolStatus": symbol_status,
        }

        return await self._make_request("GET", url, params=params)

    # topic: market data endpoints

    async def depth(
        self, symbol: str, limit: int | None = None, symbol_status: str | None = None
    ) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book
        """
        url = self._BASE_SPOT_URL + "/api/v3/depth"
        params = {"symbol": symbol, "limit": limit, "symbolStatus": symbol_status}

        return await self._make_request("GET", url, params=params)

    async def trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#recent-trades-list
        """
        url = self._BASE_SPOT_URL + "/api/v3/trades"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Исторические сделки.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#old-trade-lookup
        """
        url = self._BASE_SPOT_URL + "/api/v3/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return await self._make_request("GET", url, params=params)

    async def agg_trades(
        self,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение агрегированных сделок.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#compressedaggregate-trades-list
        """
        url = self._BASE_SPOT_URL + "/api/v3/aggTrades"
        params = {
            "symbol": symbol,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def klines(
        self,
        symbol: str,
        interval: str,
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

        return await self._make_request("GET", url, params=params)

    async def ui_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение UI свечей (оптимизированы для отображения).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#uiklines
        """
        url = self._BASE_SPOT_URL + "/api/v3/uiKlines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "timeZone": time_zone,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def avg_price(self, symbol: str) -> dict:
        """Получение текущей средней цены символа.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#current-average-price
        """
        url = self._BASE_SPOT_URL + "/api/v3/avgPrice"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def ticker_24hr(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        type: str | None = None,
        symbol_status: str | None = None,
    ) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/24hr"
        params = {
            "symbol": symbol,
            "type": type,
            "symbols": symbols,
            "symbolStatus": symbol_status,
        }

        return await self._make_request("GET", url, params=params)

    async def ticker_trading_day(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        time_zone: str | None = None,
        type: str | None = None,
        symbol_status: str | None = None,
    ) -> dict | list[dict]:
        """Статистика изменения цен за торговый день.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#trading-day-ticker
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/tradingDay"
        params = {
            "symbol": symbol,
            "symbols": symbols,
            "timeZone": time_zone,
            "type": type,
            "symbolStatus": symbol_status,
        }

        return await self._make_request("GET", url, params=params)

    async def ticker_price(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-price-ticker
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/price"
        params = {"symbol": symbol, "symbols": symbols, "symbolStatus": symbol_status}

        return await self._make_request("GET", url, params=params)

    async def ticker_book_ticker(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> dict | list[dict]:
        """Получение лучших цен bid/ask в книге ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-order-book-ticker
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/bookTicker"
        params = {"symbol": symbol, "symbols": symbols, "symbolStatus": symbol_status}

        return await self._make_request("GET", url, params=params)

    async def ticker(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        window_size: str | None = None,
        type: str | None = None,
        symbol_status: str | None = None,
    ) -> dict | list[dict]:
        """Статистика изменения цен в скользящем окне.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#rolling-window-price-change-statistics
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker"
        params = {
            "symbol": symbol,
            "symbols": symbols,
            "windowSize": window_size,
            "type": type,
            "symbolStatus": symbol_status,
        }

        return await self._make_request("GET", url, params=params)

    async def execution_rules(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        symbol_status: str | None = None,
    ) -> dict:
        """Получение правил исполнения ордеров (ценовые ограничения) по символам.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/general#execution-rules
        """
        url = self._BASE_SPOT_URL + "/api/v3/executionRules"
        params = {"symbol": symbol, "symbols": symbols, "symbolStatus": symbol_status}

        return await self._make_request("GET", url, params=params)

    async def historical_block_trades(
        self,
        symbol: str,
        from_id: int,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение исторических блочных сделок.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#historical-block-trades
        """
        url = self._BASE_SPOT_URL + "/api/v3/historicalBlockTrades"
        params = {"symbol": symbol, "fromId": from_id, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def reference_price(self, symbol: str) -> dict:
        """Получение референсной цены символа.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price
        """
        url = self._BASE_SPOT_URL + "/api/v3/referencePrice"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def reference_price_calculation(
        self,
        symbol: str,
        symbol_status: str | None = None,
    ) -> dict:
        """Получение способа расчёта референсной цены символа.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market#reference-price-calculation
        """
        url = self._BASE_SPOT_URL + "/api/v3/referencePrice/calculation"
        params = {"symbol": symbol, "symbolStatus": symbol_status}

        return await self._make_request("GET", url, params=params)

    # topic: trading endpoints

    async def order_create(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike | None = None,
        quote_order_qty: NumberLike | None = None,
        price: NumberLike | None = None,
        stop_price: NumberLike | None = None,
        time_in_force: str | None = None,
        new_client_order_id: str | None = None,
        iceberg_qty: NumberLike | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        trailing_delta: int | None = None,
        peg_price_type: str | None = None,
        peg_offset_value: int | None = None,
        peg_offset_type: str | None = None,
        quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание нового ордера на спот-рынке.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#new-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
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
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "trailingDelta": trailing_delta,
            "pegPriceType": peg_price_type,
            "pegOffsetValue": peg_offset_value,
            "pegOffsetType": peg_offset_type,
            "quoteNotionalLimit": quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_test(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike | None = None,
        quote_order_qty: NumberLike | None = None,
        price: NumberLike | None = None,
        stop_price: NumberLike | None = None,
        time_in_force: str | None = None,
        new_client_order_id: str | None = None,
        iceberg_qty: NumberLike | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        trailing_delta: int | None = None,
        peg_price_type: str | None = None,
        peg_offset_value: int | None = None,
        peg_offset_type: str | None = None,
        quote_notional_limit: NumberLike | None = None,
        compute_commission_rates: bool | None = None,
    ) -> dict:
        """Тестирование нового ордера (не выполняется реально).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#test-new-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order/test"
        params = {
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
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "trailingDelta": trailing_delta,
            "pegPriceType": peg_price_type,
            "pegOffsetValue": peg_offset_value,
            "pegOffsetType": peg_offset_type,
            "quoteNotionalLimit": quote_notional_limit,
            "computeCommissionRates": compute_commission_rates,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_cancel(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
        cancel_restrictions: str | None = None,
    ) -> dict:
        """Отмена активного ордера на спот-рынке.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#cancel-order-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
            "cancelRestrictions": cancel_restrictions,
        }

        return await self._make_request("DELETE", url, True, params=params)

    async def orders_cancel_all(self, symbol: str) -> list[dict]:
        """Отмена всех активных ордеров по символу.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#cancel-all-open-orders-on-a-symbol-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("DELETE", url, True, params=params)

    async def orders_open(self, symbol: str | None = None) -> list[dict]:
        """Получение всех активных ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#current-open-orders-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def oco_order_create(
        self,
        symbol: str,
        side: str,
        quantity: NumberLike,
        list_client_order_id: str | None = None,
        # ABOVE ORDER
        above_type: str = "TAKE_PROFIT_LIMIT",
        above_client_order_id: str | None = None,
        above_price: NumberLike | None = None,
        above_stop_price: NumberLike | None = None,
        above_trailing_delta: int | None = None,
        above_time_in_force: str | None = None,
        above_iceberg_qty: NumberLike | None = None,
        above_strategy_id: int | None = None,
        above_strategy_type: int | None = None,
        # BELOW ORDER
        below_type: str = "STOP_LOSS_LIMIT",
        below_client_order_id: str | None = None,
        below_price: NumberLike | None = None,
        below_stop_price: NumberLike | None = None,
        below_trailing_delta: int | None = None,
        below_time_in_force: str | None = None,
        below_iceberg_qty: NumberLike | None = None,
        below_strategy_id: int | None = None,
        below_strategy_type: int | None = None,
        # EXTRA
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        above_peg_price_type: str | None = None,
        above_peg_offset_type: str | None = None,
        above_peg_offset_value: int | None = None,
        above_quote_notional_limit: NumberLike | None = None,
        below_peg_price_type: str | None = None,
        below_peg_offset_type: str | None = None,
        below_peg_offset_value: int | None = None,
        below_quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание OCO ордера (новая версия).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/trading-endpoints#new-order-list---oco-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList/oco"

        params = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "listClientOrderId": list_client_order_id,
            # ABOVE
            "aboveType": above_type,
            "aboveClientOrderId": above_client_order_id,
            "abovePrice": above_price,
            "aboveStopPrice": above_stop_price,
            "aboveTrailingDelta": above_trailing_delta,
            "aboveTimeInForce": above_time_in_force,
            "aboveIcebergQty": above_iceberg_qty,
            "aboveStrategyId": above_strategy_id,
            "aboveStrategyType": above_strategy_type,
            # BELOW
            "belowType": below_type,
            "belowClientOrderId": below_client_order_id,
            "belowPrice": below_price,
            "belowStopPrice": below_stop_price,
            "belowTrailingDelta": below_trailing_delta,
            "belowTimeInForce": below_time_in_force,
            "belowIcebergQty": below_iceberg_qty,
            "belowStrategyId": below_strategy_id,
            "belowStrategyType": below_strategy_type,
            "abovePegPriceType": above_peg_price_type,
            "abovePegOffsetType": above_peg_offset_type,
            "abovePegOffsetValue": above_peg_offset_value,
            "aboveQuoteNotionalLimit": above_quote_notional_limit,
            "belowPegPriceType": below_peg_price_type,
            "belowPegOffsetType": below_peg_offset_type,
            "belowPegOffsetValue": below_peg_offset_value,
            "belowQuoteNotionalLimit": below_quote_notional_limit,
            # EXTRA
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
        }

        return await self._make_request("POST", url, True, params=params)

    async def oco_order_cancel(
        self,
        symbol: str,
        order_list_id: int | None = None,
        list_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
    ) -> dict:
        """Отмена списка ордеров (OCO, OTO, OTOCO, OPO, OPOCO).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#cancel-oco-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList"
        params = {
            "symbol": symbol,
            "orderListId": order_list_id,
            "listClientOrderId": list_client_order_id,
            "newClientOrderId": new_client_order_id,
        }

        return await self._make_request("DELETE", url, True, params=params)

    async def oco_order_get(
        self, order_list_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Получение информации о списке ордеров (OCO, OTO, OTOCO, OPO, OPOCO).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-oco-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList"
        params = {
            "orderListId": order_list_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def oco_orders_all(
        self,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех списков ордеров (OCO, OTO, OTOCO, OPO, OPOCO).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-all-oco-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/allOrderList"
        params = {
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def oco_orders_open(self) -> list[dict]:
        """Получение активных списков ордеров (OCO, OTO, OTOCO, OPO, OPOCO).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-open-oco-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrderList"

        return await self._make_request("GET", url, True)

    async def order_cancel_replace(
        self,
        symbol: str,
        side: str,
        type: str,
        cancel_replace_mode: str,
        time_in_force: str | None = None,
        quantity: NumberLike | None = None,
        quote_order_qty: NumberLike | None = None,
        price: NumberLike | None = None,
        cancel_new_client_order_id: str | None = None,
        cancel_orig_client_order_id: str | None = None,
        cancel_order_id: int | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        stop_price: NumberLike | None = None,
        trailing_delta: int | None = None,
        iceberg_qty: NumberLike | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        cancel_restrictions: str | None = None,
        order_rate_limit_exceeded_mode: str | None = None,
        peg_price_type: str | None = None,
        peg_offset_value: int | None = None,
        peg_offset_type: str | None = None,
        quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Отмена существующего ордера и создание нового.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-cancel-replace
        """
        url = self._BASE_SPOT_URL + "/api/v3/order/cancelReplace"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "cancelReplaceMode": cancel_replace_mode,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "quoteOrderQty": quote_order_qty,
            "price": price,
            "cancelNewClientOrderId": cancel_new_client_order_id,
            "cancelOrigClientOrderId": cancel_orig_client_order_id,
            "cancelOrderId": cancel_order_id,
            "newClientOrderId": new_client_order_id,
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "stopPrice": stop_price,
            "trailingDelta": trailing_delta,
            "icebergQty": iceberg_qty,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "cancelRestrictions": cancel_restrictions,
            "orderRateLimitExceededMode": order_rate_limit_exceeded_mode,
            "pegPriceType": peg_price_type,
            "pegOffsetValue": peg_offset_value,
            "pegOffsetType": peg_offset_type,
            "quoteNotionalLimit": quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_amend_keep_priority(
        self,
        symbol: str,
        new_qty: NumberLike,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        new_client_order_id: str | None = None,
    ) -> dict:
        """Уменьшение количества в ордере с сохранением приоритета в очереди.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-amend-keep-priority
        """
        url = self._BASE_SPOT_URL + "/api/v3/order/amend/keepPriority"
        params = {
            "symbol": symbol,
            "newQty": new_qty,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "newClientOrderId": new_client_order_id,
        }

        return await self._make_request("PUT", url, True, params=params)

    async def order_list_oto_create(
        self,
        symbol: str,
        working_type: str,
        working_side: str,
        working_price: NumberLike,
        working_quantity: NumberLike,
        pending_type: str,
        pending_side: str,
        pending_quantity: NumberLike,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: NumberLike | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_client_order_id: str | None = None,
        pending_price: NumberLike | None = None,
        pending_stop_price: NumberLike | None = None,
        pending_trailing_delta: NumberLike | None = None,
        pending_iceberg_qty: NumberLike | None = None,
        pending_time_in_force: str | None = None,
        pending_strategy_id: int | None = None,
        pending_strategy_type: int | None = None,
        pending_peg_price_type: str | None = None,
        pending_peg_offset_type: str | None = None,
        pending_peg_offset_value: int | None = None,
        working_quote_notional_limit: NumberLike | None = None,
        pending_quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание списка ордеров OTO (one-triggers-the-other).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-oto
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList/oto"
        params = {
            "symbol": symbol,
            "workingType": working_type,
            "workingSide": working_side,
            "workingPrice": working_price,
            "workingQuantity": working_quantity,
            "pendingType": pending_type,
            "pendingSide": pending_side,
            "pendingQuantity": pending_quantity,
            "listClientOrderId": list_client_order_id,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "workingClientOrderId": working_client_order_id,
            "workingIcebergQty": working_iceberg_qty,
            "workingTimeInForce": working_time_in_force,
            "workingStrategyId": working_strategy_id,
            "workingStrategyType": working_strategy_type,
            "workingPegPriceType": working_peg_price_type,
            "workingPegOffsetType": working_peg_offset_type,
            "workingPegOffsetValue": working_peg_offset_value,
            "pendingClientOrderId": pending_client_order_id,
            "pendingPrice": pending_price,
            "pendingStopPrice": pending_stop_price,
            "pendingTrailingDelta": pending_trailing_delta,
            "pendingIcebergQty": pending_iceberg_qty,
            "pendingTimeInForce": pending_time_in_force,
            "pendingStrategyId": pending_strategy_id,
            "pendingStrategyType": pending_strategy_type,
            "pendingPegPriceType": pending_peg_price_type,
            "pendingPegOffsetType": pending_peg_offset_type,
            "pendingPegOffsetValue": pending_peg_offset_value,
            "workingQuoteNotionalLimit": working_quote_notional_limit,
            "pendingQuoteNotionalLimit": pending_quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_list_otoco_create(
        self,
        symbol: str,
        working_type: str,
        working_side: str,
        working_price: NumberLike,
        working_quantity: NumberLike,
        pending_side: str,
        pending_quantity: NumberLike,
        pending_above_type: str,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: NumberLike | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_above_client_order_id: str | None = None,
        pending_above_price: NumberLike | None = None,
        pending_above_stop_price: NumberLike | None = None,
        pending_above_trailing_delta: NumberLike | None = None,
        pending_above_iceberg_qty: NumberLike | None = None,
        pending_above_time_in_force: str | None = None,
        pending_above_strategy_id: int | None = None,
        pending_above_strategy_type: int | None = None,
        pending_above_peg_price_type: str | None = None,
        pending_above_peg_offset_type: str | None = None,
        pending_above_peg_offset_value: int | None = None,
        pending_below_type: str | None = None,
        pending_below_client_order_id: str | None = None,
        pending_below_price: NumberLike | None = None,
        pending_below_stop_price: NumberLike | None = None,
        pending_below_trailing_delta: NumberLike | None = None,
        pending_below_iceberg_qty: NumberLike | None = None,
        pending_below_time_in_force: str | None = None,
        pending_below_strategy_id: int | None = None,
        pending_below_strategy_type: int | None = None,
        pending_below_peg_price_type: str | None = None,
        pending_below_peg_offset_type: str | None = None,
        pending_below_peg_offset_value: int | None = None,
        working_quote_notional_limit: NumberLike | None = None,
        pending_above_quote_notional_limit: NumberLike | None = None,
        pending_below_quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание списка ордеров OTOCO (one-triggers-one-cancels-the-other).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-otoco
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList/otoco"
        params = {
            "symbol": symbol,
            "workingType": working_type,
            "workingSide": working_side,
            "workingPrice": working_price,
            "workingQuantity": working_quantity,
            "pendingSide": pending_side,
            "pendingQuantity": pending_quantity,
            "pendingAboveType": pending_above_type,
            "listClientOrderId": list_client_order_id,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "workingClientOrderId": working_client_order_id,
            "workingIcebergQty": working_iceberg_qty,
            "workingTimeInForce": working_time_in_force,
            "workingStrategyId": working_strategy_id,
            "workingStrategyType": working_strategy_type,
            "workingPegPriceType": working_peg_price_type,
            "workingPegOffsetType": working_peg_offset_type,
            "workingPegOffsetValue": working_peg_offset_value,
            "pendingAboveClientOrderId": pending_above_client_order_id,
            "pendingAbovePrice": pending_above_price,
            "pendingAboveStopPrice": pending_above_stop_price,
            "pendingAboveTrailingDelta": pending_above_trailing_delta,
            "pendingAboveIcebergQty": pending_above_iceberg_qty,
            "pendingAboveTimeInForce": pending_above_time_in_force,
            "pendingAboveStrategyId": pending_above_strategy_id,
            "pendingAboveStrategyType": pending_above_strategy_type,
            "pendingAbovePegPriceType": pending_above_peg_price_type,
            "pendingAbovePegOffsetType": pending_above_peg_offset_type,
            "pendingAbovePegOffsetValue": pending_above_peg_offset_value,
            "pendingBelowType": pending_below_type,
            "pendingBelowClientOrderId": pending_below_client_order_id,
            "pendingBelowPrice": pending_below_price,
            "pendingBelowStopPrice": pending_below_stop_price,
            "pendingBelowTrailingDelta": pending_below_trailing_delta,
            "pendingBelowIcebergQty": pending_below_iceberg_qty,
            "pendingBelowTimeInForce": pending_below_time_in_force,
            "pendingBelowStrategyId": pending_below_strategy_id,
            "pendingBelowStrategyType": pending_below_strategy_type,
            "pendingBelowPegPriceType": pending_below_peg_price_type,
            "pendingBelowPegOffsetType": pending_below_peg_offset_type,
            "pendingBelowPegOffsetValue": pending_below_peg_offset_value,
            "workingQuoteNotionalLimit": working_quote_notional_limit,
            "pendingAboveQuoteNotionalLimit": pending_above_quote_notional_limit,
            "pendingBelowQuoteNotionalLimit": pending_below_quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_list_opo_create(
        self,
        symbol: str,
        working_type: str,
        working_side: str,
        working_price: NumberLike,
        working_quantity: NumberLike,
        pending_type: str,
        pending_side: str,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: NumberLike | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_client_order_id: str | None = None,
        pending_price: NumberLike | None = None,
        pending_stop_price: NumberLike | None = None,
        pending_trailing_delta: NumberLike | None = None,
        pending_iceberg_qty: NumberLike | None = None,
        pending_time_in_force: str | None = None,
        pending_strategy_id: int | None = None,
        pending_strategy_type: int | None = None,
        pending_peg_price_type: str | None = None,
        pending_peg_offset_type: str | None = None,
        pending_peg_offset_value: int | None = None,
        working_quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание списка ордеров OPO (one-pays-the-other).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opo
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList/opo"
        params = {
            "symbol": symbol,
            "workingType": working_type,
            "workingSide": working_side,
            "workingPrice": working_price,
            "workingQuantity": working_quantity,
            "pendingType": pending_type,
            "pendingSide": pending_side,
            "listClientOrderId": list_client_order_id,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "workingClientOrderId": working_client_order_id,
            "workingIcebergQty": working_iceberg_qty,
            "workingTimeInForce": working_time_in_force,
            "workingStrategyId": working_strategy_id,
            "workingStrategyType": working_strategy_type,
            "workingPegPriceType": working_peg_price_type,
            "workingPegOffsetType": working_peg_offset_type,
            "workingPegOffsetValue": working_peg_offset_value,
            "pendingClientOrderId": pending_client_order_id,
            "pendingPrice": pending_price,
            "pendingStopPrice": pending_stop_price,
            "pendingTrailingDelta": pending_trailing_delta,
            "pendingIcebergQty": pending_iceberg_qty,
            "pendingTimeInForce": pending_time_in_force,
            "pendingStrategyId": pending_strategy_id,
            "pendingStrategyType": pending_strategy_type,
            "pendingPegPriceType": pending_peg_price_type,
            "pendingPegOffsetType": pending_peg_offset_type,
            "pendingPegOffsetValue": pending_peg_offset_value,
            "workingQuoteNotionalLimit": working_quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_list_opoco_create(
        self,
        symbol: str,
        working_type: str,
        working_side: str,
        working_price: NumberLike,
        working_quantity: NumberLike,
        pending_side: str,
        pending_above_type: str,
        list_client_order_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        working_client_order_id: str | None = None,
        working_iceberg_qty: NumberLike | None = None,
        working_time_in_force: str | None = None,
        working_strategy_id: int | None = None,
        working_strategy_type: int | None = None,
        working_peg_price_type: str | None = None,
        working_peg_offset_type: str | None = None,
        working_peg_offset_value: int | None = None,
        pending_above_client_order_id: str | None = None,
        pending_above_price: NumberLike | None = None,
        pending_above_stop_price: NumberLike | None = None,
        pending_above_trailing_delta: NumberLike | None = None,
        pending_above_iceberg_qty: NumberLike | None = None,
        pending_above_time_in_force: str | None = None,
        pending_above_strategy_id: int | None = None,
        pending_above_strategy_type: int | None = None,
        pending_above_peg_price_type: str | None = None,
        pending_above_peg_offset_type: str | None = None,
        pending_above_peg_offset_value: int | None = None,
        pending_below_type: str | None = None,
        pending_below_client_order_id: str | None = None,
        pending_below_price: NumberLike | None = None,
        pending_below_stop_price: NumberLike | None = None,
        pending_below_trailing_delta: NumberLike | None = None,
        pending_below_iceberg_qty: NumberLike | None = None,
        pending_below_time_in_force: str | None = None,
        pending_below_strategy_id: int | None = None,
        pending_below_strategy_type: int | None = None,
        pending_below_peg_price_type: str | None = None,
        pending_below_peg_offset_type: str | None = None,
        pending_below_peg_offset_value: int | None = None,
        working_quote_notional_limit: NumberLike | None = None,
    ) -> dict:
        """Создание списка ордеров OPOCO (one-pays-the-other-one-cancels-the-other).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#order-list-opoco
        """
        url = self._BASE_SPOT_URL + "/api/v3/orderList/opoco"
        params = {
            "symbol": symbol,
            "workingType": working_type,
            "workingSide": working_side,
            "workingPrice": working_price,
            "workingQuantity": working_quantity,
            "pendingSide": pending_side,
            "pendingAboveType": pending_above_type,
            "listClientOrderId": list_client_order_id,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "workingClientOrderId": working_client_order_id,
            "workingIcebergQty": working_iceberg_qty,
            "workingTimeInForce": working_time_in_force,
            "workingStrategyId": working_strategy_id,
            "workingStrategyType": working_strategy_type,
            "workingPegPriceType": working_peg_price_type,
            "workingPegOffsetType": working_peg_offset_type,
            "workingPegOffsetValue": working_peg_offset_value,
            "pendingAboveClientOrderId": pending_above_client_order_id,
            "pendingAbovePrice": pending_above_price,
            "pendingAboveStopPrice": pending_above_stop_price,
            "pendingAboveTrailingDelta": pending_above_trailing_delta,
            "pendingAboveIcebergQty": pending_above_iceberg_qty,
            "pendingAboveTimeInForce": pending_above_time_in_force,
            "pendingAboveStrategyId": pending_above_strategy_id,
            "pendingAboveStrategyType": pending_above_strategy_type,
            "pendingAbovePegPriceType": pending_above_peg_price_type,
            "pendingAbovePegOffsetType": pending_above_peg_offset_type,
            "pendingAbovePegOffsetValue": pending_above_peg_offset_value,
            "pendingBelowType": pending_below_type,
            "pendingBelowClientOrderId": pending_below_client_order_id,
            "pendingBelowPrice": pending_below_price,
            "pendingBelowStopPrice": pending_below_stop_price,
            "pendingBelowTrailingDelta": pending_below_trailing_delta,
            "pendingBelowIcebergQty": pending_below_iceberg_qty,
            "pendingBelowTimeInForce": pending_below_time_in_force,
            "pendingBelowStrategyId": pending_below_strategy_id,
            "pendingBelowStrategyType": pending_below_strategy_type,
            "pendingBelowPegPriceType": pending_below_peg_price_type,
            "pendingBelowPegOffsetType": pending_below_peg_offset_type,
            "pendingBelowPegOffsetValue": pending_below_peg_offset_value,
            "workingQuoteNotionalLimit": working_quote_notional_limit,
        }

        return await self._make_request("POST", url, True, params=params)

    async def sor_order_create(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike,
        time_in_force: str | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        iceberg_qty: NumberLike | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
    ) -> dict:
        """Создание ордера через Smart Order Routing (SOR).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order
        """
        url = self._BASE_SPOT_URL + "/api/v3/sor/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "timeInForce": time_in_force,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "icebergQty": iceberg_qty,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
        }

        return await self._make_request("POST", url, True, params=params)

    async def sor_order_test(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike,
        compute_commission_rates: bool | None = None,
        time_in_force: str | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        strategy_id: int | None = None,
        strategy_type: int | None = None,
        iceberg_qty: NumberLike | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
    ) -> dict:
        """Тестирование ордера через Smart Order Routing (SOR).

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/trade#sor-order-test
        """
        url = self._BASE_SPOT_URL + "/api/v3/sor/order/test"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "computeCommissionRates": compute_commission_rates,
            "timeInForce": time_in_force,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "icebergQty": iceberg_qty,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
        }

        return await self._make_request("POST", url, True, params=params)

    # topic: account endpoints

    async def account(self, omit_zero_balances: bool | None = None) -> dict:
        """Получение информации об аккаунте (балансы, комиссии и т.д.).

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/account-endpoints#account-information-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/account"
        params = {"omitZeroBalances": omit_zero_balances}

        return await self._make_request("GET", url, True, params=params)

    async def order_get(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-order-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def all_orders(
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

        return await self._make_request("GET", url, True, params=params)

    async def all_open_orders(
        self,
        symbol: str | None = None,
    ) -> list[dict]:
        """Получение всех активных ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/account-endpoints#current-open-orders-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def my_trades(
        self,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение торговой истории аккаунта.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#account-trade-list-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/myTrades"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def order_count_usage(self) -> list[dict]:
        """Получение текущего использования лимитов ордеров.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-current-order-count-usage-trade
        """
        url = self._BASE_SPOT_URL + "/api/v3/rateLimit/order"

        return await self._make_request("GET", url, True)

    async def prevented_matches(
        self,
        symbol: str,
        prevented_match_id: int | None = None,
        order_id: int | None = None,
        from_prevented_match_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение предотвращенных совпадений.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-prevented-matches-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/myPreventedMatches"
        params = {
            "symbol": symbol,
            "preventedMatchId": prevented_match_id,
            "orderId": order_id,
            "fromPreventedMatchId": from_prevented_match_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def allocations(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        from_allocation_id: int | None = None,
        limit: int | None = None,
        order_id: int | None = None,
    ) -> list[dict]:
        """Получение распределений.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/spot-trading-endpoints#query-allocations-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/myAllocations"
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "fromAllocationId": from_allocation_id,
            "limit": limit,
            "orderId": order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def commission_rates(self, symbol: str) -> dict:
        """Получение комиссионных ставок.

        https://developers.binance.com/docs/binance-spot-api-docs/rest-api/account-endpoints#query-commission-rates-user_data
        """
        url = self._BASE_SPOT_URL + "/api/v3/account/commission"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def order_amendments(
        self,
        symbol: str,
        order_id: int,
        from_execution_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории изменений ордера.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#order-amendments
        """
        url = self._BASE_SPOT_URL + "/api/v3/order/amendments"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "fromExecutionId": from_execution_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def my_filters(self, symbol: str) -> dict:
        """Получение фильтров, применимых к аккаунту по символу.

        https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/account#my-filters
        """
        url = self._BASE_SPOT_URL + "/api/v3/myFilters"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    # topic: futures market data

    async def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ping"

        return await self._make_request("GET", url)

    async def futures_server_time(self) -> dict:
        """Получение текущего времени сервера.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Check-Server-Time#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/time"

        return await self._make_request("GET", url)

    async def futures_exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/exchangeInfo"

        return await self._make_request("GET", url)

    async def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book#request-parameters
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/depth"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Recent-Trades-List
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/trades"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Old-Trades-Lookup
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return await self._make_request("GET", url, params=params)

    async def futures_agg_trades(
        self,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение агрегированных сделок на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Aggregate-Trades-List
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/aggTrades"
        params = {
            "symbol": symbol,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/24hr"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker-v2
        """
        url = self._BASE_FUTURES_URL + "/fapi/v2/ticker/price"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_book_ticker(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лучших цен bid/ask в фьючерсной книге ордеров.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Order-Book-Ticker
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/bookTicker"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_klines(
        self,
        symbol: str,
        interval: str,
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

        return await self._make_request("GET", url, params=params)

    async def open_interest(self, symbol: str) -> dict:
        """Получение открытого интереса тикера.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openInterest"
        params = {"symbol": symbol}

        return await self._make_request(method="GET", url=url, params=params)

    async def futures_mark_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение ставки финансирования и цены маркировки.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Mark-Price
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/premiumIndex"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_funding_rate(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории ставок финансирования.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/fundingRate"
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_funding_info(self) -> list[dict]:
        """Получение информации о ставках финансирования.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Funding-Rate-Info
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/fundingInfo"

        return await self._make_request("GET", url)

    async def open_interest_hist(
        self,
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории открытого интереса.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics
        """
        url = self._BASE_FUTURES_URL + "/futures/data/openInterestHist"
        params = {
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_long_short_ratio_accounts(
        self,
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение соотношения лонг/шорт по аккаунтам.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio
        """
        url = self._BASE_FUTURES_URL + "/futures/data/topLongShortAccountRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_long_short_ratio_positions(
        self,
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение соотношения лонг/шорт по позициям.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio
        """
        url = self._BASE_FUTURES_URL + "/futures/data/topLongShortPositionRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_global_long_short_ratio(
        self,
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение глобального соотношения лонг/шорт.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Long-Short-Ratio
        """
        url = self._BASE_FUTURES_URL + "/futures/data/globalLongShortAccountRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_taker_long_short_ratio(
        self,
        symbol: str,
        period: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение соотношения лонг/шорт по тейкерам.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Taker-Buy-Sell-Volume
        """
        url = self._BASE_FUTURES_URL + "/futures/data/takerlongshortRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_composite_index(self, symbol: str | None = None) -> list[dict]:
        """Получение композитного индекса.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Composite-Index-Symbol-Information
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/indexInfo"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_api_trading_status(self, symbol: str | None = None) -> dict:
        """Получение статуса торгов API (количественные правила).

        https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Query-Current-API-trading-status
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/apiTradingStatus"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    # topic: futures account

    async def futures_account(self) -> dict:
        """Получение информации об аккаунте фьючерсов.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Account-Information-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/account"
        return await self._make_request("GET", url, True)

    async def futures_balance(self) -> list[dict]:
        """Получение баланса фьючерсного аккаунта.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/balance"

        return await self._make_request("GET", url, True)

    async def futures_multi_asset_mode(self, multi_assets_margin: bool | None = None) -> dict:
        """Изменение режима мультиактивной маржи.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Change-Multi-Assets-Mode
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/multiAssetsMargin"
        params = {"multiAssetsMargin": multi_assets_margin}

        return await self._make_request("POST", url, True, params=params)

    async def futures_multi_asset_mode_get(self) -> dict:
        """Получение режима мультиактивной маржи.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Current-Multi-Assets-Mode
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/multiAssetsMargin"

        return await self._make_request("GET", url, True)

    # topic: futures trade

    async def futures_order_create(
        self,
        symbol: str,
        side: str,
        type: str,
        quantity: NumberLike | None = None,
        reduce_only: bool | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stop_price: NumberLike | None = None,
        close_position: bool | None = None,
        activation_price: NumberLike | None = None,
        callback_rate: float | None = None,
        time_in_force: str | None = None,
        working_type: str | None = None,
        price_protect: bool | None = None,
        position_side: str | None = None,
        price_match: str | None = None,
        self_trade_prevention_mode: str | None = None,
        good_till_date: int | None = None,
        new_order_resp_type: str | None = None,
    ) -> dict:
        """Создание нового ордера на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/New-Order

        С 2025-12-09 условные ордера (`STOP_MARKET`, `TAKE_PROFIT_MARKET`, `STOP`, `TAKE_PROFIT`,
        `TRAILING_STOP_MARKET`) здесь отклоняются с ошибкой `-4120` — используйте
        `futures_algo_order_create`. Параметры `stop_price`, `close_position`, `activation_price`,
        `callback_rate`, `working_type`, `price_protect` оставлены для совместимости.
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "quantity": quantity,
            "reduceOnly": reduce_only,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stopPrice": stop_price,
            "closePosition": close_position,
            "activationPrice": activation_price,
            "callbackRate": callback_rate,
            "timeInForce": time_in_force,
            "workingType": working_type,
            "priceProtect": price_protect,
            "positionSide": position_side,
            "priceMatch": price_match,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "goodTillDate": good_till_date,
            "newOrderRespType": new_order_resp_type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_order_modify(
        self,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        symbol: str | None = None,
        side: str | None = None,
        quantity: NumberLike | None = None,
        price: NumberLike | None = None,
        price_match: str | None = None,
        modify_id: int | None = None,
        reduce_only: bool | None = None,
    ) -> dict:
        """Изменение ордера на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Modify-Order

        `reduce_only=True` только проверяет, что исходный ордер reduce-only (иначе `-5047`),
        и пропускает проверку `min_notional`. `modify_id` возвращается в ответе как есть.
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "priceMatch": price_match,
            "modifyId": modify_id,
            "reduceOnly": reduce_only,
        }

        return await self._make_request("PUT", url, True, params=params)

    async def futures_order_get(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Query-Order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_open(self, symbol: str | None = None) -> list[dict]:
        """Получение всех активных ордеров на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Current-All-Open-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_all(
        self,
        symbol: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех ордеров на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/All-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/allOrders"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_cancel_all(self, symbol: str) -> dict:
        """Отмена всех активных ордеров на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Cancel-All-Open-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/allOpenOrders"
        params = {"symbol": symbol}

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_countdown_cancel_all(
        self,
        symbol: str,
        countdown_time: int,
    ) -> dict:
        """Автоотмена всех активных ордеров через указанное время.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Auto-Cancel-All-Open-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/countdownCancelAll"
        params = {
            "symbol": symbol,
            "countdownTime": countdown_time,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_info(
        self,
        symbol: str | None = None,
        version: Literal["2", "3"] = "2",
    ) -> list[dict]:
        """Получение информации о позициях на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Position-Information-V2
        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Position-Information-V3
        """
        url = self._BASE_FUTURES_URL + f"/fapi/v{version}/positionRisk"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_my_trades(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
        order_id: int | None = None,
    ) -> list[dict]:
        """Получение истории торгов на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Account-Trade-List
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/userTrades"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_income(
        self,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории доходов на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Income-History
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/income"
        params = {
            "symbol": symbol,
            "incomeType": income_type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_leverage_change(self, symbol: str, leverage: int) -> dict:
        """Изменение кредитного плеча на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Initial-Leverage
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/leverage"
        params = {"symbol": symbol, "leverage": leverage}

        return await self._make_request("POST", url, True, params=params)

    async def futures_margin_type_change(self, symbol: str, margin_type: str) -> dict:
        """Изменение типа маржи на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Margin-Type
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/marginType"
        params = {"symbol": symbol, "marginType": margin_type}

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_margin_modify(
        self,
        symbol: str,
        position_side: str,
        amount: NumberLike,
        type: int,
    ) -> dict:
        """Изменение изолированной маржи позиции.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Modify-Isolated-Position-Margin
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionMargin"
        params = {
            "symbol": symbol,
            "positionSide": position_side,
            "amount": amount,
            "type": type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_margin_history(
        self,
        symbol: str,
        type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории изменений маржи позиции.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Get-Position-Margin-Change-History
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionMargin/history"
        params = {
            "symbol": symbol,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_commission_rate(self, symbol: str) -> dict:
        """Получение комиссионных ставок на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/User-Commission-Rate
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/commissionRate"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_adl_quantile(self, symbol: str | None = None) -> list[dict]:
        """Получение информации об автоматической ликвидации.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Position-ADL-Quantile-Estimation
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/adlQuantile"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_force_orders(
        self,
        symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории принудительных ордеров пользователя.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/User-s-Force-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/forceOrders"
        params = {
            "symbol": symbol,
            "autoCloseType": auto_close_type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_api_key_permissions(self) -> dict:
        """Получение разрешений API ключа (в т.ч. `enableFutures`).

        https://developers.binance.com/docs/wallet/account/api-key-permission
        """
        url = self._BASE_SPOT_URL + "/sapi/v1/account/apiRestrictions"

        return await self._make_request("GET", url, True)

    async def futures_order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на фьючерсном рынке.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Cancel-Order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("DELETE", url, params=params)

    async def futures_batch_orders_create(self, orders: list[dict]) -> list[dict]:
        """Создание множественных ордеров одновременно на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Place-Multiple-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/batchOrders"
        params = {"batchOrders": json.dumps(orders)}  # Нужен особый дамп

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_batch_orders_cancel(
        self,
        symbol: str,
        order_id_list: list[int] | None = None,
        orig_client_order_id_list: list[str] | None = None,
    ) -> list[dict]:
        """Отмена множественных ордеров на фьючерсах.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Cancel-Multiple-Orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/batchOrders"
        params = {"symbol": symbol}

        if order_id_list:
            params["orderIdList"] = json.dumps(order_id_list)  # Нужен особый дамп

        if orig_client_order_id_list:
            params["origClientOrderIdList"] = json.dumps(  # Нужен особый дамп
                orig_client_order_id_list
            )

        return await self._make_request("DELETE", url, signed=True, params=params)

    # topic: futures market data (extra)

    async def futures_rpi_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров с RPI-ордерами.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#rpi-order-book
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/rpiDepth"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_continuous_klines(
        self,
        pair: str,
        contract_type: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей непрерывного контракта.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#continuous-contract-kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/continuousKlines"
        params = {
            "pair": pair,
            "contractType": contract_type,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_index_price_klines(
        self,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей индексной цены.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#index-price-kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/indexPriceKlines"
        params = {
            "pair": pair,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_mark_price_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей маркировочной цены.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#mark-price-kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/markPriceKlines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_premium_index_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей премиального индекса.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#premium-index-kline-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/premiumIndexKlines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_adl_risk(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение уровня риска ADL по символам.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#adl-risk
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/symbolAdlRisk"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_trading_schedule(self) -> dict:
        """Получение расписания торговых сессий базовых рынков TradFi-контрактов.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#trading-schedule
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/tradingSchedule"

        return await self._make_request("GET", url)

    async def futures_index_constituents(self, symbol: str) -> dict:
        """Получение состава индексной цены.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-index-price-constituents
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/constituents"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_asset_index(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение индекса активов для режима Multi-Assets.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#asset-index
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/assetIndex"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_insurance_balance(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение снимка баланса страхового фонда.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#query-insurance-fund-balance-snapshot
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/insuranceBalance"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_basis(
        self,
        pair: str,
        contract_type: str,
        period: str,
        limit: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[dict]:
        """Получение базиса (разницы фьючерсной и индексной цены).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#basis
        """
        url = self._BASE_FUTURES_URL + "/futures/data/basis"
        params = {
            "pair": pair,
            "contractType": contract_type,
            "period": period,
            "limit": limit,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_delivery_price(self, pair: str) -> list[dict]:
        """Получение цен поставки квартальных контрактов.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#quarterly-contract-settlement-price
        """
        url = self._BASE_FUTURES_URL + "/futures/data/delivery-price"
        params = {"pair": pair}

        return await self._make_request("GET", url, params=params)

    # topic: futures account (extra)

    async def futures_account_config(self) -> dict:
        """Получение конфигурации фьючерсного аккаунта.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#futures-account-configuration
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/accountConfig"

        return await self._make_request("GET", url, True)

    async def futures_symbol_config(self, symbol: str | None = None) -> list[dict]:
        """Получение конфигурации символов аккаунта (плечо, тип маржи).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#symbol-configuration
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/symbolConfig"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_leverage_bracket(self, symbol: str | None = None) -> list[dict] | dict:
        """Получение ступеней номинала и плеча.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#notional-and-leverage-brackets
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/leverageBracket"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_position_mode(self) -> dict:
        """Получение текущего режима позиций (hedge / one-way).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-current-position-mode
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionSide/dual"

        return await self._make_request("GET", url, True)

    async def futures_position_mode_change(self, dual_side_position: bool) -> dict:
        """Изменение режима позиций (hedge / one-way).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#change-position-mode
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionSide/dual"
        params = {"dualSidePosition": dual_side_position}

        return await self._make_request("POST", url, True, params=params)

    async def futures_order_rate_limit(self) -> list[dict]:
        """Получение текущих лимитов на ордера.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#query-user-rate-limit
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/rateLimit/order"

        return await self._make_request("GET", url, True)

    async def futures_fee_burn(self) -> dict:
        """Получение статуса оплаты комиссии в BNB.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-bnb-burn-status
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/feeBurn"

        return await self._make_request("GET", url, True)

    async def futures_fee_burn_change(self, fee_burn: bool) -> dict:
        """Включение/выключение оплаты комиссии в BNB.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#toggle-bnb-burn-on-futures-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/feeBurn"
        params = {"feeBurn": fee_burn}

        return await self._make_request("POST", url, True, params=params)

    async def futures_income_download_id(self, start_time: int, end_time: int) -> dict:
        """Получение ID выгрузки истории транзакций.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-transaction-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/income/asyn"
        params = {"startTime": start_time, "endTime": end_time}

        return await self._make_request("GET", url, True, params=params)

    async def futures_income_download_link(self, download_id: str) -> dict:
        """Получение ссылки на выгрузку истории транзакций.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-transaction-history-download-link-by-id
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/income/asyn/id"
        params = {"downloadId": download_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_download_id(self, start_time: int, end_time: int) -> dict:
        """Получение ID выгрузки истории ордеров.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-order-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order/asyn"
        params = {"startTime": start_time, "endTime": end_time}

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_download_link(self, download_id: str) -> dict:
        """Получение ссылки на выгрузку истории ордеров.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-order-history-download-link-by-id
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order/asyn/id"
        params = {"downloadId": download_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_trades_download_id(self, start_time: int, end_time: int) -> dict:
        """Получение ID выгрузки истории сделок.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-download-id-for-futures-trade-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/trade/asyn"
        params = {"startTime": start_time, "endTime": end_time}

        return await self._make_request("GET", url, True, params=params)

    async def futures_trades_download_link(self, download_id: str) -> dict:
        """Получение ссылки на выгрузку истории сделок.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/account#get-futures-trade-download-link-by-id
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/trade/asyn/id"
        params = {"downloadId": download_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_pm_account_info(self, asset: str) -> dict:
        """Получение информации об аккаунте Classic Portfolio Margin.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/portfolio-margin-endpoints#classic-portfolio-margin-account-information
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/pmAccountInfo"
        params = {"asset": asset}

        return await self._make_request("GET", url, True, params=params)

    # topic: futures trade (extra)

    async def futures_order_test(
        self,
        symbol: str,
        side: str,
        type: str,
        position_side: str | None = None,
        reduce_only: bool | None = None,
        quantity: NumberLike | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stop_price: NumberLike | None = None,
        close_position: bool | None = None,
        activation_price: NumberLike | None = None,
        callback_rate: NumberLike | None = None,
        time_in_force: str | None = None,
        working_type: str | None = None,
        price_protect: bool | None = None,
        new_order_resp_type: str | None = None,
        price_match: str | None = None,
        self_trade_prevention_mode: str | None = None,
        good_till_date: int | None = None,
    ) -> dict:
        """Тестирование нового ордера на фьючерсах (не выполняется реально).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#test-order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order/test"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "positionSide": position_side,
            "reduceOnly": reduce_only,
            "quantity": quantity,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stopPrice": stop_price,
            "closePosition": close_position,
            "activationPrice": activation_price,
            "callbackRate": callback_rate,
            "timeInForce": time_in_force,
            "workingType": working_type,
            "priceProtect": price_protect,
            "newOrderRespType": new_order_resp_type,
            "priceMatch": price_match,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "goodTillDate": good_till_date,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_open_order_get(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение активного ордера на фьючерсах.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#query-current-open-order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openOrder"
        params = {"symbol": symbol, "orderId": order_id, "origClientOrderId": orig_client_order_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_order_amendments(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории изменений ордера на фьючерсах.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#get-order-modify-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/orderAmendment"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_tradfi_perps_contract(self) -> dict:
        """Подписание соглашения для торговли TradFi-контрактами.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#futures-tradfi-perps-contract
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/stock/contract"

        return await self._make_request("POST", url, True)

    # topic: futures algo orders

    async def futures_algo_order_create(
        self,
        symbol: str,
        side: str,
        type: str,
        algo_type: str = "CONDITIONAL",
        position_side: str | None = None,
        time_in_force: str | None = None,
        quantity: NumberLike | None = None,
        price: NumberLike | None = None,
        trigger_price: NumberLike | None = None,
        working_type: str | None = None,
        price_match: str | None = None,
        close_position: bool | None = None,
        price_protect: bool | None = None,
        reduce_only: bool | None = None,
        activate_price: NumberLike | None = None,
        callback_rate: NumberLike | None = None,
        client_algo_id: str | None = None,
        new_order_resp_type: str | None = None,
        self_trade_prevention_mode: str | None = None,
        good_till_date: int | None = None,
    ) -> dict:
        """Создание условного (algo) ордера: TP/SL, стоп-лимит, трейлинг-стоп.

        С 2025-12-09 типы `STOP_MARKET`, `TAKE_PROFIT_MARKET`, `STOP`, `TAKE_PROFIT`,
        `TRAILING_STOP_MARKET` принимаются только здесь (на `/fapi/v1/order` — ошибка `-4120`).

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#new-algo-order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/algoOrder"
        params = {
            "algoType": algo_type,
            "symbol": symbol,
            "side": side,
            "type": type,
            "positionSide": position_side,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "price": price,
            "triggerPrice": trigger_price,
            "workingType": working_type,
            "priceMatch": price_match,
            "closePosition": close_position,
            "priceProtect": price_protect,
            "reduceOnly": reduce_only,
            "activatePrice": activate_price,
            "callbackRate": callback_rate,
            "clientAlgoId": client_algo_id,
            "newOrderRespType": new_order_resp_type,
            "selfTradePreventionMode": self_trade_prevention_mode,
            "goodTillDate": good_till_date,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_algo_order_cancel(
        self,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
    ) -> dict:
        """Отмена условного (algo) ордера.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#cancel-algo-order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/algoOrder"
        params = {"algoId": algo_id, "clientAlgoId": client_algo_id}

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_algo_order_get(
        self,
        algo_id: int | None = None,
        client_algo_id: str | None = None,
    ) -> dict:
        """Получение информации об условном (algo) ордере.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#query-algo-order
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/algoOrder"
        params = {"algoId": algo_id, "clientAlgoId": client_algo_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_algo_orders_cancel_all(self, symbol: str) -> dict:
        """Отмена всех активных условных (algo) ордеров по символу.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#cancel-all-algo-open-orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/algoOpenOrders"
        params = {"symbol": symbol}

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_algo_orders_open(
        self,
        algo_type: str | None = None,
        symbol: str | None = None,
        algo_id: int | None = None,
    ) -> list[dict]:
        """Получение активных условных (algo) ордеров.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#current-all-algo-open-orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openAlgoOrders"
        params = {"algoType": algo_type, "symbol": symbol, "algoId": algo_id}

        return await self._make_request("GET", url, True, params=params)

    async def futures_algo_orders_all(
        self,
        symbol: str,
        algo_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех условных (algo) ордеров.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/trade#query-all-algo-orders
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/allAlgoOrders"
        params = {
            "symbol": symbol,
            "algoId": algo_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    # topic: futures convert

    async def futures_convert_exchange_info(
        self,
        from_asset: str | None = None,
        to_asset: str | None = None,
    ) -> list[dict]:
        """Получение пар, доступных для конвертации.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#list-all-convert-pairs
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/convert/exchangeInfo"
        params = {"fromAsset": from_asset, "toAsset": to_asset}

        return await self._make_request("GET", url, params=params)

    async def futures_convert_get_quote(
        self,
        from_asset: str,
        to_asset: str,
        from_amount: NumberLike | None = None,
        to_amount: NumberLike | None = None,
        valid_time: str | None = None,
    ) -> dict:
        """Запрос котировки для конвертации.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#send-quote-request
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/convert/getQuote"
        params = {
            "fromAsset": from_asset,
            "toAsset": to_asset,
            "fromAmount": from_amount,
            "toAmount": to_amount,
            "validTime": valid_time,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_convert_accept_quote(self, quote_id: str) -> dict:
        """Принятие котировки для конвертации.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#accept-the-offered-quote
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/convert/acceptQuote"
        params = {"quoteId": quote_id}

        return await self._make_request("POST", url, True, params=params)

    async def futures_convert_order_status(
        self,
        order_id: str | None = None,
        quote_id: str | None = None,
    ) -> dict:
        """Получение статуса ордера конвертации.

        https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/convert#order-status
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/convert/orderStatus"
        params = {"orderId": order_id, "quoteId": quote_id}

        return await self._make_request("GET", url, True, params=params)

    # topic: user data streams

    async def listen_key(self) -> dict:
        """Создание ключа прослушивания (удалено Binance 2026-02-20, отвечает 410).

        https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/user-data-stream-endpoints-deprecated#start-user-data-stream-user_stream-deprecated
        """
        warnings.warn(
            _SPOT_LISTEN_KEY_REMOVED,
            DeprecationWarning,
            stacklevel=2,
        )
        url = self._BASE_SPOT_URL + "/api/v3/userDataStream"

        return await super()._make_request("POST", url, headers=self._get_headers("POST"))

    async def renew_listen_key(self, listen_key: str) -> dict:
        """Продление ключа прослушивания (удалено Binance 2026-02-20, отвечает 410).

        https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/user-data-stream-endpoints-deprecated#keepalive-user-data-stream-user_stream-deprecated
        """
        warnings.warn(
            _SPOT_LISTEN_KEY_REMOVED,
            DeprecationWarning,
            stacklevel=2,
        )
        url = self._BASE_SPOT_URL + "/api/v3/userDataStream"
        params = {"listenKey": listen_key}

        return await super()._make_request(
            "PUT", url, params=params, headers=self._get_headers("PUT")
        )

    async def close_listen_key(self, listen_key: str) -> dict:
        """Закрытие ключа прослушивания (удалено Binance 2026-02-20, отвечает 410).

        https://developers.binance.com/docs/binance-spot-api-docs/testnet/rest-api/user-data-stream-endpoints-deprecated#close-user-data-stream-user_stream-deprecated
        """
        warnings.warn(
            _SPOT_LISTEN_KEY_REMOVED,
            DeprecationWarning,
            stacklevel=2,
        )
        url = self._BASE_SPOT_URL + "/api/v3/userDataStream"
        params = {"listenKey": listen_key}

        return await super()._make_request(
            "DELETE", url, params=params, headers=self._get_headers("DELETE")
        )

    # topic: futures user data streams

    async def futures_listen_key(self) -> dict:
        """Создание ключа прослушивания для подключения к пользовательскому вебсокету.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams/Start-User-Data-Stream#api-description
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("POST", url, headers=self._get_headers("POST"))

    async def futures_renew_listen_key(self) -> dict:
        """Обновление ключа прослушивания для подключения к пользовательскому вебсокету.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("PUT", url, headers=self._get_headers("PUT"))

    async def futures_close_listen_key(self) -> dict:
        """Закрытие ключа прослушивания для подключения к пользовательскому вебсокету.

        https://developers.binance.com/docs/derivatives/usds-margined-futures/user-data-streams
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("DELETE", url, headers=self._get_headers("DELETE"))
