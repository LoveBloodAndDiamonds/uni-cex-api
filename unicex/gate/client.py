__all__ = ["Client"]

import hashlib
import hmac
import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import dict_to_query_string, filter_params


class Client(BaseClient):
    """Клиент для работы с Gateio API."""

    _BASE_URL: str = "https://api.gateio.ws"
    """Базовый URL для REST API Gate.io."""

    def _normalize_query_params(
        self,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Нормализует query-параметры для корректной передачи bool в Gate.io."""
        normalized: dict[str, Any] = {}

        for key, value in params.items():
            if isinstance(value, bool):
                normalized[key] = str(value).lower()
                continue

            normalized[key] = value

        return normalized

    def _prepare_request(
        self,
        *,
        method: RequestMethod,
        endpoint: str,
        signed: bool,
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None, dict[str, str]]:
        """Формирует параметры и заголовки для HTTP-запроса."""
        params = filter_params(params) if params else None
        params = self._normalize_query_params(params) if params else None
        data = filter_params(data) if data else None
        url = f"{self._BASE_URL}{endpoint}"

        timestamp = str(int(time.time()))
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Timestamp": timestamp,
        }
        if self._api_key:  # type: ignore[attr-defined]
            headers["KEY"] = self._api_key  # type: ignore[attr-defined]

        if not signed:
            return url, params, data, headers

        if not self.is_authorized():
            raise NotAuthorized("Api key and api secret is required to private endpoints")

        # Для Gate подпись должна считаться по точно такому же JSON,
        # который уйдет в aiohttp `json=...` (по умолчанию json.dumps без compact separators).
        payload_string = json.dumps(data) if data else ""
        query_string = dict_to_query_string(params) if params else ""
        hashed_payload = hashlib.sha512(payload_string.encode("utf-8")).hexdigest()
        signature_body = (
            f"{method.upper()}\n{endpoint}\n{query_string}\n{hashed_payload}\n{timestamp}"
        )
        signature = hmac.new(
            self._api_secret.encode("utf-8"),  # type: ignore[attr-defined]
            signature_body.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()
        headers["SIGN"] = signature
        return url, params, data, headers

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к Gate.io API."""
        url, params, data, headers = self._prepare_request(
            method=method,
            endpoint=endpoint,
            signed=signed,
            params=params,
            data=data,
        )
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    async def request(
        self,
        method: RequestMethod,
        endpoint: str,
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
        signed: bool,
    ) -> dict:
        """Специальный метод для выполнения произвольных REST-запросов.

        Параметры:
            method (`RequestMethod`): HTTP-метод запроса ("GET", "POST" и т.д.).
            endpoint (`str`): Относительный путь эндпоинта Gate.io API.
            params (`dict | None`): Query-параметры запроса.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ Gate.io API.
        """
        return await self._make_request(
            method=method,
            endpoint=endpoint,
            params=params,
            data=data,
            signed=signed,
        )

    # topic: Spot

    async def currencies(self) -> dict:
        """Получение информации о всех валютах.

        https://www.gate.com/docs/developers/apiv4/en/#query-all-currency-information
        """
        return await self._make_request("GET", "/api/v4/spot/currencies")

    async def currency(self, currency: str) -> dict:
        """Получение информации о конкретной валюте.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-currency-information
        """
        return await self._make_request("GET", f"/api/v4/spot/currencies/{currency}")

    async def currency_pairs(self) -> dict:
        """Получение списка поддерживаемых торговых пар.

        https://www.gate.com/docs/developers/apiv4/en/#query-all-supported-currency-pairs
        """
        return await self._make_request("GET", "/api/v4/spot/currency_pairs")

    async def currency_pair(self, currency_pair: str) -> dict:
        """Получение информации о конкретной торговой паре.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-currency-pair-details
        """
        return await self._make_request("GET", f"/api/v4/spot/currency_pairs/{currency_pair}")

    async def tickers(
        self,
        currency_pair: str | None = None,
        timezone: str | None = None,
    ) -> dict:
        """Получение информации о тикерах торговых пар.

        https://www.gate.com/docs/developers/apiv4/en/#get-currency-pair-ticker-information
        """
        params = {
            "currency_pair": currency_pair,
            "timezone": timezone,
        }

        return await self._make_request("GET", "/api/v4/spot/tickers", params=params)

    async def order_book(
        self,
        currency_pair: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool | None = None,
    ) -> dict:
        """Получение информации о стакане рынка.

        https://www.gate.com/docs/developers/apiv4/en/#get-market-depth-information
        """
        params = {
            "currency_pair": currency_pair,
            "interval": interval,
            "limit": limit,
            "with_id": with_id,
        }

        return await self._make_request("GET", "/api/v4/spot/order_book", params=params)

    async def trades(
        self,
        currency_pair: str,
        limit: int | None = None,
        last_id: str | None = None,
        reverse: bool | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        page: int | None = None,
    ) -> dict:
        """Получение списка рыночных сделок.

        https://www.gate.com/docs/developers/apiv4/en/#query-market-transaction-records
        """
        params = {
            "currency_pair": currency_pair,
            "limit": limit,
            "last_id": last_id,
            "reverse": reverse,
            "from": from_time,
            "to": to_time,
            "page": page,
        }

        return await self._make_request("GET", "/api/v4/spot/trades", params=params)

    async def candlesticks(
        self,
        currency_pair: str,
        limit: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        interval: str | None = None,
    ) -> dict:
        """Получение данных свечного графика.

        https://www.gate.com/docs/developers/apiv4/en/#market-k-line-chart
        """
        params = {
            "currency_pair": currency_pair,
            "limit": limit,
            "from": from_time,
            "to": to_time,
            "interval": interval,
        }

        return await self._make_request("GET", "/api/v4/spot/candlesticks", params=params)

    async def fee(self, currency_pair: str | None = None) -> dict:
        """Получение комиссий аккаунта по торговым парам.

        https://www.gate.com/docs/developers/apiv4/en/#query-account-fee-rates
        """
        params = {
            "currency_pair": currency_pair,
        }

        return await self._make_request("GET", "/api/v4/spot/fee", params=params, signed=True)

    async def batch_fee(self, currency_pairs: str) -> dict:
        """Получение комиссий аккаунта по нескольким торговым парам.

        https://www.gate.com/docs/developers/apiv4/en/#batch-query-account-fee-rates
        """
        params = {
            "currency_pairs": currency_pairs,
        }

        return await self._make_request("GET", "/api/v4/spot/batch_fee", params=params, signed=True)

    async def accounts(self, currency: str | None = None) -> dict:
        """Получение балансов спотовых аккаунтов.

        https://www.gate.com/docs/developers/apiv4/en/#list-spot-trading-accounts
        """
        params = {
            "currency": currency,
        }

        return await self._make_request("GET", "/api/v4/spot/accounts", params=params, signed=True)

    async def account_book(
        self,
        currency: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
        type: str | None = None,
        code: str | None = None,
    ) -> dict:
        """Получение истории транзакций спотового аккаунта.

        https://www.gate.com/docs/developers/apiv4/en/#query-spot-account-transaction-history
        """
        params = {
            "currency": currency,
            "from": from_time,
            "to": to_time,
            "page": page,
            "limit": limit,
            "type": type,
            "code": code,
        }

        return await self._make_request(
            "GET", "/api/v4/spot/account_book", params=params, signed=True
        )

    async def batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict:
        """Создание нескольких ордеров за один запрос.

        https://www.gate.com/docs/developers/apiv4/en/#batch-place-orders
        """
        # NOTE: Документация описывает тело запроса как массив ордеров.
        # Клиент Gate.io сериализует данные как объект с ключом "orders".
        data = {
            "orders": orders,
        }

        return await self._make_request("POST", "/api/v4/spot/batch_orders", data=data, signed=True)

    async def open_orders(
        self,
        page: int | None = None,
        limit: int | None = None,
        account: str | None = None,
    ) -> dict:
        """Получение списка всех открытых ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#list-all-open-orders
        """
        params = {
            "page": page,
            "limit": limit,
            "account": account,
        }

        return await self._make_request(
            "GET", "/api/v4/spot/open_orders", params=params, signed=True
        )

    async def cross_liquidate_orders(
        self,
        currency_pair: str,
        amount: NumberLike,
        price: NumberLike,
        text: str | None = None,
        action_mode: str | None = None,
    ) -> dict:
        """Создание ордера для закрытия позиции при отключённой перекрёстной торговле.

        https://www.gate.com/docs/developers/apiv4/en/#close-position-when-cross-currency-is-disabled
        """
        data = {
            "text": text,
            "currency_pair": currency_pair,
            "amount": amount,
            "price": price,
            "action_mode": action_mode,
        }

        return await self._make_request(
            "POST", "/api/v4/spot/cross_liquidate_orders", data=data, signed=True
        )

    async def create_order(
        self,
        currency_pair: str,
        side: str,
        amount: NumberLike,
        text: str | None = None,
        type: str | None = None,
        account: str | None = None,
        price: NumberLike | None = None,
        time_in_force: str | None = None,
        iceberg: str | None = None,
        auto_borrow: bool | None = None,
        auto_repay: bool | None = None,
        stp_act: str | None = None,
        fee_discount: str | None = None,
        action_mode: str | None = None,
    ) -> dict:
        """Создание нового ордера.

        https://www.gate.com/docs/developers/apiv4/en/#create-an-order
        """
        data = {
            "text": text,
            "currency_pair": currency_pair,
            "type": type,
            "account": account,
            "side": side,
            "amount": amount,
            "price": price,
            "time_in_force": time_in_force,
            "iceberg": iceberg,
            "auto_borrow": auto_borrow,
            "auto_repay": auto_repay,
            "stp_act": stp_act,
            "fee_discount": fee_discount,
            "action_mode": action_mode,
        }

        return await self._make_request("POST", "/api/v4/spot/orders", data=data, signed=True)

    async def orders(
        self,
        currency_pair: str,
        status: str,
        page: int | None = None,
        limit: int | None = None,
        account: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        side: str | None = None,
    ) -> dict:
        """Получение списка ордеров по статусу.

        https://www.gate.com/docs/developers/apiv4/en/#list-orders
        """
        params = {
            "currency_pair": currency_pair,
            "status": status,
            "page": page,
            "limit": limit,
            "account": account,
            "from": from_time,
            "to": to_time,
            "side": side,
        }

        return await self._make_request("GET", "/api/v4/spot/orders", params=params, signed=True)

    async def cancel_all_orders(
        self,
        currency_pair: str | None = None,
        side: str | None = None,
        account: str | None = None,
        action_mode: str | None = None,
        trade_quote: bool | None = None,
    ) -> dict:
        """Отмена всех открытых ордеров по заданным условиям.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-all-open-orders-in-specified-currency-pair
        """
        params = {
            "currency_pair": currency_pair,
            "side": side,
            "account": account,
            "action_mode": action_mode,
            "trade_quote": trade_quote,
        }

        return await self._make_request("DELETE", "/api/v4/spot/orders", params=params, signed=True)

    async def cancel_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict:
        """Отмена нескольких ордеров по списку идентификаторов.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-batch-orders-by-specified-id-list
        """
        # NOTE: Документация описывает тело запроса как массив объектов.
        # В текущей реализации данные оборачиваются в объект с ключом "orders".
        data = {
            "orders": orders,
        }

        return await self._make_request(
            "POST", "/api/v4/spot/cancel_batch_orders", data=data, signed=True
        )

    async def order(
        self,
        order_id: str,
        currency_pair: str | None = None,
        account: str | None = None,
    ) -> dict:
        """Получение информации о конкретном ордере.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-order-details
        """
        params = {
            "currency_pair": currency_pair,
            "account": account,
        }

        return await self._make_request(
            "GET", f"/api/v4/spot/orders/{order_id}", params=params, signed=True
        )

    async def amend_order(
        self,
        order_id: str,
        currency_pair: str | None = None,
        account: str | None = None,
        amount: NumberLike | None = None,
        price: NumberLike | None = None,
        amend_text: str | None = None,
        action_mode: str | None = None,
    ) -> dict:
        """Изменение параметров ордера.

        https://www.gate.com/docs/developers/apiv4/en/#amend-single-order
        """
        params = {
            "currency_pair": currency_pair,
            "account": account,
        }
        data = {
            "currency_pair": currency_pair,
            "account": account,
            "amount": amount,
            "price": price,
            "amend_text": amend_text,
            "action_mode": action_mode,
        }

        return await self._make_request(
            "PATCH",
            f"/api/v4/spot/orders/{order_id}",
            params=params,
            data=data,
            signed=True,
        )

    async def cancel_order(
        self,
        order_id: str,
        currency_pair: str,
        account: str | None = None,
        action_mode: str | None = None,
    ) -> dict:
        """Отмена конкретного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-single-order
        """
        params = {
            "currency_pair": currency_pair,
            "account": account,
            "action_mode": action_mode,
        }

        return await self._make_request(
            "DELETE",
            f"/api/v4/spot/orders/{order_id}",
            params=params,
            signed=True,
        )

    async def my_trades(
        self,
        currency_pair: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        order_id: str | None = None,
        account: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
    ) -> dict:
        """Получение личной истории сделок.

        https://www.gate.com/docs/developers/apiv4/en/#query-personal-trading-records
        """
        params = {
            "currency_pair": currency_pair,
            "limit": limit,
            "page": page,
            "order_id": order_id,
            "account": account,
            "from": from_time,
            "to": to_time,
        }

        return await self._make_request("GET", "/api/v4/spot/my_trades", params=params, signed=True)

    async def countdown_cancel_all(
        self,
        timeout: int,
        currency_pair: str | None = None,
    ) -> dict:
        """Настройка автоматической отмены ордеров по таймеру.

        https://www.gate.com/docs/developers/apiv4/en/#countdown-cancel-orders
        """
        data = {
            "timeout": timeout,
            "currency_pair": currency_pair,
        }

        return await self._make_request(
            "POST", "/api/v4/spot/countdown_cancel_all", data=data, signed=True
        )

    async def amend_batch_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict:
        """Изменение параметров нескольких ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#batch-modification-of-orders
        """
        # NOTE: Формат массива ордеров следует уточнить в зависимости от требований API.
        data = {
            "orders": orders,
        }

        return await self._make_request(
            "POST", "/api/v4/spot/amend_batch_orders", data=data, signed=True
        )

    async def insurance_history(
        self,
        business: str,
        currency: str,
        from_time: int,
        to_time: int,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории страхового фонда спотового рынка.

        https://www.gate.com/docs/developers/apiv4/en/#query-spot-insurance-fund-historical-data
        """
        params = {
            "business": business,
            "currency": currency,
            "from": from_time,
            "to": to_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request(
            "GET", "/api/v4/spot/insurance_history", params=params, signed=True
        )

    async def create_price_order(self, order: dict[str, Any]) -> dict:
        """Создание отложенного ордера с ценовым триггером.

        https://www.gate.com/docs/developers/apiv4/en/#create-price-triggered-order
        """
        return await self._make_request(
            "POST", "/api/v4/spot/price_orders", data=order, signed=True
        )

    async def price_orders(
        self,
        status: str,
        market: str | None = None,
        account: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """Получение списка активных отложенных ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#query-running-auto-order-list
        """
        params = {
            "status": status,
            "market": market,
            "account": account,
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request(
            "GET", "/api/v4/spot/price_orders", params=params, signed=True
        )

    async def cancel_price_orders(
        self,
        market: str | None = None,
        account: str | None = None,
    ) -> dict:
        """Отмена всех отложенных ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-all-auto-orders
        """
        params = {
            "market": market,
            "account": account,
        }

        return await self._make_request(
            "DELETE", "/api/v4/spot/price_orders", params=params, signed=True
        )

    async def price_order(self, order_id: str) -> dict:
        """Получение информации о конкретном отложенном ордере.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-auto-order-details
        """
        return await self._make_request("GET", f"/api/v4/spot/price_orders/{order_id}", signed=True)

    async def cancel_price_order(self, order_id: str) -> dict:
        """Отмена конкретного отложенного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-single-auto-order
        """
        return await self._make_request(
            "DELETE", f"/api/v4/spot/price_orders/{order_id}", signed=True
        )

    async def server_time(self) -> Any:
        """Получение серверного времени.

        https://www.gate.com/docs/developers/apiv4/en/#get-server-current-time
        """
        return await self._make_request("GET", "/api/v4/spot/time")

    async def rpi_order_book(
        self,
        currency_pair: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool | None = None,
    ) -> Any:
        """Получение книги ордеров с RPI-ордерами.

        https://www.gate.com/docs/developers/apiv4/en/#get-the-rpi-order-book
        """
        params = {
            "currency_pair": currency_pair,
            "interval": interval,
            "limit": limit,
            "with_id": with_id,
        }

        return await self._make_request("GET", "/api/v4/spot/rpi_order_book", params=params)

    async def pov_order_create(
        self,
        currency_pair: str,
        side: str,
        amount: str,
        participation_rate: int,
        ttl: str,
        limit_price: str | None = None,
        trigger_price: str | None = None,
        text: str | None = None,
    ) -> Any:
        """Создание POV-ордера (percentage-of-volume).

        https://www.gate.com/docs/developers/apiv4/en/#create-a-spot-percentage-of-volume-pov-strategy-order
        """
        data = {
            "currency_pair": currency_pair,
            "side": side,
            "amount": amount,
            "participation_rate": participation_rate,
            "ttl": ttl,
            "limit_price": limit_price,
            "trigger_price": trigger_price,
            "text": text,
        }

        return await self._make_request("POST", "/api/v4/spot/pov_orders", signed=True, data=data)

    async def pov_orders(
        self,
        status: str,
        currency_pair: str | None = None,
        side: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> Any:
        """Получение списка POV-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#list-spot-pov-orders
        """
        params = {
            "currency_pair": currency_pair,
            "status": status,
            "side": side,
            "page": page,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            "/api/v4/spot/pov_orders",
            signed=True,
            params=params,
        )

    async def pov_orders_cancel(self, currency_pair: str | None = None) -> Any:
        """Отмена POV-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-spot-pov-orders
        """
        params = {"currency_pair": currency_pair}

        return await self._make_request(
            "DELETE",
            "/api/v4/spot/pov_orders",
            signed=True,
            params=params,
        )

    async def pov_order(self, order_id: str) -> Any:
        """Получение POV-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#query-spot-pov-order-details
        """
        return await self._make_request("GET", f"/api/v4/spot/pov_orders/{order_id}", signed=True)

    async def pov_order_cancel(self, order_id: str) -> Any:
        """Отмена POV-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-a-spot-pov-order
        """
        return await self._make_request(
            "DELETE",
            f"/api/v4/spot/pov_orders/{order_id}",
            signed=True,
        )

    # topic: Futures

    async def futures_contracts(
        self,
        settle: Literal["usdt", "btc", "usd1"],
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict]:
        """Получение списка фьючерсных контрактов.

        https://www.gate.com/docs/developers/apiv4/en/#query-all-futures-contracts
        """
        params = {
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request("GET", f"/api/v4/futures/{settle}/contracts", params=params)

    async def futures_contract(self, settle: str, contract: str) -> dict:
        """Получение информации о конкретном фьючерсном контракте.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-contract-information
        """
        return await self._make_request("GET", f"/api/v4/futures/{settle}/contracts/{contract}")

    async def futures_order_book(
        self,
        settle: str,
        contract: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool | None = None,
    ) -> dict:
        """Получение информации о стакане фьючерсного рынка.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-market-depth-information
        """
        params = {
            "contract": contract,
            "interval": interval,
            "limit": limit,
            "with_id": with_id,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/order_book", params=params
        )

    async def futures_trades(
        self,
        settle: str,
        contract: str,
        limit: int | None = None,
        offset: int | None = None,
        last_id: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
    ) -> dict:
        """Получение списка рыночных сделок по фьючерсам.

        https://www.gate.com/docs/developers/apiv4/en/#futures-market-transaction-records
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
            "last_id": last_id,
            "from": from_time,
            "to": to_time,
        }

        return await self._make_request("GET", f"/api/v4/futures/{settle}/trades", params=params)

    async def futures_candlesticks(
        self,
        settle: str,
        contract: str,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
        timezone: str | None = None,
    ) -> dict:
        """Получение свечных данных по фьючерсному контракту.

        https://www.gate.com/docs/developers/apiv4/en/#futures-market-k-line-chart
        """
        params = {
            "contract": contract,
            "from": from_time,
            "to": to_time,
            "limit": limit,
            "interval": interval,
            "timezone": timezone,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/candlesticks", params=params
        )

    async def futures_premium_index(
        self,
        settle: str,
        contract: str,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
        interval: str | None = None,
    ) -> dict:
        """Получение данных премиум-индекса.

        https://www.gate.com/docs/developers/apiv4/en/#premium-index-k-line-chart
        """
        params = {
            "contract": contract,
            "from": from_time,
            "to": to_time,
            "limit": limit,
            "interval": interval,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/premium_index", params=params
        )

    async def futures_tickers(
        self,
        settle: str,
        contract: str | None = None,
    ) -> dict:
        """Получение торговой статистики по фьючерсам.

        https://www.gate.com/docs/developers/apiv4/en/#get-all-futures-trading-statistics
        """
        params = {
            "contract": contract,
        }

        return await self._make_request("GET", f"/api/v4/futures/{settle}/tickers", params=params)

    async def futures_funding_rate(
        self,
        settle: str,
        contract: str,
        limit: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
    ) -> dict:
        """Получение истории ставок финансирования.

        https://www.gate.com/docs/developers/apiv4/en/#futures-market-historical-funding-rate
        """
        params = {
            "contract": contract,
            "limit": limit,
            "from": from_time,
            "to": to_time,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/funding_rate", params=params
        )

    async def futures_insurance(
        self,
        settle: str,
        limit: int | None = None,
    ) -> dict:
        """Получение истории страхового фонда фьючерсного рынка.

        https://www.gate.com/docs/developers/apiv4/en/#futures-market-insurance-fund-history
        """
        params = {
            "limit": limit,
        }

        return await self._make_request("GET", f"/api/v4/futures/{settle}/insurance", params=params)

    async def futures_contract_stats(
        self,
        settle: str,
        contract: str,
        from_time: int | None = None,
        interval: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение статистики по фьючерсному контракту.

        https://www.gate.com/docs/developers/apiv4/en/#futures-statistics
        """
        params = {
            "contract": contract,
            "from": from_time,
            "interval": interval,
            "limit": limit,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/contract_stats", params=params
        )

    async def futures_index_constituents(self, settle: str, index: str) -> dict:
        """Получение состава индекса.

        https://www.gate.com/docs/developers/apiv4/en/#query-index-constituents
        """
        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/index_constituents/{index}"
        )

    async def futures_liq_orders(
        self,
        settle: str,
        contract: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории ликвидаций.

        https://www.gate.com/docs/developers/apiv4/en/#query-liquidation-order-history
        """
        params = {
            "contract": contract,
            "from": from_time,
            "to": to_time,
            "limit": limit,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/liq_orders", params=params
        )

    async def futures_risk_limit_tiers(
        self,
        settle: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """Получение лимитов риска по фьючерсным контрактам.

        https://www.gate.com/docs/developers/apiv4/en/#query-risk-limit-tiers
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/risk_limit_tiers", params=params
        )

    async def futures_accounts(self, settle: str) -> dict:
        """Получение информации о фьючерсном аккаунте.

        https://www.gate.com/docs/developers/apiv4/en/#get-futures-account
        """
        return await self._make_request("GET", f"/api/v4/futures/{settle}/accounts", signed=True)

    async def futures_account_book(
        self,
        settle: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        type_: str | None = None,
    ) -> dict:
        """Получение истории изменений фьючерсного аккаунта.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-account-change-history
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
            "from": from_time,
            "to": to_time,
            "type": type_,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/account_book", params=params, signed=True
        )

    async def futures_positions(
        self,
        settle: str,
        holding: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        positions_limit: int | None = None,
    ) -> dict:
        """Получение списка позиций пользователя.

        С 2026-07-02 (v4.106.104) лимит передаётся как `positions_limit` (1–100, без него —
        все позиции). `limit` оставлен для совместимости и уходит в оба параметра.

        https://www.gate.com/docs/developers/apiv4/en/#get-user-position-list
        """
        params = {
            "holding": holding,
            "positions_limit": positions_limit if positions_limit is not None else limit,
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/positions", params=params, signed=True
        )

    async def futures_position(
        self,
        settle: str,
        contract: str,
    ) -> dict:
        """Получение информации о позиции по контракту.

        https://www.gate.com/docs/developers/apiv4/en/#get-single-position-information
        """
        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/positions/{contract}", signed=True
        )

    async def futures_update_margin(
        self,
        settle: str,
        contract: str,
        change: str,
    ) -> dict:
        """Изменение маржи позиции.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-margin
        """
        params = {
            "change": change,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/positions/{contract}/margin",
            params=params,
            signed=True,
        )

    async def futures_update_leverage(
        self,
        settle: str,
        contract: str,
        leverage: str,
        cross_leverage_limit: str | None = None,
        pid: int | None = None,
    ) -> dict:
        """Изменение кредита позиции.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-leverage
        """
        params = {
            "leverage": leverage,
            "cross_leverage_limit": cross_leverage_limit,
            "pid": pid,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/positions/{contract}/leverage",
            params=params,
            signed=True,
        )

    async def futures_switch_cross_mode(
        self,
        settle: str,
        mode: str,
        contract: str,
    ) -> dict:
        """Переключение режима маржи позиции.

        https://www.gate.com/docs/developers/apiv4/en/#switch-position-margin-mode
        """
        data = {
            "mode": mode,
            "contract": contract,
        }

        return await self._make_request(
            "POST", f"/api/v4/futures/{settle}/positions/cross_mode", data=data, signed=True
        )

    async def futures_dual_comp_switch_cross_mode(
        self,
        settle: str,
        mode: str,
        contract: str,
    ) -> dict:
        """Переключение режима маржи в хедж-режиме.

        https://www.gate.com/docs/developers/apiv4/en/#switch-between-cross-and-isolated-margin-modes-under-hedge-mode
        """
        data = {
            "mode": mode,
            "contract": contract,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/dual_comp/positions/cross_mode",
            data=data,
            signed=True,
        )

    async def futures_update_risk_limit(
        self,
        settle: str,
        contract: str,
        risk_limit: str,
    ) -> dict:
        """Изменение лимита риска позиции.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-risk-limit
        """
        params = {
            "risk_limit": risk_limit,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/positions/{contract}/risk_limit",
            params=params,
            signed=True,
        )

    async def futures_set_dual_mode(
        self,
        settle: str,
        dual_mode: bool,
    ) -> dict:
        """Настройка режима двойных позиций.

        https://www.gate.com/docs/developers/apiv4/en/#set-position-mode
        """
        params = {
            "dual_mode": dual_mode,
        }

        return await self._make_request(
            "POST", f"/api/v4/futures/{settle}/dual_mode", params=params, signed=True
        )

    async def futures_dual_comp_position(
        self,
        settle: str,
        contract: str,
    ) -> dict:
        """Получение информации о позиции в двойном режиме.

        https://www.gate.com/docs/developers/apiv4/en/#get-position-information-in-dual-mode
        """
        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/dual_comp/positions/{contract}", signed=True
        )

    async def futures_dual_comp_update_margin(
        self,
        settle: str,
        contract: str,
        change: str,
        dual_side: str,
    ) -> dict:
        """Изменение маржи позиции в двойном режиме.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-margin-in-dual-mode
        """
        params = {
            "change": change,
            "dual_side": dual_side,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/dual_comp/positions/{contract}/margin",
            params=params,
            signed=True,
        )

    async def futures_dual_comp_update_leverage(
        self,
        settle: str,
        contract: str,
        leverage: str,
        cross_leverage_limit: str | None = None,
    ) -> dict:
        """Изменение плеча позиции в двойном режиме.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-leverage-in-dual-mode
        """
        params = {
            "leverage": leverage,
            "cross_leverage_limit": cross_leverage_limit,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/dual_comp/positions/{contract}/leverage",
            params=params,
            signed=True,
        )

    async def futures_dual_comp_update_risk_limit(
        self,
        settle: str,
        contract: str,
        risk_limit: str,
    ) -> dict:
        """Изменение лимита риска в двойном режиме.

        https://www.gate.com/docs/developers/apiv4/en/#update-position-risk-limit-in-dual-mode
        """
        params = {
            "risk_limit": risk_limit,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/dual_comp/positions/{contract}/risk_limit",
            params=params,
            signed=True,
        )

    async def futures_create_order(self, settle: str, order: dict[str, Any]) -> dict:
        """Создание фьючерсного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#place-futures-order
        """
        return await self._make_request(
            "POST", f"/api/v4/futures/{settle}/orders", data=order, signed=True
        )

    async def futures_orders(
        self,
        settle: str,
        status: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        last_id: str | None = None,
    ) -> dict:
        """Получение списка фьючерсных ордеров по статусу.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-order-list
        """
        params = {
            "contract": contract,
            "status": status,
            "limit": limit,
            "offset": offset,
            "last_id": last_id,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/orders", params=params, signed=True
        )

    async def futures_cancel_all_orders(
        self,
        settle: str,
        contract: str,
        side: str | None = None,
        exclude_reduce_only: bool | None = None,
        text: str | None = None,
        action_mode: str | None = None,
    ) -> dict:
        """Отмена всех открытых фьючерсных ордеров по контракту.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-all-orders-with-open-status
        """
        params = {
            "contract": contract,
            "side": side,
            "exclude_reduce_only": exclude_reduce_only,
            "text": text,
            "action_mode": action_mode,
        }

        return await self._make_request(
            "DELETE", f"/api/v4/futures/{settle}/orders", params=params, signed=True
        )

    async def futures_orders_timerange(
        self,
        settle: str,
        contract: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """Получение списка фьючерсных ордеров за период.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-order-list-by-time-range
        """
        params = {
            "contract": contract,
            "from": from_time,
            "to": to_time,
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/orders_timerange", params=params, signed=True
        )

    async def futures_create_orders_batch(
        self,
        settle: str,
        orders: list[dict[str, Any]],
    ) -> dict:
        """Создание нескольких фьючерсных ордеров за один запрос.

        https://www.gate.com/docs/developers/apiv4/en/#place-batch-futures-orders
        """
        # NOTE: Документация требует массив объектов ордеров, запрос сериализуется как JSON-массив.
        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/batch_orders",
            data=orders,  # type: ignore
            signed=True,
        )

    async def futures_order(
        self,
        settle: str,
        order_id: str,
    ) -> dict:
        """Получение информации о фьючерсном ордере.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-order-details
        """
        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/orders/{order_id}", signed=True
        )

    async def futures_cancel_order(
        self,
        settle: str,
        order_id: str,
        action_mode: str | None = None,
    ) -> dict:
        """Отмена конкретного фьючерсного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-single-order
        """
        params = {"action_mode": action_mode}

        return await self._make_request(
            "DELETE", f"/api/v4/futures/{settle}/orders/{order_id}", params=params, signed=True
        )

    async def futures_amend_order(
        self,
        settle: str,
        order_id: str,
        size: NumberLike | None = None,
        price: NumberLike | None = None,
        amend_text: str | None = None,
        text: str | None = None,
    ) -> dict:
        """Изменение параметров фьючерсного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#amend-single-order
        """
        data = {
            "size": size,
            "price": price,
            "amend_text": amend_text,
            "text": text,
        }

        return await self._make_request(
            "PUT",
            f"/api/v4/futures/{settle}/orders/{order_id}",
            data=data,
            signed=True,
        )

    async def futures_my_trades(
        self,
        settle: str,
        contract: str | None = None,
        order: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        last_id: str | None = None,
    ) -> dict:
        """Получение личной истории сделок по фьючерсам.

        https://www.gate.com/docs/developers/apiv4/en/#query-personal-trading-records
        """
        params = {
            "contract": contract,
            "order": order,
            "limit": limit,
            "offset": offset,
            "last_id": last_id,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/my_trades", params=params, signed=True
        )

    async def futures_my_trades_timerange(
        self,
        settle: str,
        contract: str | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        role: str | None = None,
    ) -> dict:
        """Получение личной истории сделок за период.

        https://www.gate.com/docs/developers/apiv4/en/#query-personal-trading-records-by-time-range
        """
        params = {
            "contract": contract,
            "from": from_time,
            "to": to_time,
            "limit": limit,
            "offset": offset,
            "role": role,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/my_trades_timerange", params=params, signed=True
        )

    async def futures_position_close(
        self,
        settle: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        side: str | None = None,
        pnl: str | None = None,
    ) -> dict:
        """Получение истории закрытых позиций.

        https://www.gate.com/docs/developers/apiv4/en/#query-position-close-history
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
            "from": from_time,
            "to": to_time,
            "side": side,
            "pnl": pnl,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/position_close", params=params, signed=True
        )

    async def futures_liquidates(
        self,
        settle: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        at: int | None = None,
    ) -> dict:
        """Получение истории ликвидаций аккаунта.

        https://www.gate.com/docs/developers/apiv4/en/#query-liquidation-history
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
            "from": from_time,
            "to": to_time,
            "at": at,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/liquidates", params=params, signed=True
        )

    async def futures_auto_deleverages(
        self,
        settle: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        from_time: int | None = None,
        to_time: int | None = None,
        at: int | None = None,
    ) -> dict:
        """Получение истории автоматического снижения плеча (ADL).

        https://www.gate.com/docs/developers/apiv4/en/#query-adl-auto-deleveraging-order-information
        """
        params = {
            "contract": contract,
            "limit": limit,
            "offset": offset,
            "from": from_time,
            "to": to_time,
            "at": at,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/auto_deleverages", params=params, signed=True
        )

    async def futures_countdown_cancel_all(
        self,
        settle: str,
        timeout: int,
        contract: str | None = None,
    ) -> dict:
        """Настройка таймера автоматической отмены фьючерсных ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#countdown-cancel-orders
        """
        data = {
            "timeout": timeout,
            "contract": contract,
        }

        return await self._make_request(
            "POST", f"/api/v4/futures/{settle}/countdown_cancel_all", data=data, signed=True
        )

    async def futures_fee(
        self,
        settle: str,
        contract: str | None = None,
    ) -> dict:
        """Получение ставок комиссий на фьючерсном рынке.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-market-trading-fee-rates
        """
        params = {
            "contract": contract,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/fee", params=params, signed=True
        )

    async def futures_cancel_orders_batch(
        self,
        settle: str,
        order_ids: list[str],
    ) -> dict:
        """Отмена списка фьючерсных ордеров по идентификаторам.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-batch-orders-by-specified-id-list
        """
        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/batch_cancel_orders",
            data=order_ids,  # type: ignore
            signed=True,
        )

    async def futures_amend_orders_batch(
        self,
        settle: str,
        orders: list[dict[str, Any]],
    ) -> dict:
        """Изменение параметров нескольких фьючерсных ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#batch-modify-orders-by-specified-ids
        """
        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/batch_amend_orders",
            data=orders,  # type: ignore
            signed=True,
        )

    async def futures_risk_limit_table(
        self,
        settle: str,
        table_id: str,
    ) -> dict:
        """Получение таблицы лимитов риска по идентификатору.

        https://www.gate.com/docs/developers/apiv4/en/#query-risk-limit-table-by-table-id
        """
        params = {
            "table_id": table_id,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/risk_limit_table", params=params
        )

    async def futures_create_price_order(
        self,
        settle: str,
        order: dict[str, Any],
    ) -> dict:
        """Создание фьючерсного ордера с ценовым триггером.

        https://www.gate.com/docs/developers/apiv4/en/#create-price-triggered-order
        """
        return await self._make_request(
            "POST", f"/api/v4/futures/{settle}/price_orders", data=order, signed=True
        )

    async def futures_price_orders(
        self,
        settle: str,
        status: str,
        contract: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict:
        """Получение списка отложенных ордеров по фьючерсам.

        https://www.gate.com/docs/developers/apiv4/en/#query-auto-order-list
        """
        params = {
            "status": status,
            "contract": contract,
            "limit": limit,
            "offset": offset,
        }

        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/price_orders", params=params, signed=True
        )

    async def futures_cancel_price_orders(
        self,
        settle: str,
        contract: str | None = None,
    ) -> dict:
        """Отмена всех отложенных фьючерсных ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-all-auto-orders
        """
        params = {
            "contract": contract,
        }

        return await self._make_request(
            "DELETE", f"/api/v4/futures/{settle}/price_orders", params=params, signed=True
        )

    async def futures_price_order(
        self,
        settle: str,
        order_id: str,
    ) -> dict:
        """Получение информации о ценовом триггерном ордере.

        https://www.gate.com/docs/developers/apiv4/en/#query-single-auto-order-details
        """
        return await self._make_request(
            "GET", f"/api/v4/futures/{settle}/price_orders/{order_id}", signed=True
        )

    async def futures_cancel_price_order(
        self,
        settle: str,
        order_id: str,
    ) -> dict:
        """Отмена ценового триггерного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#cancel-single-auto-order
        """
        return await self._make_request(
            "DELETE", f"/api/v4/futures/{settle}/price_orders/{order_id}", signed=True
        )

    # topic: Futures (extra)

    async def futures_contracts_all(
        self,
        settle: str,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """Получение всех контрактов, включая делистнутые.

        https://www.gate.com/docs/developers/apiv4/en/#query-all-contract-information-including-delisted
        """
        params = {"limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/contracts_all",
            params=params,
        )

    async def futures_rpi_order_book(
        self,
        settle: str,
        contract: str,
        interval: str | None = None,
        limit: int | None = None,
        with_id: bool | None = None,
    ) -> Any:
        """Получение книги ордеров с RPI-ордерами.

        https://www.gate.com/docs/developers/apiv4/en/#query-futures-rpi-order-book
        """
        params = {"contract": contract, "interval": interval, "limit": limit, "with_id": with_id}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/rpi_order_book",
            params=params,
        )

    async def futures_adl_risk_states(self, settle: str) -> Any:
        """Получение уровней риска ADL по всем контрактам.

        https://www.gate.com/docs/developers/apiv4/en/#list-market-level-adl-risk-states
        """
        return await self._make_request("GET", f"/api/v4/futures/{settle}/adl_risk_states")

    async def futures_funding_rates_batch(self, settle: str, contracts: list[Any]) -> Any:
        """Пакетное получение истории ставок финансирования.

        https://www.gate.com/docs/developers/apiv4/en/#batch-query-historical-funding-rate-data-for-perpetual-contracts
        """
        data = {
            "contracts": contracts,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/funding_rates",
            data=data,
        )

    async def futures_positions_timerange(
        self,
        settle: str,
        contract: str,
        from_: str | None = None,
        to: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Any:
        """Получение истории позиций за период.

        https://www.gate.com/docs/developers/apiv4/en/#get-user-s-historical-position-information-list-by-time
        """
        params = {"contract": contract, "from": from_, "to": to, "limit": limit, "offset": offset}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/positions_timerange",
            signed=True,
            params=params,
        )

    async def futures_set_position_mode(self, settle: str, position_mode: str) -> Any:
        """Изменение режима позиций (single / dual / dual_plus), замена dual_mode.

        https://www.gate.com/docs/developers/apiv4/en/#set-position-holding-mode-replacing-the-dual-mode-interface
        """
        params = {"position_mode": position_mode}

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/set_position_mode",
            signed=True,
            params=params,
        )

    async def futures_get_leverage(
        self,
        settle: str,
        contract: str,
        pos_margin_mode: str,
        dual_side: str,
    ) -> Any:
        """Получение плеча для указанного режима.

        https://www.gate.com/docs/developers/apiv4/en/#get-leverage-information-for-specified-mode
        """
        params = {"pos_margin_mode": pos_margin_mode, "dual_side": dual_side}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/get_leverage/{contract}",
            signed=True,
            params=params,
        )

    async def futures_set_contract_leverage(
        self,
        settle: str,
        contract: str,
        leverage: str,
        margin_mode: str,
        dual_side: str | None = None,
    ) -> Any:
        """Изменение плеча для указанного режима маржи.

        https://www.gate.com/docs/developers/apiv4/en/#update-leverage-for-specified-mode
        """
        params = {"leverage": leverage, "margin_mode": margin_mode, "dual_side": dual_side}

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/positions/{contract}/set_leverage",
            signed=True,
            params=params,
        )

    async def futures_price_order_amend(
        self,
        settle: str,
        order_id: str,
        size: int | None = None,
        amount: str | None = None,
        price: str | None = None,
        trigger_price: str | None = None,
        price_type: int | None = None,
        auto_size: str | None = None,
        close: bool | None = None,
    ) -> Any:
        """Изменение триггерного ордера.

        https://www.gate.com/docs/developers/apiv4/en/#modify-a-single-auto-order
        """
        data = {
            "settle": settle,
            "order_id": int(order_id),
            "size": size,
            "amount": amount,
            "price": price,
            "trigger_price": trigger_price,
            "price_type": price_type,
            "auto_size": auto_size,
            "close": close,
        }

        return await self._make_request(
            "PUT",
            f"/api/v4/futures/{settle}/price_orders/amend/{order_id}",
            signed=True,
            data=data,
        )

    async def futures_bbo_order_create(
        self,
        settle: str,
        contract: str,
        size: int,
        direction: str,
        level: int,
        iceberg: int | None = None,
        close: bool | None = None,
        is_close: bool | None = None,
        reduce_only: bool | None = None,
        is_reduce_only: bool | None = None,
        is_liq: bool | None = None,
        tif: str | None = None,
        left: int | None = None,
        fill_price: str | None = None,
        text: str | None = None,
        tkfr: str | None = None,
        mkfr: str | None = None,
        refu: int | None = None,
        auto_size: str | None = None,
        stp_id: int | None = None,
        stp_act: str | None = None,
        amend_text: str | None = None,
        pid: int | None = None,
    ) -> Any:
        """Создание BBO-ордера (по уровню лучшей цены).

        https://www.gate.com/docs/developers/apiv4/en/#level-based-bbo-contract-order-placement
        """
        data = {
            "contract": contract,
            "size": size,
            "direction": direction,
            "iceberg": iceberg,
            "level": level,
            "close": close,
            "is_close": is_close,
            "reduce_only": reduce_only,
            "is_reduce_only": is_reduce_only,
            "is_liq": is_liq,
            "tif": tif,
            "left": left,
            "fill_price": fill_price,
            "text": text,
            "tkfr": tkfr,
            "mkfr": mkfr,
            "refu": refu,
            "auto_size": auto_size,
            "stp_id": stp_id,
            "stp_act": stp_act,
            "amend_text": amend_text,
            "pid": pid,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/bbo_orders",
            signed=True,
            data=data,
        )

    async def futures_trail_order_create(
        self,
        settle: str,
        contract: str,
        amount: str,
        price_type: int,
        activation_price: str | None = None,
        is_gte: bool | None = None,
        price_offset: str | None = None,
        reduce_only: bool | None = None,
        position_related: bool | None = None,
        text: str | None = None,
        pos_margin_mode: str | None = None,
        position_mode: str | None = None,
    ) -> Any:
        """Создание трейлинг-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#create-trail-order
        """
        data = {
            "contract": contract,
            "amount": amount,
            "activation_price": activation_price,
            "is_gte": is_gte,
            "price_type": price_type,
            "price_offset": price_offset,
            "reduce_only": reduce_only,
            "position_related": position_related,
            "text": text,
            "pos_margin_mode": pos_margin_mode,
            "position_mode": position_mode,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/create",
            signed=True,
            data=data,
        )

    async def futures_trail_order_update(
        self,
        settle: str,
        id_: int,
        amount: str | None = None,
        activation_price: str | None = None,
        is_gte_str: str | None = None,
        price_type: int | None = None,
        price_offset: str | None = None,
    ) -> Any:
        """Изменение трейлинг-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#update-trail-order
        """
        data = {
            "id": id_,
            "amount": amount,
            "activation_price": activation_price,
            "is_gte_str": is_gte_str,
            "price_type": price_type,
            "price_offset": price_offset,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/update",
            signed=True,
            data=data,
        )

    async def futures_trail_order_stop(
        self,
        settle: str,
        id_: int | None = None,
        text: str | None = None,
    ) -> Any:
        """Остановка трейлинг-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#terminate-trail-order
        """
        data = {
            "id": id_,
            "text": text,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/stop",
            signed=True,
            data=data,
        )

    async def futures_trail_orders_stop_all(
        self,
        settle: str,
        contract: str | None = None,
        related_position: int | None = None,
    ) -> Any:
        """Пакетная остановка трейлинг-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#batch-terminate-trail-orders
        """
        data = {
            "contract": contract,
            "related_position": related_position,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/stop_all",
            signed=True,
            data=data,
        )

    async def futures_trail_orders(
        self,
        settle: str,
        contract: str | None = None,
        is_finished: bool | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        sort_by: int | None = None,
        hide_cancel: bool | None = None,
        related_position: int | None = None,
        sort_by_trigger: bool | None = None,
        reduce_only: int | None = None,
        side: int | None = None,
    ) -> Any:
        """Получение списка трейлинг-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#get-trail-order-list
        """
        params = {
            "contract": contract,
            "is_finished": is_finished,
            "start_at": start_at,
            "end_at": end_at,
            "page_num": page_num,
            "page_size": page_size,
            "sort_by": sort_by,
            "hide_cancel": hide_cancel,
            "related_position": related_position,
            "sort_by_trigger": sort_by_trigger,
            "reduce_only": reduce_only,
            "side": side,
        }

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/list",
            signed=True,
            params=params,
        )

    async def futures_trail_order_detail(self, settle: str, id_: int) -> Any:
        """Получение трейлинг-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#get-trail-order-details
        """
        params = {"id": id_}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/detail",
            signed=True,
            params=params,
        )

    async def futures_trail_order_change_log(
        self,
        settle: str,
        id_: int,
        page_num: int | None = None,
        page_size: int | None = None,
    ) -> Any:
        """Получение истории изменений трейлинг-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#get-trail-order-user-modification-records
        """
        params = {"id": id_, "page_num": page_num, "page_size": page_size}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/autoorder/v1/trail/change_log",
            signed=True,
            params=params,
        )

    async def futures_chase_order_create(
        self,
        settle: str,
        contract: str,
        amount: str,
        price_limit: str,
        offset_limit: str | None = None,
        reduce_only: bool | None = None,
        text: str | None = None,
        is_dual_mode: bool | None = None,
        price_type: int | None = None,
        price_gap_type: int | None = None,
        price_gap_value: str | None = None,
        pos_margin_mode: str | None = None,
        position_mode: str | None = None,
    ) -> Any:
        """Создание chase-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#create-a-chase-order
        """
        data = {
            "contract": contract,
            "settle": settle,
            "amount": amount,
            "price_limit": price_limit,
            "offset_limit": offset_limit,
            "reduce_only": reduce_only,
            "text": text,
            "is_dual_mode": is_dual_mode,
            "price_type": price_type,
            "price_gap_type": price_gap_type,
            "price_gap_value": price_gap_value,
            "pos_margin_mode": pos_margin_mode,
            "position_mode": position_mode,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/chase/create",
            signed=True,
            data=data,
        )

    async def futures_chase_order_stop(
        self,
        settle: str,
        id_: str | None = None,
        text: str | None = None,
    ) -> Any:
        """Остановка chase-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#stop-a-chase-order
        """
        data = {
            "id": id_,
            "text": text,
            "settle": settle,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/chase/stop",
            signed=True,
            data=data,
        )

    async def futures_chase_orders_stop_all(
        self,
        settle: str,
        contract: str | None = None,
        pos_margin_mode: str | None = None,
    ) -> Any:
        """Пакетная остановка chase-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#stop-chase-orders-in-batch
        """
        data = {
            "contract": contract,
            "settle": settle,
            "pos_margin_mode": pos_margin_mode,
        }

        return await self._make_request(
            "POST",
            f"/api/v4/futures/{settle}/autoorder/v1/chase/stop_all",
            signed=True,
            data=data,
        )

    async def futures_chase_orders(
        self,
        settle: str,
        sort_by: int,
        contract: str | None = None,
        is_finished: bool | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page_num: int | None = None,
        page_size: int | None = None,
        hide_cancel: bool | None = None,
        reduce_only: int | None = None,
        side: int | None = None,
    ) -> Any:
        """Получение списка chase-ордеров.

        https://www.gate.com/docs/developers/apiv4/en/#list-chase-orders
        """
        params = {
            "contract": contract,
            "is_finished": is_finished,
            "start_at": start_at,
            "end_at": end_at,
            "page_num": page_num,
            "page_size": page_size,
            "sort_by": sort_by,
            "hide_cancel": hide_cancel,
            "reduce_only": reduce_only,
            "side": side,
        }

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/autoorder/v1/chase/list",
            signed=True,
            params=params,
        )

    async def futures_chase_order_detail(self, settle: str, id_: str) -> Any:
        """Получение chase-ордера.

        https://www.gate.com/docs/developers/apiv4/en/#get-chase-order-detail
        """
        params = {"id": id_}

        return await self._make_request(
            "GET",
            f"/api/v4/futures/{settle}/autoorder/v1/chase/detail",
            signed=True,
            params=params,
        )
