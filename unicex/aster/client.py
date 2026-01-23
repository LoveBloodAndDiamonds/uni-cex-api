__all__ = ["Client"]

import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Aster API."""

    _BASE_FUTURES_URL: str = "https://fapi.asterdex.com"
    """Базовый URL для REST API Aster Futures."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, method: RequestMethod) -> dict[str, str]:
        """Возвращает заголовки для запросов к Aster API."""
        headers = {"Accept": "application/json"}
        if self._api_key:  # type: ignore[attr-defined]
            headers["X-MBX-APIKEY"] = self._api_key  # type: ignore[attr-defined]
        if method in {"POST", "PUT", "DELETE"}:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    def _prepare_payload(
        self,
        *,
        method: RequestMethod,
        signed: bool,
        params: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Подготавливает параметры запроса."""
        params = filter_params(params) if params else {}
        headers = self._get_headers(method)

        if not signed:
            return {"params": params}, headers

        if not self.is_authorized():
            raise NotAuthorized("Api key and api secret is required to private endpoints")

        payload = {**params}
        payload["timestamp"] = int(time.time() * 1000)
        payload["recvWindow"] = self._RECV_WINDOW

        # Подпись формируем по query string без параметра signature.
        query_string = dict_to_query_string(payload)
        payload["signature"] = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
            "hex",
        )

        return payload, headers

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Aster API."""
        payload, headers = self._prepare_payload(method=method, signed=signed, params=params)

        if not signed:
            return await super()._make_request(method=method, url=url, headers=headers, **payload)

        return await super()._make_request(
            method=method,
            url=url,
            params=payload,
            headers=headers,
        )

    async def request(
        self, method: RequestMethod, url: str, params: dict, data: dict, signed: bool
    ) -> dict:
        """Выполняет запрос к произвольному endpoint Aster API.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation
        """
        return await self._make_request(method=method, url=url, params=params, signed=signed)

    # topic: futures market data endpoints

    async def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#test-connectivity
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ping"

        return await self._make_request("GET", url)

    async def futures_server_time(self) -> dict:
        """Получение серверного времени.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#check-server-time
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/time"

        return await self._make_request("GET", url)

    async def futures_exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#exchange-information
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/exchangeInfo"

        return await self._make_request("GET", url)

    async def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#order-book
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/depth"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#recent-trades-list
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/trades"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#old-trades-lookup-market_data
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

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#compressed-aggregate-trades-list
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

    async def futures_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#kline-candlestick-data
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

    async def futures_index_price_klines(
        self,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей по индексу цены.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#index-price-kline-candlestick-data
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
        """Получение свечей по марк-цене.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price-kline-candlestick-data
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

    async def futures_mark_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение ставки финансирования и цены маркировки.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price
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

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-funding-rate-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/fundingRate"
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#id-24hr-ticker-price-change-statistics
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/24hr"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#symbol-price-ticker
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/price"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_book_ticker(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лучших цен bid/ask в книге ордеров.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#symbol-order-book-ticker
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/bookTicker"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    # topic: futures account/trade endpoints

    async def futures_position_mode(self, dual_side_position: Literal["true", "false"]) -> dict:
        """Изменение режима позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-position-mode-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionSide/dual"
        params = {"dualSidePosition": dual_side_position}

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_mode_get(self) -> dict:
        """Получение текущего режима позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-current-position-mode-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/positionSide/dual"

        return await self._make_request("GET", url, True)

    async def futures_multi_asset_mode(self, multi_assets_margin: Literal["true", "false"]) -> dict:
        """Изменение режима мультиактивной маржи.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-multi-assets-mode-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/multiAssetsMargin"
        params = {"multiAssetsMargin": multi_assets_margin}

        return await self._make_request("POST", url, True, params=params)

    async def futures_multi_asset_mode_get(self) -> dict:
        """Получение режима мультиактивной маржи.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-current-multi-assets-mode-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/multiAssetsMargin"

        return await self._make_request("GET", url, True)

    async def futures_order_create(
        self,
        symbol: str,
        side: Literal["BUY", "SELL"],
        type: Literal[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ],
        position_side: Literal["BOTH", "LONG", "SHORT"] | None = None,
        time_in_force: str | None = None,
        quantity: NumberLike | None = None,
        reduce_only: Literal["true", "false"] | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stop_price: NumberLike | None = None,
        close_position: Literal["true", "false"] | None = None,
        activation_price: NumberLike | None = None,
        callback_rate: NumberLike | None = None,
        working_type: Literal["MARK_PRICE", "CONTRACT_PRICE"] | None = None,
        price_protect: Literal["TRUE", "FALSE"] | None = None,
        new_order_resp_type: str | None = None,
    ) -> dict:
        """Создание нового ордера на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#new-order-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "positionSide": position_side,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "reduceOnly": reduce_only,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stopPrice": stop_price,
            "closePosition": close_position,
            "activationPrice": activation_price,
            "callbackRate": callback_rate,
            "workingType": working_type,
            "priceProtect": price_protect,
            "newOrderRespType": new_order_resp_type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_batch_orders_create(self, orders: list[dict]) -> list[dict]:
        """Создание множественных ордеров одновременно на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#place-multiple-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/batchOrders"
        params = {
            "batchOrders": json.dumps(orders, separators=(",", ":")),
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_order_get(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#query-order-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на фьючерсном рынке.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-order-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_orders_cancel_all(self, symbol: str) -> dict:
        """Отмена всех активных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-all-open-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/allOpenOrders"
        params = {"symbol": symbol}

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_batch_orders_cancel(
        self,
        symbol: str,
        order_id_list: list[int] | None = None,
        orig_client_order_id_list: list[str] | None = None,
    ) -> list[dict]:
        """Отмена множественных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-multiple-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/batchOrders"
        params = {"symbol": symbol}

        if order_id_list:
            params["orderIdList"] = json.dumps(order_id_list, separators=(",", ":"))

        if orig_client_order_id_list:
            params["origClientOrderIdList"] = json.dumps(
                orig_client_order_id_list, separators=(",", ":")
            )

        return await self._make_request("DELETE", url, signed=True, params=params)

    async def futures_countdown_cancel_all(
        self,
        symbol: str,
        countdown_time: int,
    ) -> dict:
        """Автоотмена всех активных ордеров через указанное время.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#auto-cancel-all-open-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/countdownCancelAll"
        params = {
            "symbol": symbol,
            "countdownTime": countdown_time,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_order_open(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение активного ордера.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#query-current-open-order-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openOrder"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_open(self, symbol: str | None = None) -> list[dict]:
        """Получение всех активных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#current-all-open-orders-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_all(
        self,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-orders-user_data
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

    async def futures_balance(self) -> list[dict]:
        """Получение баланса фьючерсного аккаунта.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#futures-account-balance-v2-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v2/balance"

        return await self._make_request("GET", url, True)

    async def futures_account(self) -> dict:
        """Получение информации об аккаунте фьючерсов.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#account-information-v4-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v4/account"

        return await self._make_request("GET", url, True)

    async def futures_leverage_change(self, symbol: str, leverage: int) -> dict:
        """Изменение кредитного плеча на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-initial-leverage-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/leverage"
        params = {"symbol": symbol, "leverage": leverage}

        return await self._make_request("POST", url, True, params=params)

    async def futures_margin_type_change(self, symbol: str, margin_type: str) -> dict:
        """Изменение типа маржи на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-margin-type-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/marginType"
        params = {"symbol": symbol, "marginType": margin_type}

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_margin_modify(
        self,
        symbol: str,
        position_side: str | None,
        amount: NumberLike,
        type: int,
    ) -> dict:
        """Изменение изолированной маржи позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#modify-isolated-position-margin-trade
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

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-position-margin-change-history-trade
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

    async def futures_position_info(self, symbol: str | None = None) -> list[dict]:
        """Получение информации о позициях на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#position-information-v2-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v2/positionRisk"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_my_trades(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории торгов на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#account-trade-list-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/userTrades"
        params = {
            "symbol": symbol,
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

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-income-historyuser_data
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

    async def futures_leverage_brackets(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лимитов по плечу и нотионалу.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#notional-and-leverage-brackets-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/leverageBracket"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_adl_quantile(self, symbol: str | None = None) -> list[dict]:
        """Получение информации об автоматической ликвидации.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#position-adl-quantile-estimation-user_data
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

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#users-force-orders-user_data
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

    async def futures_commission_rate(self, symbol: str) -> dict:
        """Получение комиссионных ставок на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#user-commission-rate-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/commissionRate"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    # topic: futures user data streams

    async def futures_listen_key(self) -> dict:
        """Создание ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#start-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("POST", url, headers=self._get_headers("POST"))

    async def futures_renew_listen_key(self) -> dict:
        """Обновление ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#keepalive-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("PUT", url, headers=self._get_headers("PUT"))

    async def futures_close_listen_key(self) -> dict:
        """Закрытие ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#close-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/listenKey"

        return await super()._make_request("DELETE", url, headers=self._get_headers("DELETE"))

    async def open_interest(self) -> dict:
        """Секретный эндпоинт откопанный в недрах фронтенда asterdex.com разработчиком @RushanDev.

        Формат возвращаемых данных:
            ```python
            {'code': '000000',
             'message': None,
             'messageDetail': None,
             'data': [
                {
                'symbol': 'TRUTHUSDT',
                'baseAsset': 'TRUTH',
                'quoteAsset': 'USDT',
                'lastPrice': 0.0126301,
                'highPrice': 0.0138825,
                'lowPrice': 0.012459,
                'baseVolume': 2011775,
                'quoteVolume': 26613.48,
                'openInterest': 85333.69964392  // В USDT
                }, ...
            ]
        ]
        ```
        """
        url = "https://www.asterdex.com/bapi/future/v1/public/future/aster/ticker/pair"

        return await super()._make_request("GET", url, headers=self._get_headers("GET"))
