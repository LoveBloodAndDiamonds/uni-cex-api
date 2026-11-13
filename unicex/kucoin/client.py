__all__ = ["Client"]


import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Kucoin API (UTA V2, `/api/ua/v2`).

    `/api/ua/v1` KuCoin перевёл в раздел «Abandoned Endpoints».
    """

    _BASE_URL: str = "https://api.kucoin.com"
    """Базовый URL для запросов."""

    def is_authorized(self) -> bool:
        """Проверяет наличие API‑ключа, секрета и пассфразы."""
        return (
            self._api_key is not None
            and self._api_secret is not None
            and self._api_passphrase is not None
        )

    def _sign_headers(self, method: RequestMethod, request_path: str, body: str) -> dict[str, str]:
        """Формирует заголовки авторизации KuCoin (KC-API-KEY-VERSION 3).

        Подпись: base64(HMAC-SHA256(secret, timestamp + METHOD + path?query + body)).
        Пассфраза: base64(HMAC-SHA256(secret, passphrase)).
        """
        if not self.is_authorized():
            raise NotAuthorized(
                "Api key, api secret and api passphrase is required to private endpoints"
            )
        timestamp = str(int(time.time() * 1000))
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[arg-type]
            f"{timestamp}{method}{request_path}{body}",
            "base64",
        )
        passphrase = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[arg-type]
            self._api_passphrase,  # type: ignore[arg-type]
            "base64",
        )
        return {
            "KC-API-KEY": self._api_key,  # type: ignore[dict-item]
            "KC-API-SIGN": signature,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-PASSPHRASE": passphrase,
            "KC-API-KEY-VERSION": "3",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        """Выполняет HTTP-запрос к эндпоинтам Kucoin API.

        Параметры:
            method (`RequestMethod`): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            endpoint (`str`): Путь эндпоинта Kucoin API.
            params (`dict | None`): Query-параметры.
            data (`dict | None`): Тело запроса (для POST).
            signed (`bool`): Нужна ли подпись запроса.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        params = {
            k: ",".join(map(str, v)) if isinstance(v, list | tuple) else v
            for k, v in filter_params(params or {}).items()
        }
        params = {k: str(v).lower() if isinstance(v, bool) else v for k, v in params.items()}
        body = json.dumps(filter_params(data), separators=(",", ":")) if data else ""

        headers = None
        if signed:
            # Подписывается не URL-кодированная строка запроса
            query = "&".join(f"{k}={v}" for k, v in params.items())
            request_path = f"{endpoint}?{query}" if query else endpoint
            headers = self._sign_headers(method, request_path, body)

        return await super()._make_request(
            method=method,
            url=self._BASE_URL + endpoint,
            params=params,
            data=body if method in ("POST", "PUT") else None,
            headers=headers,
        )

    async def request(
        self,
        method: RequestMethod,
        endpoint: str,
        params: dict | None = None,
        data: dict | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (`RequestMethod`): HTTP метод запроса.
            endpoint (`str`): Путь эндпоинта (например, `/api/ua/v2/market/ticker`).
            params (`dict | None`): Query-параметры.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужна ли подпись запроса.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(method, endpoint, params=params, data=data, signed=signed)

    # topic: market data

    async def symbol(
        self,
        trade_type: Literal["SPOT", "FUTURES", "ISOLATED", "CROSS"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение символов и информации о них.

        https://www.kucoin.com/docs-new/v2/rest/ua/instrument
        """
        params = {"tradeType": trade_type, "symbol": symbol}

        return await self._make_request("GET", "/api/ua/v2/market/instrument", params=params)

    async def ticker(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение тикеров и информации о них.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-ticker
        """
        params = {"tradeType": trade_type, "symbol": symbol}

        return await self._make_request("GET", "/api/ua/v2/market/ticker", params=params)

    async def open_interest(
        self,
        symbol: str | list[str] | None = None,
        interval: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение открытого интереса (в контрактах).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-futures-open-interest
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startAt": start_at,
            "endAt": end_at,
            "pageSize": page_size,
        }

        return await self._make_request("GET", "/api/ua/v2/market/open-interest", params=params)

    async def kline(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        symbol: str,
        interval: str,
        start_at: int | None = None,
        end_at: int | None = None,
        kline_type: Literal["TRADE", "MARK_PRICE", "INDEX_PRICE", "PREMIUM_INDEX"] | None = None,
    ) -> dict[str, Any]:
        """Получение списка свечей.

        Формат свечи: `[t (сек), o, h, l, c, v, q]`; для фьючерсов `v` — в контрактах.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-klines
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "interval": interval,
            "startAt": start_at,
            "endAt": end_at,
            "klineType": kline_type,
        }

        return await self._make_request("GET", "/api/ua/v2/market/kline", params=params)

    async def funding_rate_history(
        self,
        symbol: str,
        start_at: int,
        end_at: int,
    ) -> dict[str, Any]:
        """Получение истории ставок финансирования.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-history-funding-rate
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/market/funding-rate-history",
            params=params,
        )

    async def funding_rate(
        self, symbol: str | None = None, product_type: str | None = None
    ) -> dict[str, Any]:
        """Получение текущей ставки финансирования (без `symbol` — по всем контрактам).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-current-funding
        """
        params = {"symbol": symbol, "productType": product_type}

        return await self._make_request(
            "GET",
            "/api/ua/v2/market/funding-rate",
            params=params,
        )

    async def announcements(
        self,
        language: str | None = None,
        type_: str | None = None,
        page_number: int | None = None,
        page_size: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        """Получение объявлений.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-announcements
        """
        params = {
            "language": language,
            "type": type_,
            "pageNumber": page_number,
            "pageSize": page_size,
            "startTime": start_time,
            "endTime": end_time,
        }

        return await self._make_request("GET", "/api/ua/v2/market/announcement", params=params)

    async def currency(self, currency: str, chain: str | None = None) -> dict[str, Any]:
        """Получение информации о валюте.

        https://www.kucoin.com/docs-new/v2/rest/ua/currency
        """
        params = {
            "chain": chain,
            "currency": currency,
        }

        return await self._make_request("GET", "/api/ua/v2/market/currency", params=params)

    async def orderbook(
        self,
        symbol: str,
        trade_type: str | None = None,
        limit: str | None = None,
        rpi_filter: int | None = None,
    ) -> dict[str, Any]:
        """Получение книги ордеров.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-orderbook
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "limit": limit,
            "rpiFilter": rpi_filter,
        }

        return await self._make_request("GET", "/api/ua/v2/market/orderbook", params=params)

    async def trades(self, trade_type: str, symbol: str) -> dict[str, Any]:
        """Получение последних сделок.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-trades
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
        }

        return await self._make_request("GET", "/api/ua/v2/market/trade", params=params)

    async def index_price(
        self,
        symbol: str,
        start_at: str | None = None,
        end_at: str | None = None,
        page_size: str | None = None,
        last_id: int | None = None,
    ) -> dict[str, Any]:
        """Получение индексной цены.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-index-price
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
            "pageSize": page_size,
            "lastId": last_id,
        }

        return await self._make_request("GET", "/api/ua/v2/market/index-price", params=params)

    async def position_tiers(
        self,
        trade_type: str,
        margin_mode: str,
        data: str,
        account_type: str,
        currency: str | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение ступеней риска позиции.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-position-tiers
        """
        params = {
            "tradeType": trade_type,
            "currency": currency,
            "marginMode": margin_mode,
            "data": data,
            "accountType": account_type,
            "symbol": symbol,
        }

        return await self._make_request("GET", "/api/ua/v2/market/position-tiers", params=params)

    async def collateral_ratio(self) -> dict[str, Any]:
        """Получение коэффициентов залога.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-collateral-ratio
        """
        return await self._make_request("GET", "/api/ua/v2/market/collateral-discount-ratio")

    async def borrowable_currencies(self) -> dict[str, Any]:
        """Получение валют, доступных для займа.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-borrowable-currencies
        """
        return await self._make_request("GET", "/api/ua/v2/market/borrowable-currency")

    async def interest_rate_index(
        self,
        symbol: str,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение индекса процентной ставки фьючерсов.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-interest-rate-index
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
            "lastId": last_id,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/market/interest-rate-index",
            params=params,
        )

    async def trade_statistics(self) -> dict[str, Any]:
        """Получение 24-часовой статистики платформы (спот и фьючерсы).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-trade-statistics
        """
        return await self._make_request("GET", "/api/ua/v2/trade-statistics")

    async def call_auction_info(self, symbol: str) -> dict[str, Any]:
        """Получение данных call auction.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-call-auction-info
        """
        params = {
            "symbol": symbol,
        }

        return await self._make_request("GET", "/api/ua/v2/market/call-auction-info", params=params)

    async def fiat_price(self, base: str, currencies: list[Any] | None = None) -> dict[str, Any]:
        """Получение цены в фиатных валютах.

        https://www.kucoin.com/docs-new/v2/rest/ua/fiat-price
        """
        params = {
            "base": base,
            "currencies": currencies,
        }

        return await self._make_request("GET", "/api/ua/v2/market/fiat-price", params=params)

    async def oes_currencies(
        self,
        custodian: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Получение валют стороннего кастодиана.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-oes-settlement-currency
        """
        params = {
            "custodian": custodian,
            "currency": currency,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/oes/currency",
            params=params,
        )

    async def server_status(self, trade_type: str) -> dict[str, Any]:
        """Получение статуса сервиса.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-service-status
        """
        params = {
            "tradeType": trade_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/server/status",
            params=params,
        )

    async def kyc_regions(self) -> dict[str, Any]:
        """Получение регионов KYC.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-kyc-region
        """
        return await self._make_request("GET", "/api/ua/v2/user/kyc-region")

    async def my_ip(self) -> dict[str, Any]:
        """Получение IP-адреса клиента.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-client-ip-address
        """
        return await self._make_request("GET", "/api/ua/v2/user/my-ip")

    async def currencies(
        self,
        chain: str | None = None,
        currency_list: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Получение списка валют.

        https://www.kucoin.com/docs-new/v2/rest/ua/currencies
        """
        params = {
            "chain": chain,
            "currencyList": currency_list,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/currencies",
            params=params,
        )

    async def account_overview(self) -> dict[str, Any]:
        """Получение обзора аккаунта (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/account/get-account-overview-uta
        """
        return await self._make_request("GET", "/api/ua/v2/unified/account/overview", signed=True)

    async def account_balance(self) -> dict[str, Any]:
        """Получение активов аккаунта по валютам (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-account-currency-assets-uta
        """
        return await self._make_request("GET", "/api/ua/v2/unified/account/balance", signed=True)

    async def account_balance_classic(
        self,
        account_type: str,
        account_subtype: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Получение активов аккаунта по валютам (Classic).

        https://www.kucoin.com/docs-new/v2/rest/ua/classic-account-balance
        """
        params = {
            "accountSubtype": account_subtype,
            "accountType": account_type,
            "currency": currency,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/balance",
            params=params,
            signed=True,
        )

    async def api_key_info(self) -> dict[str, Any]:
        """Получение информации об API-ключе.

        https://www.kucoin.com/docs-new/v2/rest/ua/api-key
        """
        return await self._make_request("GET", "/api/ua/v2/user/api-key", signed=True)

    async def account_mode(self) -> dict[str, Any]:
        """Получение режима аккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-account-mode
        """
        return await self._make_request("GET", "/api/ua/v2/account/mode", signed=True)

    async def account_mode_set(self, account_type: str) -> dict[str, Any]:
        """Изменение режима аккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/set-account-mode
        """
        data = {
            "accountType": account_type,
        }

        return await self._make_request("POST", "/api/ua/v2/account/mode", data=data, signed=True)

    async def leverage(
        self,
        trade_type: str,
        currency: str | None = None,
        symbol: str | None = None,
        margin_mode: str | None = None,
    ) -> dict[str, Any]:
        """Получение плеча (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-leverage
        """
        params = {
            "currency": currency,
            "symbol": symbol,
            "tradeType": trade_type,
            "marginMode": margin_mode,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/account/leverage",
            params=params,
            signed=True,
        )

    async def leverage_modify(self, symbol: str, leverage: str) -> dict[str, Any]:
        """Изменение плеча фьючерсов (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/modify-leverage-uta
        """
        data = {
            "symbol": symbol,
            "leverage": leverage,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/account/modify-leverage",
            data=data,
            signed=True,
        )

    async def cross_margin_leverage_modify(
        self,
        leverage: str,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Изменение плеча кросс-маржи (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/modify-cross-margin-leverage-uta
        """
        data = {
            "leverage": leverage,
            "currency": currency,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/account/modify-leverage-margin-cross",
            data=data,
            signed=True,
        )

    async def borrowing_rates_and_limits(self, currency: str) -> dict[str, Any]:
        """Получение ставок и лимитов заимствования.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-borrowing-rates-and-limits
        """
        params = {
            "currency": currency,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/interest-limits",
            params=params,
            signed=True,
        )

    async def account_ledger(
        self,
        account_type: str,
        business_type: str | None = None,
        currency: str | None = None,
        direction: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        page_size: int | None = None,
        last_id: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории операций по аккаунту.

        https://www.kucoin.com/docs-new/v2/rest/ua/account-ledger
        """
        params = {
            "accountType": account_type,
            "businessType": business_type,
            "currency": currency,
            "direction": direction,
            "startAt": start_at,
            "endAt": end_at,
            "pageSize": page_size,
            "lastId": last_id,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/ledger",
            params=params,
            signed=True,
        )

    async def interest_history(
        self,
        account_type: str,
        currency: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории начисления процентов (UTA).

        https://www.kucoin.com/docs-new/v2/rest/ua/get-interest-history-uta
        """
        params = {
            "accountType": account_type,
            "currency": currency,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "size": size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/interest-history",
            params=params,
            signed=True,
        )

    async def api_rate_limit(self, uids: str) -> dict[str, Any]:
        """Получение лимита запросов API.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-api-rate-limit
        """
        params = {
            "uids": uids,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/rate-limit/query",
            params=params,
            signed=True,
        )

    async def api_rate_limits_all(self) -> dict[str, Any]:
        """Получение всех лимитов запросов API.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-all-api-rate-limit
        """
        return await self._make_request("GET", "/api/ua/v2/rate-limit/query-all", signed=True)

    async def api_rate_limit_cap(self) -> dict[str, Any]:
        """Получение максимального лимита запросов API.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-api-rate-limit-cap
        """
        return await self._make_request("GET", "/api/ua/v2/rate-limit/query-cap", signed=True)

    async def fee_rate(self, trade_type: str, symbol: str) -> dict[str, Any]:
        """Получение ставок комиссии.

        https://www.kucoin.com/docs-new/v2/rest/ua/actual-fee
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/user/fee-rate",
            params=params,
            signed=True,
        )

    async def kcs_fee_deduction(self, enabled: bool) -> dict[str, Any]:
        """Управление оплатой комиссии в KCS.

        https://www.kucoin.com/docs-new/v2/rest/ua/kcs-deduct
        """
        params = {
            "enabled": enabled,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/fee/kcs-deduct",
            params=params,
            signed=True,
        )

    async def oes_custody_quota(
        self,
        custodian: str | None = None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Получение лимитов по валютам стороннего кастодиана.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-oes-custody-quota
        """
        params = {
            "custodian": custodian,
            "currency": currency,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/oes/custody-quota",
            params=params,
            signed=True,
        )

    async def collateral_assets(
        self,
        ccy: str | None = None,
        collateral_enabled: bool | None = None,
    ) -> dict[str, Any]:
        """Получение залоговых активов.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-collateral-assets
        """
        params = {
            "ccy": ccy,
            "collateralEnabled": collateral_enabled,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/collateral-assets",
            params=params,
            signed=True,
        )

    async def collateral_assets_set(
        self,
        type_: str,
        collateral_enabled: bool,
        ccy_list: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Изменение залоговых активов.

        https://www.kucoin.com/docs-new/v2/rest/ua/set-collateral-assets
        """
        data = {
            "type": type_,
            "ccyList": ccy_list,
            "collateralEnabled": collateral_enabled,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/account/set-collateral-assets",
            data=data,
            signed=True,
        )

    async def max_order_quantity(
        self,
        symbol: str,
        trade_type: str,
        price: NumberLike | None = None,
    ) -> dict[str, Any]:
        """Получение максимального размера ордера.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-max-order-quantity
        """
        params = {
            "symbol": symbol,
            "tradeType": trade_type,
            "price": price,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/order/max-order-quantity",
            params=params,
            signed=True,
        )

    async def sub_account_balance(
        self,
        uid: str | None = None,
        page_size: int | None = None,
        last_id: int | None = None,
    ) -> dict[str, Any]:
        """Получение активов субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/sub-account-balance
        """
        params = {
            "uid": uid,
            "pageSize": page_size,
            "lastId": last_id,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/sub-account/balance",
            params=params,
            signed=True,
        )

    async def sub_account_list(
        self,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка субаккаунтов.

        https://www.kucoin.com/docs-new/v2/rest/ua/sub-accounts
        """
        params = {
            "currentPage": current_page,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/user/sub-account-list",
            params=params,
            signed=True,
        )

    async def sub_api_keys(self, api_key: str, sub_name: str) -> dict[str, Any]:
        """Получение API-ключей субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/sub-api-keys
        """
        params = {
            "apiKey": api_key,
            "subName": sub_name,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/user/sub-api-key",
            params=params,
            signed=True,
        )

    async def sub_account_transfer_permission(
        self,
        sub_uids: str,
        sub_to_sub: bool,
    ) -> dict[str, Any]:
        """Изменение разрешения на переводы субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/transfer-permission
        """
        data = {
            "subUids": sub_uids,
            "subToSub": sub_to_sub,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/sub-account/canTransferOut",
            data=data,
            signed=True,
        )

    async def sub_account_create(
        self,
        password: str,
        sub_name: str,
        access: str,
        remarks: str | None = None,
        mode: str | None = None,
    ) -> dict[str, Any]:
        """Создание субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/add-sub-account
        """
        data = {
            "password": password,
            "remarks": remarks,
            "subName": sub_name,
            "access": access,
            "mode": mode,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/user/sub/create-sub-account",
            data=data,
            signed=True,
        )

    async def sub_api_key_create(
        self,
        sub_name: str,
        passphrase: str,
        remark: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """Создание API-ключа субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/add-sub-api-key
        """
        data = {
            "subName": sub_name,
            "passphrase": passphrase,
            "remark": remark,
            "permission": permission,
            "ipWhitelist": ip_whitelist,
            "expire": expire,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/user/create-sub-api-key",
            data=data,
            signed=True,
        )

    async def sub_api_key_modify(
        self,
        sub_name: str,
        api_key: str,
        passphrase: str,
        permission: str | None = None,
        ip_whitelist: str | None = None,
        expire: str | None = None,
    ) -> dict[str, Any]:
        """Изменение API-ключа субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/modify-sub-api-key
        """
        data = {
            "subName": sub_name,
            "apiKey": api_key,
            "passphrase": passphrase,
            "permission": permission,
            "ipWhitelist": ip_whitelist,
            "expire": expire,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/user/modify-sub-api-key",
            data=data,
            signed=True,
        )

    async def sub_accounts_rate_limit_set(self, list: list[Any]) -> dict[str, Any]:
        """Изменение лимита запросов API субаккаунтов.

        https://www.kucoin.com/docs-new/v2/rest/ua/set-sub-accounts-api-rate-limit
        """
        data = {
            "list": list,
        }

        return await self._make_request("POST", "/api/ua/v2/rate-limit/set", data=data, signed=True)

    async def sub_api_key_delete(
        self,
        api_key: str,
        sub_name: str,
        passphrase: str,
    ) -> dict[str, Any]:
        """Удаление API-ключа субаккаунта.

        https://www.kucoin.com/docs-new/v2/rest/ua/delete-sub-api-key
        """
        params = {
            "apiKey": api_key,
            "subName": sub_name,
            "passphrase": passphrase,
        }

        return await self._make_request(
            "DELETE",
            "/api/ua/v2/user/sub-api-key",
            params=params,
            signed=True,
        )

    async def deposit_address(self, currency: str, chain: str | None = None) -> dict[str, Any]:
        """Получение адреса депозита.

        https://www.kucoin.com/docs-new/v2/rest/ua/deposit-address
        """
        params = {
            "chain": chain,
            "currency": currency,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/deposit/address",
            params=params,
            signed=True,
        )

    async def deposit_history(
        self,
        currency: str | None = None,
        id_: str | None = None,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории депозитов.

        https://www.kucoin.com/docs-new/v2/rest/ua/deposit-history
        """
        params = {
            "currency": currency,
            "id": id_,
            "status": status,
            "startAt": start_at,
            "endAt": end_at,
            "currentPage": current_page,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/deposit/history",
            params=params,
            signed=True,
        )

    async def transfer_quotas(
        self,
        account_type: str,
        currency: str,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение доступных для перевода сумм.

        https://www.kucoin.com/docs-new/v2/rest/ua/transfer-quota
        """
        params = {
            "accountType": account_type,
            "currency": currency,
            "symbol": symbol,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/account/transfer-quota",
            params=params,
            signed=True,
        )

    async def flex_transfer(
        self,
        client_oid: str,
        transfer_type: str,
        currency: str,
        amount: str,
        from_account_type: str,
        from_account_tag: str,
        to_account_type: str,
        to_account_tag: str,
        from_uid: str | None = None,
        to_uid: str | None = None,
    ) -> dict[str, Any]:
        """Перевод средств между аккаунтами.

        https://www.kucoin.com/docs-new/v2/rest/ua/flex-transfer
        """
        data = {
            "clientOid": client_oid,
            "transferType": transfer_type,
            "currency": currency,
            "amount": amount,
            "fromUid": from_uid,
            "fromAccountType": from_account_type,
            "fromAccountTag": from_account_tag,
            "toUid": to_uid,
            "toAccountType": to_account_type,
            "toAccountTag": to_account_tag,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/account/transfer",
            data=data,
            signed=True,
        )

    async def withdrawal_quotas(
        self,
        currency: str,
        withdraw_type: str,
        chain: str | None = None,
        is_inner: bool | None = None,
    ) -> dict[str, Any]:
        """Получение лимитов вывода.

        https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-quota
        """
        params = {
            "chain": chain,
            "currency": currency,
            "isInner": is_inner,
            "withdrawType": withdraw_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/withdrawals/quotas",
            params=params,
            signed=True,
        )

    async def withdrawal_history(
        self,
        currency: str | None = None,
        id_: str | None = None,
        status: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории выводов.

        https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history
        """
        params = {
            "currency": currency,
            "id": id_,
            "status": status,
            "startAt": start_at,
            "endAt": end_at,
            "currentPage": current_page,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/withdrawal/history",
            params=params,
            signed=True,
        )

    async def withdraw(
        self,
        currency: str,
        amount: str,
        to_address: str,
        withdraw_type: str,
        chain: str | None = None,
        memo: str | None = None,
        remark: str | None = None,
        is_inner: bool | None = None,
        fee_deduct_type: str | None = None,
    ) -> dict[str, Any]:
        """Вывод средств.

        https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal
        """
        data = {
            "currency": currency,
            "chain": chain,
            "amount": amount,
            "toAddress": to_address,
            "memo": memo,
            "remark": remark,
            "isInner": is_inner,
            "withdrawType": withdraw_type,
            "feeDeductType": fee_deduct_type,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/asset/withdrawal",
            data=data,
            signed=True,
        )

    async def withdrawal_cancel(self, withdraw_id: str) -> dict[str, Any]:
        """Отмена вывода средств.

        https://www.kucoin.com/docs-new/v2/rest/ua/cancel-withdrawal
        """
        data = {
            "withdrawId": withdraw_id,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/asset/withdraw/cancel",
            data=data,
            signed=True,
        )

    async def small_balance_currencies(self, account_type: str) -> dict[str, Any]:
        """Получение валют с малым остатком.

        https://www.kucoin.com/docs-new/v2/rest/ua/small-balance-currencies
        """
        params = {
            "accountType": account_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/small-balance/currencies",
            params=params,
            signed=True,
        )

    async def small_balance_convert(
        self,
        account_type: str,
        currency_list: list[Any],
        client_order_id: str,
        target_currency: str | None = None,
    ) -> dict[str, Any]:
        """Конвертация малых остатков.

        https://www.kucoin.com/docs-new/v2/rest/ua/small-balance-convert
        """
        data = {
            "accountType": account_type,
            "currencyList": currency_list,
            "targetCurrency": target_currency,
            "clientOrderId": client_order_id,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/asset/small-balance/order",
            data=data,
            signed=True,
        )

    async def small_balance_convert_detail(
        self,
        order_id: str | None = None,
        client_order_id: str | None = None,
    ) -> dict[str, Any]:
        """Получение деталей конвертации малых остатков.

        https://www.kucoin.com/docs-new/v2/rest/ua/small-balance-order-detail
        """
        params = {
            "orderId": order_id,
            "clientOrderId": client_order_id,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/small-balance/order/detail",
            params=params,
            signed=True,
        )

    async def small_balance_convert_history(
        self,
        account_type: str,
        start_at: int | None = None,
        end_at: int | None = None,
        current_page: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории конвертаций малых остатков.

        https://www.kucoin.com/docs-new/v2/rest/ua/small-balance-order-history
        """
        params = {
            "accountType": account_type,
            "startAt": start_at,
            "endAt": end_at,
            "currentPage": current_page,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/asset/small-balance/order/history",
            params=params,
            signed=True,
        )

    async def order_place(
        self,
        trade_type: str,
        symbol: str,
        side: str,
        order_type: str,
        size: str,
        size_unit: str,
        client_oid: str | None = None,
        position_side: str | None = None,
        price: str | None = None,
        reduce_only: bool | None = None,
        margin_mode: str | None = None,
        stp: str | None = None,
        time_in_force: str | None = None,
        cancel_after: int | None = None,
        post_only: bool | None = None,
        tags: str | None = None,
        trigger_direction: str | None = None,
        trigger_price: str | None = None,
        trigger_price_type: str | None = None,
        tp_trigger_price: str | None = None,
        tp_trigger_price_type: str | None = None,
        sl_trigger_price: str | None = None,
        sl_trigger_price_type: str | None = None,
        close_order: bool | None = None,
    ) -> dict[str, Any]:
        """Создание ордера.

        https://www.kucoin.com/docs-new/v2/rest/ua/place-order
        """
        data = {
            "tradeType": trade_type,
            "clientOid": client_oid,
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "orderType": order_type,
            "size": size,
            "sizeUnit": size_unit,
            "price": price,
            "reduceOnly": reduce_only,
            "marginMode": margin_mode,
            "stp": stp,
            "timeInForce": time_in_force,
            "cancelAfter": cancel_after,
            "postOnly": post_only,
            "tags": tags,
            "triggerDirection": trigger_direction,
            "triggerPrice": trigger_price,
            "triggerPriceType": trigger_price_type,
            "tpTriggerPrice": tp_trigger_price,
            "tpTriggerPriceType": tp_trigger_price_type,
            "slTriggerPrice": sl_trigger_price,
            "slTriggerPriceType": sl_trigger_price_type,
            "closeOrder": close_order,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/order/place",
            data=data,
            signed=True,
        )

    async def order_amend(
        self,
        symbol: str,
        new_size: NumberLike | None = None,
        order_id: str | None = None,
        client_oid: str | None = None,
        new_price: NumberLike | None = None,
        size_unit: str | None = None,
        cxl_on_fail: bool | None = None,
        sl_trigger_price: NumberLike | None = None,
        tp_trigger_price: NumberLike | None = None,
        sl_trigger_price_type: str | None = None,
        tp_trigger_price_type: str | None = None,
    ) -> dict[str, Any]:
        """Изменение ордера (пока только фьючерсы).

        https://www.kucoin.com/docs-new/v2/rest/ua/amend-order
        """
        data = {
            "symbol": symbol,
            "newSize": new_size,
            "orderId": order_id,
            "clientOid": client_oid,
            "newPrice": new_price,
            "sizeUnit": size_unit,
            "cxlOnFail": cxl_on_fail,
            "slTriggerPrice": sl_trigger_price,
            "tpTriggerPrice": tp_trigger_price,
            "slTriggerPriceType": sl_trigger_price_type,
            "tpTriggerPriceType": tp_trigger_price_type,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/order/amend",
            data=data,
            signed=True,
        )

    async def order_cancel(
        self,
        symbol: str,
        trade_type: str,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Отмена ордера.

        https://www.kucoin.com/docs-new/v2/rest/ua/cancel-order
        """
        data = {
            "symbol": symbol,
            "tradeType": trade_type,
            "orderId": order_id,
            "clientOid": client_oid,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/order/cancel",
            data=data,
            signed=True,
        )

    async def orders_cancel_by_id(
        self,
        trade_type: str,
        cancel_order_list: list[Any],
    ) -> dict[str, Any]:
        """Пакетная отмена ордеров по ID.

        https://www.kucoin.com/docs-new/v2/rest/ua/batch-cancel-order-by-id
        """
        data = {
            "tradeType": trade_type,
            "cancelOrderList": cancel_order_list,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/order/cancel-batch",
            data=data,
            signed=True,
        )

    async def orders_cancel_by_symbol(
        self,
        trade_type: str,
        symbol: str,
        order_filter: str,
        margin_mode: str | None = None,
    ) -> dict[str, Any]:
        """Отмена всех ордеров по символу.

        https://www.kucoin.com/docs-new/v2/rest/ua/batch-cancel-order-by-symbol
        """
        data = {
            "tradeType": trade_type,
            "symbol": symbol,
            "marginMode": margin_mode,
            "orderFilter": order_filter,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/order/cancel-all",
            data=data,
            signed=True,
        )

    async def order_detail(
        self,
        trade_type: str,
        symbol: str,
        order_id: str | None = None,
        client_oid: str | None = None,
    ) -> dict[str, Any]:
        """Получение информации об ордере.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-order-details
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "orderId": order_id,
            "clientOid": client_oid,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/order/detail",
            params=params,
            signed=True,
        )

    async def orders_open(
        self,
        trade_type: str,
        symbol: str | None = None,
        order_filter: str | None = None,
        page_number: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Получение активных ордеров.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-open-order-list
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "orderFilter": order_filter,
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/order/open-list",
            params=params,
            signed=True,
        )

    async def orders_history(
        self,
        trade_type: str,
        symbol: str | None = None,
        side: str | None = None,
        order_filter: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории ордеров.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-order-history
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "side": side,
            "orderFilter": order_filter,
            "startAt": start_at,
            "endAt": end_at,
            "lastId": last_id,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/order/history",
            params=params,
            signed=True,
        )

    async def trade_history(
        self,
        trade_type: str,
        symbol: str | None = None,
        order_id: str | None = None,
        client_oid: str | None = None,
        side: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
        fill_type: str | None = None,
    ) -> dict[str, Any]:
        """Получение истории сделок.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-trade-history
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "orderId": order_id,
            "clientOid": client_oid,
            "side": side,
            "startAt": start_at,
            "endAt": end_at,
            "lastId": last_id,
            "pageSize": page_size,
            "fillType": fill_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/order/execution",
            params=params,
            signed=True,
        )

    async def positions(
        self,
        symbol: str | None = None,
        page_number: str | None = None,
        page_size: str | None = None,
    ) -> dict[str, Any]:
        """Получение открытых позиций.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-position-list-uta
        """
        params = {
            "symbol": symbol,
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/position/open-list",
            params=params,
            signed=True,
        )

    async def positions_history(
        self,
        symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории позиций.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-position-history-uta
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
            "lastId": last_id,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/position/history",
            params=params,
            signed=True,
        )

    async def funding_fee_history(
        self,
        symbol: str | None = None,
        start_at: int | None = None,
        end_at: int | None = None,
        last_id: int | None = None,
        page_size: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории списаний фандинга.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-private-funding-fee-history
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
            "lastId": last_id,
            "pageSize": page_size,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/position/funding-history",
            params=params,
            signed=True,
        )

    async def margin_mode(self, symbol: str | None = None) -> dict[str, Any]:
        """Получение режима маржи.

        https://www.kucoin.com/docs-new/v2/rest/ua/get-margin-mode
        """
        params = {
            "symbol": symbol,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/unified/position/margin-mode",
            params=params,
            signed=True,
        )

    async def margin_mode_set(self, symbol: str, margin_mode: str) -> dict[str, Any]:
        """Изменение режима маржи.

        https://www.kucoin.com/docs-new/v2/rest/ua/batch-modify-margin-mode
        """
        data = {
            "symbol": symbol,
            "marginMode": margin_mode,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/position/margin-mode",
            data=data,
            signed=True,
        )

    async def position_margin_modify(
        self,
        type_: str,
        amount: NumberLike,
        symbol: str,
        trade_type: str,
    ) -> dict[str, Any]:
        """Изменение маржи позиции.

        https://www.kucoin.com/docs-new/v2/rest/ua/modify-isolated-futures-margin
        """
        data = {
            "type": type_,
            "amount": amount,
            "symbol": symbol,
            "tradeType": trade_type,
        }

        return await self._make_request(
            "POST",
            "/api/ua/v2/unified/position/modify-margin",
            data=data,
            signed=True,
        )

    async def otc_loan_accounts(self, account_type: str | None = None) -> dict[str, Any]:
        """Получение аккаунтов OTC-займа.

        https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-accounts
        """
        params = {
            "accountType": account_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/otc-loan/account",
            params=params,
            signed=True,
        )

    async def otc_loan_collateral_ratio(self, account_type: str | None = None) -> dict[str, Any]:
        """Получение коэффициентов залога OTC-займа.

        https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-collateral-ratio
        """
        params = {
            "accountType": account_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/otc-loan/discount-rate",
            params=params,
            signed=True,
        )

    async def otc_loan_info(self, account_type: str | None = None) -> dict[str, Any]:
        """Получение информации об OTC-займе.

        https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-loan-info
        """
        params = {
            "accountType": account_type,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v2/otc-loan/loan",
            params=params,
            signed=True,
        )
