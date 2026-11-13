__all__ = ["Client"]

import datetime
import json
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import NumberLike, RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с OKX API."""

    _BASE_URL: str = "https://www.okx.com"
    """Базовый URL для REST API OKX."""

    def is_authorized(self) -> bool:
        """Проверяет наличие API‑ключей у клиента.

        Возвращает:
            `bool`: Признак наличия ключей.
        """
        return (
            self._api_key is not None
            and self._api_secret is not None
            and self._api_passphrase is not None
        )

    def _get_timestamp(self) -> str:
        """Генерирует timestamp в формате OKX (ISO с миллисекундами и Z).

        Возвращает:
            `str`: Временная метка в формате ISO с миллисекундами и суффиксом Z.
        """
        now = datetime.datetime.now(tz=datetime.UTC).replace(tzinfo=None)
        timestamp = now.isoformat("T", "milliseconds")
        return timestamp + "Z"

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
            endpoint (`str`): Относительный путь эндпоинта (например `/api/v5/public/time`).
            params (`dict[str, Any] | None`): Query-параметры.
            body (`dict[str, Any] | None`): Тело запроса (для POST/PUT).

        Возвращает:
            tuple:
                - `timestamp (str)`: Временная метка в формате OKX.
                - `signature (str)`: Подпись в формате base64.
        """
        if not self.is_authorized():
            raise NotAuthorized(
                "Api key and api secret and api passphrase is required to private endpoints"
            )

        timestamp = self._get_timestamp()

        # Формируем query string для GET запросов
        query_string = ""
        if params and method == "GET":
            query_params = "&".join(f"{k}={v}" for k, v in params.items())
            query_string = f"?{query_params}"

        # Формируем body для POST запросов
        body_str = json.dumps(body) if body else ""

        # Создаем строку для подписи: timestamp + method + requestPath + body
        prehash = f"{timestamp}{method}{endpoint}{query_string}{body_str}"
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[arg-type]
            prehash,
            "base64",
        )
        return timestamp, signature

    def _get_headers(self, timestamp: str, signature: str) -> dict[str, str]:
        """Возвращает заголовки для REST-запросов OKX.

        Параметры:
            timestamp (`str`): Временная метка.
            signature (`str`): Подпись (base64).

        Возвращает:
            `dict[str, str]`: Словарь заголовков запроса.
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers.update(
            {
                "OK-ACCESS-KEY": self._api_key,  # type: ignore[attr-defined]
                "OK-ACCESS-SIGN": signature,
                "OK-ACCESS-TIMESTAMP": timestamp,
                "OK-ACCESS-PASSPHRASE": self._api_passphrase,  # type: ignore[attr-defined]
                "x-simulated-trading": "0",
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

        # Предобрабатывает параметры запроса
        if params:
            params = filter_params(params)
        if isinstance(body, dict):
            body = filter_params(body)

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
        """Выполняет HTTP-запрос к эндпоинтам OKX API.

        Если `signed=True`:
            - генерирует `timestamp` и `signature`;
            - добавляет авторизационные заголовки (`OK-ACCESS-KEY`, `OK-ACCESS-PASSPHRASE`, `OK-ACCESS-TIMESTAMP`, `OK-ACCESS-SIGN`).

        Если `signed=False`:
            - выполняет публичный запрос без подписи.

        Параметры:
            method (`RequestMethod`): HTTP-метод (`"GET"`, `"POST"`, и т. п.).
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/v5/public/time"`).
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
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/v5/public/time"`).
            signed (`bool`): Приватный запрос (с подписью) или публичный.
            params (`dict[str, Any] | None`): Query-параметры запроса.
            data (`dict[str, Any] | None`): Тело запроса для `POST/PUT`.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(
            method=method, endpoint=endpoint, params=params, data=data, signed=signed
        )

    # topic: Trading Account

    async def get_account_instruments(
        self,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
        inst_id: str | None = None,
        series_id: str | None = None,
    ) -> dict:
        """Получение доступных инструментов аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-instruments
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "instId": inst_id,
            "seriesId": series_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/instruments",
            params=params,
            signed=True,
        )

    async def get_balance(self, ccy: str | None = None) -> dict:
        """Получение баланса аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/balance",
            params=params,
            signed=True,
        )

    async def get_positions(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"] | None = None,
        inst_id: str | None = None,
        pos_id: str | None = None,
    ) -> dict:
        """Получение текущих позиций аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
            "posId": pos_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/positions",
            params=params,
            signed=True,
        )

    async def get_positions_history(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"] | None = None,
        inst_id: str | None = None,
        mgn_mode: Literal["cross", "isolated"] | None = None,
        type_: str | None = None,
        pos_id: str | None = None,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории позиций аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions-history
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
            "mgnMode": mgn_mode,
            "type": type_,
            "posId": pos_id,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/positions-history",
            params=params,
            signed=True,
        )

    async def get_account_position_risk(
        self, inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"] | None = None
    ) -> dict:
        """Получение риска по аккаунту и позициям.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-account-and-position-risk
        """
        params = {
            "instType": inst_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/account-position-risk",
            params=params,
            signed=True,
        )

    async def get_account_bills(
        self,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"] | None = None,
        inst_id: str | None = None,
        ccy: str | None = None,
        mgn_mode: Literal["isolated", "cross"] | None = None,
        ct_type: Literal["linear", "inverse"] | None = None,
        type_: str | None = None,
        sub_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение выписок за последние 7 дней.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bills-details-last-7-days
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
            "ccy": ccy,
            "mgnMode": mgn_mode,
            "ctType": ct_type,
            "type": type_,
            "subType": sub_type,
            "after": after,
            "before": before,
            "begin": begin,
            "end": end,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/bills",
            params=params,
            signed=True,
        )

    async def get_account_bills_archive(
        self,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"] | None = None,
        inst_id: str | None = None,
        ccy: str | None = None,
        mgn_mode: Literal["isolated", "cross"] | None = None,
        ct_type: Literal["linear", "inverse"] | None = None,
        type_: str | None = None,
        sub_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение выписок за последние 3 месяца.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bills-details-last-3-months
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
            "ccy": ccy,
            "mgnMode": mgn_mode,
            "ctType": ct_type,
            "type": type_,
            "subType": sub_type,
            "after": after,
            "before": before,
            "begin": begin,
            "end": end,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/bills-archive",
            params=params,
            signed=True,
        )

    async def apply_bills_history_archive(
        self, year: str, quarter: Literal["Q1", "Q2", "Q3", "Q4"], type_: str | None = None
    ) -> dict:
        """Запрос на формирование архива выписок.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-apply-bills-details-since-2021
        """
        data = {
            "year": year,
            "quarter": quarter,
            "type": type_,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/bills-history-archive",
            data=data,
            signed=True,
        )

    async def get_bills_history_archive(
        self, year: str, quarter: Literal["Q1", "Q2", "Q3", "Q4"], type_: str | None = None
    ) -> dict:
        """Получение ссылки на архив выписок.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bills-details-since-2021
        """
        params = {
            "year": year,
            "quarter": quarter,
            "type": type_,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/bills-history-archive",
            params=params,
            signed=True,
        )

    async def get_account_config(self) -> dict:
        """Получение конфигурации аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-account-configuration
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/config",
            signed=True,
        )

    async def set_position_mode(self, pos_mode: Literal["long_short_mode", "net_mode"]) -> dict:
        """Изменение режима позиций.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-position-mode
        """
        data = {
            "posMode": pos_mode,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-position-mode",
            data=data,
            signed=True,
        )

    async def set_leverage(
        self,
        lever: str,
        mgn_mode: Literal["isolated", "cross"],
        inst_id: str | None = None,
        ccy: str | None = None,
        pos_side: Literal["long", "short"] | None = None,
    ) -> dict:
        """Установка плеча.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-leverage
        """
        data = {
            "instId": inst_id,
            "ccy": ccy,
            "lever": lever,
            "mgnMode": mgn_mode,
            "posSide": pos_side,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-leverage",
            data=data,
            signed=True,
        )

    async def get_max_order_size(
        self,
        inst_id: str,
        td_mode: Literal["cross", "isolated", "cash", "spot_isolated"],
        ccy: str | None = None,
        px: NumberLike | None = None,
        leverage: str | None = None,
        trade_quote_ccy: str | None = None,
        outcome: str | None = None,
    ) -> dict:
        """Получение максимального размера ордера.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-order-quantity
        """
        params = {
            "instId": inst_id,
            "tdMode": td_mode,
            "ccy": ccy,
            "px": px,
            "leverage": leverage,
            "tradeQuoteCcy": trade_quote_ccy,
            "outcome": outcome,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/max-size",
            params=params,
            signed=True,
        )

    async def get_max_avail_size(
        self,
        inst_id: str,
        td_mode: Literal["cross", "isolated", "cash", "spot_isolated"],
        ccy: str | None = None,
        reduce_only: bool | None = None,
        px: NumberLike | None = None,
        trade_quote_ccy: str | None = None,
    ) -> dict:
        """Получение максимального доступного баланса/эквити.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-available-balance-equity
        """
        params = {
            "instId": inst_id,
            "ccy": ccy,
            "tdMode": td_mode,
            "reduceOnly": reduce_only,
            "px": px,
            "tradeQuoteCcy": trade_quote_ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/max-avail-size",
            params=params,
            signed=True,
        )

    async def adjustment_margin(
        self,
        inst_id: str,
        pos_side: Literal["long", "short", "net"],
        type_: Literal["add", "reduce"],
        amt: str,
        ccy: str | None = None,
    ) -> dict:
        """Изменение маржи изолированной позиции.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-increase-decrease-margin
        """
        data = {
            "instId": inst_id,
            "posSide": pos_side,
            "type": type_,
            "amt": amt,
            "ccy": ccy,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/position/margin-balance",
            data=data,
            signed=True,
        )

    async def get_leverage(
        self,
        mgn_mode: Literal["isolated", "cross"],
        inst_id: str | None = None,
        ccy: str | None = None,
    ) -> dict:
        """Получение текущего плеча.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage
        """
        params = {
            "instId": inst_id,
            "ccy": ccy,
            "mgnMode": mgn_mode,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/leverage-info",
            params=params,
            signed=True,
        )

    async def get_leverage_estimated_info(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES"],
        mgn_mode: Literal["isolated", "cross"],
        lever: str,
        inst_id: str | None = None,
        ccy: str | None = None,
        pos_side: Literal["net", "long", "short"] | None = None,
    ) -> dict:
        """Получение оценочных данных по плечу.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-leverage-estimated-info
        """
        params = {
            "instType": inst_type,
            "mgnMode": mgn_mode,
            "lever": lever,
            "instId": inst_id,
            "ccy": ccy,
            "posSide": pos_side,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/adjust-leverage-info",
            params=params,
            signed=True,
        )

    async def get_max_loan(
        self,
        mgn_mode: Literal["isolated", "cross"],
        inst_id: str | None = None,
        ccy: str | None = None,
        mgn_ccy: str | None = None,
        trade_quote_ccy: str | None = None,
    ) -> dict:
        """Получение максимального объема заимствования.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-the-maximum-loan-of-instrument
        """
        params = {
            "mgnMode": mgn_mode,
            "instId": inst_id,
            "ccy": ccy,
            "mgnCcy": mgn_ccy,
            "tradeQuoteCcy": trade_quote_ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/max-loan",
            params=params,
            signed=True,
        )

    async def get_fee_rates(
        self,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"],
        inst_id: str | None = None,
        inst_family: str | None = None,
        rule_type: Literal["normal", "pre_market"] | None = None,
        group_id: str | None = None,
    ) -> dict:
        """Получение торговых комиссий.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-fee-rates
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
            "instFamily": inst_family,
            "ruleType": rule_type,
            "groupId": group_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/trade-fee",
            params=params,
            signed=True,
        )

    async def get_interest_accrued(
        self,
        type_: str | None = None,
        ccy: str | None = None,
        inst_id: str | None = None,
        mgn_mode: Literal["cross", "isolated"] | None = None,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение данных по начисленным процентам.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-interest-accrued-data
        """
        params = {
            "type": type_,
            "ccy": ccy,
            "instId": inst_id,
            "mgnMode": mgn_mode,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/interest-accrued",
            params=params,
            signed=True,
        )

    async def get_interest_rate(self, ccy: str | None = None) -> dict:
        """Получение текущих процентных ставок.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-interest-rate
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/interest-rate",
            params=params,
            signed=True,
        )

    async def set_fee_type(self, fee_type: Literal["0", "1"]) -> dict:
        """Настройка типа комиссии.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-fee-type
        """
        data = {
            "feeType": fee_type,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-fee-type",
            data=data,
            signed=True,
        )

    async def set_greeks(self, greeks_type: Literal["PA", "BS"]) -> dict:
        """Настройка формата греков.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-greeks-pa-bs
        """
        data = {
            "greeksType": greeks_type,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-greeks",
            data=data,
            signed=True,
        )

    async def set_isolated_mode(
        self,
        iso_mode: Literal["auto_transfers_ccy", "automatic"],
        type_: Literal["MARGIN", "CONTRACTS"],
    ) -> dict:
        """Настройка режима изолированной маржи.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-isolated-margin-trading-settings
        """
        data = {
            "isoMode": iso_mode,
            "type": type_,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-isolated-mode",
            data=data,
            signed=True,
        )

    async def get_max_withdrawal(self, ccy: str | None = None) -> dict:
        """Получение максимальной суммы вывода из трейдингового аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-maximum-withdrawals
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/max-withdrawal",
            params=params,
            signed=True,
        )

    async def get_risk_state(self) -> dict:
        """Получение статуса рисков аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-account-risk-state
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/risk-state",
            signed=True,
        )

    async def get_interest_limits(
        self,
        type_: str | None = None,
        ccy: str | None = None,
    ) -> dict:
        """Получение лимитов и процентов заимствования.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-borrow-interest-and-limit
        """
        params = {
            "type": type_,
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/interest-limits",
            params=params,
            signed=True,
        )

    async def spot_manual_borrow_repay(
        self, ccy: str, side: Literal["borrow", "repay"], amt: str
    ) -> dict:
        """Ручное заимствование или погашение в спотовом режиме.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-manual-borrow-repay
        """
        data = {
            "ccy": ccy,
            "side": side,
            "amt": amt,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/spot-manual-borrow-repay",
            data=data,
            signed=True,
        )

    async def set_auto_repay(self, auto_repay: bool) -> dict:
        """Настройка автоматического погашения в спотовом режиме.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-auto-repay
        """
        data = {
            "autoRepay": auto_repay,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-auto-repay",
            data=data,
            signed=True,
        )

    async def spot_borrow_repay_history(
        self,
        ccy: str | None = None,
        type_: Literal["auto_borrow", "auto_repay", "manual_borrow", "manual_repay"] | None = None,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории заимствований и погашений в спотовом режиме.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-borrow-repay-history
        """
        params = {
            "ccy": ccy,
            "type": type_,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/spot-borrow-repay-history",
            params=params,
            signed=True,
        )

    async def position_builder(
        self,
        acct_lv: str | None = None,
        incl_real_pos_and_eq: bool | None = None,
        lever: str | None = None,
        sim_pos: list[dict[str, Any]] | None = None,
        sim_asset: list[dict[str, Any]] | None = None,
        greeks_type: Literal["BS", "PA", "CASH"] | None = None,
        idx_vol: str | None = None,
    ) -> dict:
        """Расчет параметров портфеля с виртуальными позициями.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-new
        """
        data = {
            "acctLv": acct_lv,
            "inclRealPosAndEq": incl_real_pos_and_eq,
            "lever": lever,
            "simPos": sim_pos,
            "simAsset": sim_asset,
            "greeksType": greeks_type,
            "idxVol": idx_vol,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/position-builder",
            data=data,
            signed=True,
        )

    async def position_builder_graph(
        self,
        type_: Literal["mmr"],
        incl_real_pos_and_eq: bool | None = None,
        sim_pos: list[dict[str, Any]] | None = None,
        sim_asset: list[dict[str, Any]] | None = None,
        greeks_type: Literal["BS", "PA", "CASH"] | None = None,
        mmr_config: dict[str, Any] | None = None,
    ) -> dict:
        """Расчет графика тренда риск-параметров.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-trend-graph
        """
        data = {
            "inclRealPosAndEq": incl_real_pos_and_eq,
            "simPos": sim_pos,
            "simAsset": sim_asset,
            "greeksType": greeks_type,
            "type": type_,
            "mmrConfig": mmr_config,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/position-builder-graph",
            data=data,
            signed=True,
        )

    async def set_risk_offset_amount(self, ccy: str, cl_spot_in_use_amt: str) -> dict:
        """Установка величины спотового риск-офсета.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-risk-offset-amount
        """
        data = {
            "ccy": ccy,
            "clSpotInUseAmt": cl_spot_in_use_amt,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-riskOffset-amt",
            data=data,
            signed=True,
        )

    async def get_greeks(self, ccy: str | None = None) -> dict:
        """Получение греков по активам.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-greeks
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/greeks",
            params=params,
            signed=True,
        )

    async def get_account_position_tiers(
        self,
        inst_type: Literal["SWAP", "FUTURES", "OPTION"],
        inst_family: str,
        uly: str | None = None,
    ) -> dict:
        """Получение лимитов позиций в PM режиме.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-pm-position-limitation
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "uly": uly,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/position-tiers",
            params=params,
            signed=True,
        )

    async def activate_option(self) -> dict:
        """Активация торговли опционами.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-activate-option
        """
        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/activate-option",
            data={},
            signed=True,
        )

    async def set_auto_loan(self, auto_loan: bool | None = None) -> dict:
        """Настройка автоматического заимствования.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-auto-loan
        """
        data = {
            "autoLoan": auto_loan,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-auto-loan",
            data=data,
            signed=True,
        )

    async def account_level_switch_preset(
        self,
        acct_lv: Literal["2", "3", "4"],
        lever: str | None = None,
        risk_offset_type: str | None = None,
    ) -> dict:
        """Преднастройка смены режима аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-preset-account-mode-switch
        """
        data = {
            "acctLv": acct_lv,
            "lever": lever,
            "riskOffsetType": risk_offset_type,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/account-level-switch-preset",
            data=data,
            signed=True,
        )

    async def get_account_switch_precheck(self, acct_lv: Literal["1", "2", "3", "4"]) -> dict:
        """Предварительная проверка смены режима аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-precheck-account-mode-switch
        """
        params = {
            "acctLv": acct_lv,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/set-account-switch-precheck",
            params=params,
            signed=True,
        )

    async def set_account_level(self, acct_lv: Literal["1", "2", "3", "4"]) -> dict:
        """Смена режима аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-account-mode
        """
        data = {
            "acctLv": acct_lv,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-account-level",
            data=data,
            signed=True,
        )

    async def set_collateral_assets(
        self,
        type_: Literal["all", "custom"],
        collateral_enabled: bool,
        ccy_list: list[str] | None = None,
    ) -> dict:
        """Настройка списка коллатеральных активов.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-collateral-assets
        """
        data = {
            "type": type_,
            "collateralEnabled": collateral_enabled,
            "ccyList": ccy_list,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-collateral-assets",
            data=data,
            signed=True,
        )

    async def get_collateral_assets(
        self, ccy: str | None = None, collateral_enabled: bool | None = None
    ) -> dict:
        """Получение списка коллатеральных активов.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-collateral-assets
        """
        params = {
            "ccy": ccy,
            "collateralEnabled": collateral_enabled,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/collateral-assets",
            params=params,
            signed=True,
        )

    async def reset_mmp_status(
        self, inst_family: str, inst_type: Literal["OPTION"] | None = None
    ) -> dict:
        """Сброс статуса MMP.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-reset-mmp-status
        """
        data = {
            "instType": inst_type,
            "instFamily": inst_family,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/mmp-reset",
            data=data,
            signed=True,
        )

    async def set_mmp(
        self,
        inst_family: str,
        time_interval: str,
        frozen_interval: str,
        qty_limit: str,
    ) -> dict:
        """Настройка параметров MMP.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-mmp
        """
        data = {
            "instFamily": inst_family,
            "timeInterval": time_interval,
            "frozenInterval": frozen_interval,
            "qtyLimit": qty_limit,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/mmp-config",
            data=data,
            signed=True,
        )

    async def get_mmp_config(self, inst_family: str | None = None) -> dict:
        """Получение настроек MMP.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-mmp-config
        """
        params = {
            "instFamily": inst_family,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/mmp-config",
            params=params,
            signed=True,
        )

    async def move_positions(
        self,
        from_acct: str,
        to_acct: str,
        legs: list[dict[str, Any]],
        client_id: str,
    ) -> dict:
        """Перемещение позиций между аккаунтами.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-move-positions
        """
        data = {
            "fromAcct": from_acct,
            "toAcct": to_acct,
            "legs": legs,
            "clientId": client_id,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/move-positions",
            data=data,
            signed=True,
        )

    async def get_move_positions_history(
        self,
        block_td_id: str | None = None,
        client_id: str | None = None,
        begin_ts: int | None = None,
        end_ts: int | None = None,
        limit: int | None = None,
        state: Literal["filled", "pending"] | None = None,
    ) -> dict:
        """Получение истории перемещения позиций.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-move-positions-history
        """
        params = {
            "blockTdId": block_td_id,
            "clientId": client_id,
            "beginTs": begin_ts,
            "endTs": end_ts,
            "limit": limit,
            "state": state,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/move-positions-history",
            params=params,
            signed=True,
        )

    async def set_auto_earn(
        self,
        ccy: str,
        action: Literal["turn_on", "turn_off"],
        earn_type: Literal["0", "1"] | None = None,
        apr: str | None = None,
    ) -> dict:
        """Настройка автоматического Earn.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-auto-earn
        """
        data = {
            "earnType": earn_type,
            "ccy": ccy,
            "action": action,
            "apr": apr,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-auto-earn",
            data=data,
            signed=True,
        )

    async def set_settle_currency(self, settle_ccy: str) -> dict:
        """Настройка расчетной валюты для USD-маржинальных контрактов.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-settle-currency
        """
        data = {
            "settleCcy": settle_ccy,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-settle-currency",
            data=data,
            signed=True,
        )

    async def get_bill_types(self, type_: str | None = None) -> dict:
        """Получение типов и подтипов записей в истории счёта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bill-types
        """
        params = {
            "type": type_,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/subtypes",
            params=params,
            signed=True,
        )

    async def activate_feature(self, feature: str) -> dict:
        """Активация функции аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-activate-feature
        """
        data = {
            "feature": feature,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/activate-feature",
            data=data,
            signed=True,
        )

    async def set_trading_config(self, type_: str, stgy_type: str | None = None) -> dict:
        """Изменение торговой конфигурации аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-set-trading-config
        """
        data = {
            "type": type_,
            "stgyType": stgy_type,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/account/set-trading-config",
            data=data,
            signed=True,
        )

    async def precheck_set_delta_neutral(self, stgy_type: str) -> dict:
        """Предпроверка перехода в режим delta neutral.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-precheck-set-delta-neutral
        """
        params = {
            "stgyType": stgy_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/precheck-set-delta-neutral",
            params=params,
            signed=True,
        )

    async def get_subaccount_trading_balance(self, sub_acct: str) -> dict:
        """Получение торгового баланса субаккаунта.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-sub-account-trading-balance
        """
        params = {
            "subAcct": sub_acct,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/subaccount/balances",
            params=params,
            signed=True,
        )

    async def get_subaccount_max_withdrawal(self, sub_acct: str, ccy: str | None = None) -> dict:
        """Получение максимальной суммы вывода субаккаунта.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-sub-account-maximum-withdrawals
        """
        params = {
            "subAcct": sub_acct,
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/account/subaccount/max-withdrawal",
            params=params,
            signed=True,
        )

    # topic: Order Book Trading (Trade)

    async def place_order(
        self,
        inst_id: str,
        td_mode: Literal["cross", "isolated", "cash", "spot_isolated"],
        side: Literal["buy", "sell"],
        ord_type: Literal[
            "market",
            "limit",
            "post_only",
            "fok",
            "ioc",
            "optimal_limit_ioc",
            "mmp",
            "mmp_and_post_only",
            "op_fok",
        ],
        sz: NumberLike,
        ccy: str | None = None,
        cl_ord_id: str | None = None,
        tag: str | None = None,
        pos_side: Literal["net", "long", "short"] | None = None,
        px: NumberLike | None = None,
        px_usd: NumberLike | None = None,
        px_vol: NumberLike | None = None,
        reduce_only: bool | None = None,
        tgt_ccy: Literal["base_ccy", "quote_ccy"] | None = None,
        ban_amend: bool | None = None,
        px_amend_type: Literal["0", "1"] | None = None,
        trade_quote_ccy: str | None = None,
        stp_mode: Literal["cancel_maker", "cancel_taker", "cancel_both"] | None = None,
        quick_mgn_type: str | None = None,
        attach_algo_orders: list[dict[str, Any]] | None = None,
        outcome: str | None = None,
        rpi_px_round: bool | None = None,
        rpi_taker_access: bool | None = None,
        slippage_pct: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict:
        """Создание ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order
        """
        data: dict[str, Any] = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
            "ccy": ccy,
            "clOrdId": cl_ord_id,
            "tag": tag,
            "posSide": pos_side,
            "px": px,
            "pxUsd": px_usd,
            "pxVol": px_vol,
            "reduceOnly": reduce_only,
            "tgtCcy": tgt_ccy,
            "banAmend": ban_amend,
            "pxAmendType": px_amend_type,
            "tradeQuoteCcy": trade_quote_ccy,
            "stpMode": stp_mode,
            "quickMgnType": quick_mgn_type,
            "outcome": outcome,
            "rpiPxRound": rpi_px_round,
            "rpiTakerAccess": rpi_taker_access,
            "slippagePct": slippage_pct,
        }
        if attach_algo_orders is not None:
            data["attachAlgoOrds"] = [filter_params(order) for order in attach_algo_orders]
        if extra_params:
            data.update(extra_params)

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/order",
            data=filter_params(data),
            signed=True,
        )

    async def place_multiple_orders(self, orders: list[dict[str, Any]]) -> dict:
        """Создание ордеров пакетно.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-multiple-orders
        """
        data = [filter_params(order) for order in orders]

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/batch-orders",
            data=data,  # type: ignore
            signed=True,
        )

    async def cancel_order(
        self,
        inst_id: str,
        ord_id: str | None = None,
        cl_ord_id: str | None = None,
    ) -> dict:
        """Отмена ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-order
        """
        if not ord_id and not cl_ord_id:
            raise ValueError("Either ord_id or cl_ord_id must be provided")

        data = filter_params(
            {
                "instId": inst_id,
                "ordId": ord_id,
                "clOrdId": cl_ord_id,
            }
        )

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/cancel-order",
            data=data,
            signed=True,
        )

    async def cancel_multiple_orders(self, orders: list[dict[str, Any]]) -> dict:
        """Отмена ордеров пакетно.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-multiple-orders
        """
        data = [filter_params(order) for order in orders]

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/cancel-batch-orders",
            data=data,  # type: ignore
            signed=True,
        )

    async def amend_order(
        self,
        inst_id: str,
        ord_id: str | None = None,
        cl_ord_id: str | None = None,
        *,
        new_sz: NumberLike | None = None,
        new_px: NumberLike | None = None,
        new_px_usd: NumberLike | None = None,
        new_px_vol: NumberLike | None = None,
        cxl_on_fail: bool | None = None,
        req_id: str | None = None,
        px_amend_type: Literal["0", "1"] | None = None,
        attach_algo_orders: list[dict[str, Any]] | None = None,
        rpi_px_round: bool | None = None,
        rpi_taker_access: bool | None = None,
        speed_bump: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict:
        """Изменение параметров ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-order
        """
        if not ord_id and not cl_ord_id:
            raise ValueError("Either ord_id or cl_ord_id must be provided")

        data: dict[str, Any] = {
            "instId": inst_id,
            "ordId": ord_id,
            "clOrdId": cl_ord_id,
            "newSz": new_sz,
            "newPx": new_px,
            "newPxUsd": new_px_usd,
            "newPxVol": new_px_vol,
            "cxlOnFail": cxl_on_fail,
            "reqId": req_id,
            "pxAmendType": px_amend_type,
            "rpiPxRound": rpi_px_round,
            "rpiTakerAccess": rpi_taker_access,
            "speedBump": speed_bump,
        }
        if attach_algo_orders is not None:
            data["attachAlgoOrds"] = [filter_params(order) for order in attach_algo_orders]
        if extra_params:
            data.update(extra_params)

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/amend-order",
            data=filter_params(data),
            signed=True,
        )

    async def amend_multiple_orders(self, orders: list[dict[str, Any]]) -> dict:
        """Изменение параметров ордеров пакетно.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-amend-multiple-orders
        """
        data = [filter_params(order) for order in orders]

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/amend-batch-orders",
            data=data,  # type: ignore
            signed=True,
        )

    async def close_positions(
        self,
        inst_id: str,
        mgn_mode: Literal["cross", "isolated"],
        pos_side: Literal["net", "long", "short"] | None = None,
        ccy: str | None = None,
        auto_cxl: bool | None = None,
        cl_ord_id: str | None = None,
        tag: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict:
        """Закрытие позиции рыночным ордером.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-close-positions
        """
        data: dict[str, Any] = {
            "instId": inst_id,
            "mgnMode": mgn_mode,
            "posSide": pos_side,
            "ccy": ccy,
            "autoCxl": auto_cxl,
            "clOrdId": cl_ord_id,
            "tag": tag,
        }
        if extra_params:
            data.update(extra_params)

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/close-position",
            data=filter_params(data),
            signed=True,
        )

    async def get_order(
        self,
        inst_id: str,
        ord_id: str | None = None,
        cl_ord_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-order-details
        """
        if not ord_id and not cl_ord_id:
            raise ValueError("Either ord_id or cl_ord_id must be provided")

        params = filter_params(
            {
                "instId": inst_id,
                "ordId": ord_id,
                "clOrdId": cl_ord_id,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/order",
            params=params,
            signed=True,
        )

    async def get_order_list(
        self,
        inst_type: str | None = None,
        inst_family: str | None = None,
        inst_id: str | None = None,
        ord_type: str | None = None,
        state: Literal["live", "partially_filled"] | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение списка активных ордеров.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-order-list
        """
        params = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "instId": inst_id,
                "ordType": ord_type,
                "state": state,
                "after": after,
                "before": before,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/orders-pending",
            params=params,
            signed=True,
        )

    async def get_orders_history(
        self,
        inst_type: str,
        inst_family: str | None = None,
        inst_id: str | None = None,
        ord_type: str | None = None,
        state: str | None = None,
        category: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории ордеров за 7 дней.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-order-history-last-7-days
        """
        params = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "instId": inst_id,
                "ordType": ord_type,
                "state": state,
                "category": category,
                "after": after,
                "before": before,
                "begin": begin,
                "end": end,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/orders-history",
            params=params,
            signed=True,
        )

    async def get_orders_history_archive(
        self,
        inst_type: str,
        inst_family: str | None = None,
        inst_id: str | None = None,
        ord_type: str | None = None,
        state: str | None = None,
        category: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории ордеров за 3 месяца.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-order-history-last-3-months
        """
        params = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "instId": inst_id,
                "ordType": ord_type,
                "state": state,
                "category": category,
                "after": after,
                "before": before,
                "begin": begin,
                "end": end,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/orders-history-archive",
            params=params,
            signed=True,
        )

    async def get_fills(
        self,
        inst_type: str | None = None,
        inst_family: str | None = None,
        inst_id: str | None = None,
        ord_id: str | None = None,
        sub_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение сделок за 3 дня.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-transaction-details-last-3-days
        """
        params = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "instId": inst_id,
                "ordId": ord_id,
                "subType": sub_type,
                "after": after,
                "before": before,
                "begin": begin,
                "end": end,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/fills",
            params=params,
            signed=True,
        )

    async def get_fills_history(
        self,
        inst_type: str,
        inst_family: str | None = None,
        inst_id: str | None = None,
        ord_id: str | None = None,
        sub_type: str | None = None,
        after: str | None = None,
        before: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение сделок за 3 месяца.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-transaction-details-last-3-months
        """
        params = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "instId": inst_id,
                "ordId": ord_id,
                "subType": sub_type,
                "after": after,
                "before": before,
                "begin": begin,
                "end": end,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/fills-history",
            params=params,
            signed=True,
        )

    async def get_easy_convert_currency_list(self, source: Literal["1", "2"] | None = None) -> dict:
        """Получение списка валют для Easy Convert.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-easy-convert-currency-list
        """
        params = filter_params({"source": source})

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/easy-convert-currency-list",
            params=params,
            signed=True,
        )

    async def easy_convert(
        self,
        from_ccy: list[str],
        to_ccy: str,
        source: Literal["1", "2"] | None = None,
    ) -> dict:
        """Конвертация мелких остатков через Easy Convert.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-easy-convert
        """
        data = filter_params(
            {
                "fromCcy": from_ccy,
                "toCcy": to_ccy,
                "source": source,
            }
        )

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/easy-convert",
            data=data,
            signed=True,
        )

    async def get_easy_convert_history(
        self,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории Easy Convert.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-easy-convert-history
        """
        params = filter_params(
            {
                "after": after,
                "before": before,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/easy-convert-history",
            params=params,
            signed=True,
        )

    async def get_one_click_repay_currency_list(
        self,
        debt_type: Literal["cross", "isolated"] | None = None,
    ) -> dict:
        """Получение списка валют для One-click Repay.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-currency-list
        """
        params = filter_params({"debtType": debt_type})

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/one-click-repay-currency-list",
            params=params,
            signed=True,
        )

    async def trade_one_click_repay(
        self,
        debt_ccy: list[str],
        repay_ccy: str,
    ) -> dict:
        """Совершение One-click Repay.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-trade-one-click-repay
        """
        data = filter_params({"debtCcy": debt_ccy, "repayCcy": repay_ccy})

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/one-click-repay",
            data=data,
            signed=True,
        )

    async def get_one_click_repay_history(
        self,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории One-click Repay.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-history
        """
        params = filter_params(
            {
                "after": after,
                "before": before,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/one-click-repay-history",
            params=params,
            signed=True,
        )

    async def get_one_click_repay_currency_list_v2(self) -> dict:
        """Получение списка валют для One-click Repay (v2).

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-currency-list-new
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/one-click-repay-currency-list-v2",
            signed=True,
        )

    async def trade_one_click_repay_v2(
        self,
        debt_ccy: str,
        repay_ccy_list: list[str],
    ) -> dict:
        """Совершение One-click Repay (v2).

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-trade-one-click-repay-new
        """
        data = filter_params({"debtCcy": debt_ccy, "repayCcyList": repay_ccy_list})

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/one-click-repay-v2",
            data=data,
            signed=True,
        )

    async def get_one_click_repay_history_v2(
        self,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории One-click Repay (v2).

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-one-click-repay-history-new
        """
        params = filter_params(
            {
                "after": after,
                "before": before,
                "limit": limit,
            }
        )

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/one-click-repay-history-v2",
            params=params,
            signed=True,
        )

    async def mass_cancel_orders(
        self,
        inst_type: Literal["OPTION"],
        inst_family: str,
        lock_interval: str | None = None,
    ) -> dict:
        """Массовое снятие MMP-ордеров.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-mass-cancel-order
        """
        data = filter_params(
            {
                "instType": inst_type,
                "instFamily": inst_family,
                "lockInterval": lock_interval,
            }
        )

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/mass-cancel",
            data=data,
            signed=True,
        )

    async def cancel_all_after(
        self,
        time_out: str,
        tag: str | None = None,
    ) -> dict:
        """Установка Cancel All After.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-all-after
        """
        data = filter_params({"timeOut": time_out, "tag": tag})

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/cancel-all-after",
            data=data,
            signed=True,
        )

    async def get_account_rate_limit(self) -> dict:
        """Получение информации о лимитах запросов аккаунта.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-account-rate-limit
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/account-rate-limit",
            signed=True,
        )

    async def order_precheck(
        self,
        inst_id: str,
        td_mode: Literal["cross", "isolated", "cash", "spot_isolated"],
        side: Literal["buy", "sell"],
        ord_type: Literal[
            "market",
            "limit",
            "post_only",
            "fok",
            "ioc",
            "optimal_limit_ioc",
        ],
        sz: NumberLike,
        pos_side: Literal["net", "long", "short"] | None = None,
        px: NumberLike | None = None,
        reduce_only: bool | None = None,
        tgt_ccy: Literal["base_ccy", "quote_ccy"] | None = None,
        attach_algo_orders: list[dict[str, Any]] | None = None,
        outcome: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> dict:
        """Превентивная проверка перед размещением ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-order-precheck
        """
        data: dict[str, Any] = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
            "posSide": pos_side,
            "px": px,
            "reduceOnly": reduce_only,
            "tgtCcy": tgt_ccy,
            "outcome": outcome,
        }
        if attach_algo_orders is not None:
            data["attachAlgoOrds"] = [filter_params(order) for order in attach_algo_orders]
        if extra_params:
            data.update(extra_params)

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/order-precheck",
            data=filter_params(data),
            signed=True,
        )

    # topic: Order Book Trading (Algo Trading)

    async def place_algo_order(
        self,
        inst_id: str,
        td_mode: str,
        side: str,
        ord_type: str,
        ccy: str | None = None,
        pos_side: str | None = None,
        sz: NumberLike | None = None,
        tag: str | None = None,
        tgt_ccy: str | None = None,
        algo_cl_ord_id: str | None = None,
        close_fraction: str | None = None,
        trade_quote_ccy: str | None = None,
        tp_trigger_px: NumberLike | None = None,
        tp_trigger_px_type: str | None = None,
        tp_ord_px: NumberLike | None = None,
        tp_ord_kind: str | None = None,
        sl_trigger_px: NumberLike | None = None,
        sl_trigger_px_type: str | None = None,
        sl_ord_px: NumberLike | None = None,
        cxl_on_close_pos: bool | None = None,
        reduce_only: bool | None = None,
        chase_type: str | None = None,
        chase_val: str | None = None,
        max_chase_type: str | None = None,
        max_chase_val: str | None = None,
        trigger_px: NumberLike | None = None,
        order_px: NumberLike | None = None,
        advance_ord_type: str | None = None,
        adv_chase_params: list[Any] | None = None,
        trigger_px_type: str | None = None,
        attach_algo_ords: list[Any] | None = None,
        callback_ratio: NumberLike | None = None,
        callback_spread: NumberLike | None = None,
        active_px: NumberLike | None = None,
        px_var: str | None = None,
        px_spread: str | None = None,
        sz_limit: str | None = None,
        px_limit: str | None = None,
        time_interval: str | None = None,
        lmt_order_number: str | None = None,
        aggressiveness: str | None = None,
        trigger_params: list[Any] | None = None,
    ) -> dict:
        """Создание алгоритмического ордера (TP/SL, trigger, trailing, TWAP, chase).

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-post-place-algo-order
        """
        data = {
            "instId": inst_id,
            "tdMode": td_mode,
            "ccy": ccy,
            "side": side,
            "posSide": pos_side,
            "ordType": ord_type,
            "sz": sz,
            "tag": tag,
            "tgtCcy": tgt_ccy,
            "algoClOrdId": algo_cl_ord_id,
            "closeFraction": close_fraction,
            "tradeQuoteCcy": trade_quote_ccy,
            "tpTriggerPx": tp_trigger_px,
            "tpTriggerPxType": tp_trigger_px_type,
            "tpOrdPx": tp_ord_px,
            "tpOrdKind": tp_ord_kind,
            "slTriggerPx": sl_trigger_px,
            "slTriggerPxType": sl_trigger_px_type,
            "slOrdPx": sl_ord_px,
            "cxlOnClosePos": cxl_on_close_pos,
            "reduceOnly": reduce_only,
            "chaseType": chase_type,
            "chaseVal": chase_val,
            "maxChaseType": max_chase_type,
            "maxChaseVal": max_chase_val,
            "triggerPx": trigger_px,
            "orderPx": order_px,
            "advanceOrdType": advance_ord_type,
            "advChaseParams": adv_chase_params,
            "triggerPxType": trigger_px_type,
            "attachAlgoOrds": attach_algo_ords,
            "callbackRatio": callback_ratio,
            "callbackSpread": callback_spread,
            "activePx": active_px,
            "pxVar": px_var,
            "pxSpread": px_spread,
            "szLimit": sz_limit,
            "pxLimit": px_limit,
            "timeInterval": time_interval,
            "lmtOrderNumber": lmt_order_number,
            "aggressiveness": aggressiveness,
            "triggerParams": trigger_params,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/order-algo",
            data=data,
            signed=True,
        )

    async def cancel_algo_orders(self, orders: list[dict[str, Any]]) -> dict:
        """Отмена алгоритмических ордеров (до 10 за запрос).

        Элемент списка: `{"instId": ..., "algoId": ...}` или `{"instId": ..., "algoClOrdId": ...}`.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-post-cancel-algo-order
        """
        data = [filter_params(order) for order in orders]

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/cancel-algos",
            data=data,  # type: ignore
            signed=True,
        )

    async def amend_algo_order(
        self,
        inst_id: str,
        algo_id: str | None = None,
        algo_cl_ord_id: str | None = None,
        cxl_on_fail: bool | None = None,
        req_id: str | None = None,
        new_sz: NumberLike | None = None,
        new_tp_trigger_px: str | None = None,
        new_tp_ord_px: str | None = None,
        new_sl_trigger_px: str | None = None,
        new_sl_ord_px: str | None = None,
        new_tp_trigger_px_type: str | None = None,
        new_sl_trigger_px_type: str | None = None,
        new_trigger_px: str | None = None,
        new_ord_px: str | None = None,
        new_trigger_px_type: str | None = None,
        attach_algo_ords: list[Any] | None = None,
        adv_chase_params: list[Any] | None = None,
    ) -> dict:
        """Изменение алгоритмического ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-post-amend-algo-order
        """
        data = {
            "instId": inst_id,
            "algoId": algo_id,
            "algoClOrdId": algo_cl_ord_id,
            "cxlOnFail": cxl_on_fail,
            "reqId": req_id,
            "newSz": new_sz,
            "newTpTriggerPx": new_tp_trigger_px,
            "newTpOrdPx": new_tp_ord_px,
            "newSlTriggerPx": new_sl_trigger_px,
            "newSlOrdPx": new_sl_ord_px,
            "newTpTriggerPxType": new_tp_trigger_px_type,
            "newSlTriggerPxType": new_sl_trigger_px_type,
            "newTriggerPx": new_trigger_px,
            "newOrdPx": new_ord_px,
            "newTriggerPxType": new_trigger_px_type,
            "attachAlgoOrds": attach_algo_ords,
            "advChaseParams": adv_chase_params,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/trade/amend-algos",
            data=data,
            signed=True,
        )

    async def get_algo_order_details(
        self,
        algo_id: str | None = None,
        algo_cl_ord_id: str | None = None,
    ) -> dict:
        """Получение информации об алгоритмическом ордере.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-get-algo-order-details
        """
        params = {
            "algoId": algo_id,
            "algoClOrdId": algo_cl_ord_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/order-algo",
            params=params,
            signed=True,
        )

    async def get_algo_order_list(
        self,
        ord_type: str,
        algo_id: str | None = None,
        inst_type: str | None = None,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение активных алгоритмических ордеров.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-get-algo-order-list
        """
        params = {
            "ordType": ord_type,
            "algoId": algo_id,
            "instType": inst_type,
            "instId": inst_id,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/orders-algo-pending",
            params=params,
            signed=True,
        )

    async def get_algo_order_history(
        self,
        ord_type: str,
        state: str | None = None,
        algo_id: str | None = None,
        inst_type: str | None = None,
        inst_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории алгоритмических ордеров.

        https://www.okx.com/docs-v5/en/#order-book-trading-algo-trading-get-algo-order-history
        """
        params = {
            "ordType": ord_type,
            "state": state,
            "algoId": algo_id,
            "instType": inst_type,
            "instId": inst_id,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/trade/orders-algo-history",
            params=params,
            signed=True,
        )

    # topic: Order Book Trading (Market Data)

    async def get_tickers(
        self,
        inst_type: Literal["SPOT", "SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
    ) -> dict:
        """Получение списка тикеров с основными метриками.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-tickers
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/tickers",
            params=params,
        )

    async def get_ticker(self, inst_id: str) -> dict:
        """Получение тикера инструмента с данными за 24 часа.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-ticker
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/ticker",
            params=params,
        )

    async def get_order_book(self, inst_id: str, sz: int | None = None) -> dict:
        """Получение книги ордеров с обновлением каждые 50 мс.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-order-book
        """
        params = {
            "instId": inst_id,
            "sz": sz,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/books",
            params=params,
        )

    async def get_full_order_book(self, inst_id: str, sz: int | None = None) -> dict:
        """Получение полной книги ордеров с глубиной до 5000 уровней.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-full-order-book
        """
        params = {
            "instId": inst_id,
            "sz": sz,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/books-full",
            params=params,
        )

    async def get_candlesticks(
        self,
        inst_id: str,
        bar: str | None = None,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
        adjust: str | None = None,
    ) -> dict:
        """Получение списка свечей с максимальной глубиной в 1440 записей.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
        """
        params = {
            "instId": inst_id,
            "bar": bar,
            "after": after,
            "before": before,
            "limit": limit,
            "adjust": adjust,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/candles",
            params=params,
        )

    async def get_candlesticks_history(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        bar: str | None = None,
        limit: int | None = None,
        adjust: str | None = None,
    ) -> dict:
        """Получение исторических свечей за прошлые периоды.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks-history
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "bar": bar,
            "limit": limit,
            "adjust": adjust,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/history-candles",
            params=params,
        )

    async def get_trades(self, inst_id: str, limit: int | None = None) -> dict:
        """Получение последних сделок по инструменту.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-trades
        """
        params = {
            "instId": inst_id,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/trades",
            params=params,
        )

    async def get_trades_history(
        self,
        inst_id: str,
        type_: Literal["1", "2"] | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории сделок с пагинацией за последние три месяца.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-trades-history
        """
        params = {
            "instId": inst_id,
            "type": type_,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/history-trades",
            params=params,
        )

    async def get_option_trades_by_family(self, inst_family: str) -> dict:
        """Получение сделок по всем опционам в рамках семьи инструментов.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-option-trades-by-instrument-family
        """
        params = {
            "instFamily": inst_family,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/option/instrument-family-trades",
            params=params,
        )

    async def get_option_trades(
        self,
        inst_id: str | None = None,
        inst_family: str | None = None,
        opt_type: Literal["C", "P"] | None = None,
    ) -> dict:
        """Получение сделок по выбранным опционам.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-option-trades
        """
        params = {
            "instId": inst_id,
            "instFamily": inst_family,
            "optType": opt_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/option-trades",
            params=params,
        )

    async def get_24h_total_volume(self) -> dict:
        """Получение совокупного 24-часового объема торгов по платформе.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-24h-total-volume
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/platform-24-volume",
        )

    async def get_call_auction_details(self, inst_id: str) -> dict:
        """Получение данных по предторговому аукциону инструмента.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-call-auction-details
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/call-auction-details",
            params=params,
        )

    async def get_rpi_order_book(self, inst_id: str, sz: NumberLike | None = None) -> dict:
        """Получение книги ордеров с RPI-ордерами.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-rpi-order-book
        """
        params = {
            "instId": inst_id,
            "sz": sz,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/books-rpi",
            params=params,
        )

    async def get_block_tickers(self, inst_type: str, inst_family: str | None = None) -> dict:
        """Получение тикеров блочных сделок.

        https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-tickers
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/block-tickers",
            params=params,
        )

    async def get_block_ticker(self, inst_id: str) -> dict:
        """Получение тикера блочных сделок по инструменту.

        https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-block-ticker
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/block-ticker",
            params=params,
        )

    async def get_public_block_trades(self, inst_id: str) -> dict:
        """Получение публичных блочных сделок (single-leg).

        https://www.okx.com/docs-v5/en/#block-trading-rest-api-get-public-single-leg-transactions-of-block-trades
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/block-trades",
            params=params,
        )

    # topic: Public Data

    async def get_instruments(
        self,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
        inst_id: str | None = None,
        series_id: str | None = None,
    ) -> dict:
        """Получение списка доступных публичных инструментов.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-instruments
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "instId": inst_id,
            "seriesId": series_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/instruments",
            params=params,
        )

    async def get_estimated_delivery_price(self, inst_id: str) -> dict:
        """Получение оценочной цены поставки или исполнения опциона.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-estimated-delivery-exercise-price
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/estimated-price",
            params=params,
        )

    async def get_delivery_exercise_history(
        self,
        inst_type: Literal["FUTURES", "OPTION"],
        inst_family: str,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории поставок и исполнений за последние три месяца.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-delivery-exercise-history
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/delivery-exercise-history",
            params=params,
        )

    async def get_estimated_settlement_info(self, inst_id: str) -> dict:
        """Получение оценочной цены ближайшего расчета по фьючерсу.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-estimated-future-settlement-price
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/estimated-settlement-info",
            params=params,
        )

    async def get_futures_settlement_history(
        self,
        inst_family: str,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории расчетов фьючерсов за последние три месяца.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-futures-settlement-history
        """
        params = {
            "instFamily": inst_family,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/settlement-history",
            params=params,
        )

    async def get_funding_rate(self, inst_id: str | Literal["ANY"]) -> dict:
        """Получение текущей ставки финансирования.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/funding-rate",
            params=params,
        )

    async def get_funding_rate_history(
        self,
        inst_id: str,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории ставок финансирования за последние три месяца.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate-history
        """
        params = {
            "instId": inst_id,
            "before": before,
            "after": after,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/funding-rate-history",
            params=params,
        )

    async def get_open_interest(
        self,
        inst_type: Literal["SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
        inst_id: str | None = None,
    ) -> dict:
        """Получение общего открытого интереса по контрактам OKX.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-open-interest
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/open-interest",
            params=params,
        )

    async def get_price_limit(self, inst_id: str) -> dict:
        """Получение верхнего и нижнего лимитов цен для инструмента.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-limit-price
        """
        params = {
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/price-limit",
            params=params,
        )

    async def get_option_market_data(
        self,
        inst_family: str,
        exp_time: str | None = None,
    ) -> dict:
        """Получение сводных рыночных данных по опционам.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-option-market-data
        """
        params = {
            "instFamily": inst_family,
            "expTime": exp_time,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/opt-summary",
            params=params,
        )

    async def get_discount_rate_quota(
        self,
        ccy: str | None = None,
        discount_lv: str | None = None,
    ) -> dict:
        """Получение ставок скидок и беспроцентных квот.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-discount-rate-and-interest-free-quota
        """
        params = {
            "ccy": ccy,
            "discountLv": discount_lv,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/discount-rate-interest-free-quota",
            params=params,
        )

    async def get_system_time(self) -> dict:
        """Получение времени сервера OKX.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-system-time
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/time",
        )

    async def get_mark_price(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
        inst_id: str | None = None,
    ) -> dict:
        """Получение маржинальной цены инструмента.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/mark-price",
            params=params,
        )

    async def get_position_tiers(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"],
        td_mode: Literal["cross", "isolated"],
        inst_family: str | None = None,
        inst_id: str | None = None,
        ccy: str | None = None,
        tier: str | None = None,
    ) -> dict:
        """Получение уровней позиций и допустимого плеча.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-position-tiers
        """
        params = {
            "instType": inst_type,
            "tdMode": td_mode,
            "instFamily": inst_family,
            "instId": inst_id,
            "ccy": ccy,
            "tier": tier,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/position-tiers",
            params=params,
        )

    async def get_interest_rate_loan_quota(self) -> dict:
        """Получение ставок и квот заимствования.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-interest-rate-and-loan-quota
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/interest-rate-loan-quota",
        )

    async def get_underlying(self, inst_type: Literal["SWAP", "FUTURES", "OPTION"]) -> dict:
        """Получение списка базовых активов по типу инструмента.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-underlying
        """
        params = {
            "instType": inst_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/underlying",
            params=params,
        )

    async def get_insurance_fund(
        self,
        inst_type: Literal["MARGIN", "SWAP", "FUTURES", "OPTION"],
        type_: Literal[
            "regular_update",
            "liquidation_balance_deposit",
            "bankruptcy_loss",
            "platform_revenue",
            "adl",
        ]
        | None = None,
        inst_family: str | None = None,
        ccy: str | None = None,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение данных страхового фонда.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-insurance-fund
        """
        params = {
            "instType": inst_type,
            "type": type_,
            "instFamily": inst_family,
            "ccy": ccy,
            "before": before,
            "after": after,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/insurance-fund",
            params=params,
        )

    async def convert_contract_coin(
        self,
        inst_id: str,
        sz: NumberLike,
        type_: Literal["1", "2"] | None = None,
        px: NumberLike | None = None,
        unit: Literal["coin", "usds"] | None = None,
        op_type: Literal["open", "close"] | None = None,
    ) -> dict:
        """Конвертация размера контракта и количества монет.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-unit-convert
        """
        params = {
            "type": type_,
            "instId": inst_id,
            "sz": sz,
            "px": px,
            "unit": unit,
            "opType": op_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/convert-contract-coin",
            params=params,
        )

    async def get_option_tick_bands(self, inst_family: str | None = None) -> dict:
        """Получение доступных ценовых диапазонов опционов.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-option-tick-bands
        """
        params = {
            "instType": "OPTION",
            "instFamily": inst_family,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/instrument-tick-bands",
            params=params,
        )

    async def get_premium_history(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение истории премии индекса за полгода.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-premium-history
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/premium-history",
            params=params,
        )

    async def get_index_tickers(
        self,
        quote_ccy: str | None = None,
        inst_id: str | None = None,
    ) -> dict:
        """Получение индексов и ключевых метрик по ним.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-tickers
        """
        params = {
            "quoteCcy": quote_ccy,
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/index-tickers",
            params=params,
        )

    async def get_index_candlesticks(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        bar: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение свечей по индексным значениям.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "bar": bar,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/index-candles",
            params=params,
        )

    async def get_index_candlesticks_history(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        bar: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение исторических свечей по индексам.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-candlesticks-history
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "bar": bar,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/history-index-candles",
            params=params,
        )

    async def get_mark_price_candlesticks(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        bar: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение свечей по маржинальной цене инструмента.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price-candlesticks
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "bar": bar,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/mark-price-candles",
            params=params,
        )

    async def get_mark_price_candlesticks_history(
        self,
        inst_id: str,
        after: int | None = None,
        before: int | None = None,
        bar: str | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение исторических свечей по маржинальной цене.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mark-price-candlesticks-history
        """
        params = {
            "instId": inst_id,
            "after": after,
            "before": before,
            "bar": bar,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/history-mark-price-candles",
            params=params,
        )

    async def get_exchange_rate(self) -> dict:
        """Получение средневзвешенного курса USD/CNY за две недели.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-exchange-rate
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/exchange-rate",
        )

    async def get_index_components(self, index: str) -> dict:
        """Получение состава выбранного индекса.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-index-components
        """
        params = {
            "index": index,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/market/index-components",
            params=params,
        )

    async def get_economic_calendar(
        self,
        region: str | None = None,
        importance: Literal["1", "2", "3"] | None = None,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение данных макроэкономического календаря.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-economic-calendar-data
        """
        params = {
            "region": region,
            "importance": importance,
            "before": before,
            "after": after,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/economic-calendar",
            params=params,
            signed=True,
        )

    async def get_market_data_history(
        self,
        module: Literal["1", "2", "3", "6"],
        inst_type: Literal["SPOT", "FUTURES", "SWAP", "OPTION"],
        begin: int,
        end: int,
        inst_id_list: str | None = None,
        inst_family_list: str | None = None,
        date_aggr_type: Literal["daily", "monthly"] = "daily",
    ) -> dict:
        """Получение ссылок на исторические рыночные данные OKX.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-historical-market-data
        """
        params = {
            "module": module,
            "instType": inst_type,
            "instIdList": inst_id_list,
            "instFamilyList": inst_family_list,
            "dateAggrType": date_aggr_type,
            "begin": begin,
            "end": end,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/market-data-history",
            params=params,
        )

    async def get_corporate_actions(
        self,
        ticker: str | None = None,
        inst_id: str | None = None,
        limit: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> dict:
        """Получение корпоративных действий по акционным контрактам.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-corporate-actions
        """
        params = {
            "ticker": ticker,
            "instId": inst_id,
            "limit": limit,
            "after": after,
            "before": before,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/corporate-actions",
            params=params,
        )

    async def get_delta_hedge_currencies(self, ccy: str | None = None) -> dict:
        """Получение валют, образующих delta hedge (например ETH и BETH).

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-delta-hedge-currencies
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/delta-hedge-currencies",
            params=params,
        )

    async def get_mm_instrument_types(
        self,
        inst_type: str | None = None,
        inst_id: str | None = None,
    ) -> dict:
        """Получение классификации инструментов программы маркет-мейкеров.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-mm-instrument-types
        """
        params = {
            "instType": inst_type,
            "instId": inst_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/mm-instrument-types",
            params=params,
        )

    async def get_event_contract_series(self, series_id: str | None = None) -> dict:
        """Получение серий event-контрактов.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-series
        """
        params = {
            "seriesId": series_id,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/event-contract/series",
            params=params,
        )

    async def get_event_contract_events(
        self,
        series_id: str,
        event_id: str | None = None,
        state: str | None = None,
        limit: str | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> dict:
        """Получение событий event-контрактов.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-events
        """
        params = {
            "seriesId": series_id,
            "eventId": event_id,
            "state": state,
            "limit": limit,
            "before": before,
            "after": after,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/event-contract/events",
            params=params,
        )

    async def get_event_contract_markets(
        self,
        series_id: str,
        event_id: str | None = None,
        inst_id: str | None = None,
        state: str | None = None,
        limit: str | None = None,
        before: str | None = None,
        after: str | None = None,
    ) -> dict:
        """Получение рынков event-контрактов.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-markets
        """
        params = {
            "seriesId": series_id,
            "eventId": event_id,
            "instId": inst_id,
            "state": state,
            "limit": limit,
            "before": before,
            "after": after,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/public/event-contract/markets",
            params=params,
        )

    # topic: Trading Statistics

    async def get_long_short_account_ratio_contract(
        self,
        inst_id: str,
        period: str | None = None,
        begin: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение соотношения лонгов и шортов по аккаунтам для контракта.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-contract-long-short-ratio
        """
        params = {
            "instId": inst_id,
            "period": period,
            "begin": begin,
            "end": end,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/long-short-account-ratio-contract",
            params=params,
        )

    async def get_support_coin(self) -> dict:
        """Получение списка валют, поддерживаемых торговой статистикой.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-support-coin
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/trading-data/support-coin",
        )

    async def get_contract_open_interest_history(
        self,
        inst_id: str,
        period: str | None = None,
        end: str | None = None,
        begin: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории открытого интереса по контракту.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-contract-open-interest-history
        """
        params = {
            "instId": inst_id,
            "period": period,
            "end": end,
            "begin": begin,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/open-interest-history",
            params=params,
        )

    async def get_taker_volume(
        self,
        ccy: str,
        inst_type: str,
        begin: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict:
        """Получение объёма тейкеров на покупку и продажу.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-taker-volume
        """
        params = {
            "ccy": ccy,
            "instType": inst_type,
            "begin": begin,
            "end": end,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/taker-volume",
            params=params,
        )

    async def get_contract_taker_volume(
        self,
        inst_id: str,
        period: str | None = None,
        unit: str | None = None,
        end: str | None = None,
        begin: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение объёма тейкеров по контракту.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-contract-taker-volume
        """
        params = {
            "instId": inst_id,
            "period": period,
            "unit": unit,
            "end": end,
            "begin": begin,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/taker-volume-contract",
            params=params,
        )

    async def get_margin_loan_ratio(
        self,
        ccy: str,
        begin: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict:
        """Получение соотношения лонгов и шортов в марже.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-margin-long-short-ratio
        """
        params = {
            "ccy": ccy,
            "begin": begin,
            "end": end,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/margin/loan-ratio",
            params=params,
        )

    async def get_long_short_account_ratio(
        self,
        ccy: str,
        begin: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict:
        """Получение соотношения аккаунтов в лонге и шорте по валюте.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-long-short-ratio
        """
        params = {
            "ccy": ccy,
            "begin": begin,
            "end": end,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/long-short-account-ratio",
            params=params,
        )

    async def get_top_trader_long_short_account_ratio(
        self,
        inst_id: str,
        period: str | None = None,
        end: str | None = None,
        begin: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение соотношения лонгов и шортов топ-трейдеров (по аккаунтам).

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-top-traders-contract-long-short-ratio
        """
        params = {
            "instId": inst_id,
            "period": period,
            "end": end,
            "begin": begin,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader",
            params=params,
        )

    async def get_top_trader_long_short_position_ratio(
        self,
        inst_id: str,
        period: str | None = None,
        end: str | None = None,
        begin: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение соотношения лонгов и шортов топ-трейдеров (по позициям).

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-top-traders-contract-long-short-ratio-by-position
        """
        params = {
            "instId": inst_id,
            "period": period,
            "end": end,
            "begin": begin,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader",
            params=params,
        )

    async def get_contracts_open_interest_volume(
        self,
        ccy: str,
        begin: str | None = None,
        end: str | None = None,
        period: str | None = None,
    ) -> dict:
        """Получение открытого интереса и объёма по контрактам.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-contracts-open-interest-and-volume
        """
        params = {
            "ccy": ccy,
            "begin": begin,
            "end": end,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/contracts/open-interest-volume",
            params=params,
        )

    async def get_options_open_interest_volume(self, ccy: str, period: str | None = None) -> dict:
        """Получение открытого интереса и объёма опционов.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-options-open-interest-and-volume
        """
        params = {
            "ccy": ccy,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/option/open-interest-volume",
            params=params,
        )

    async def get_put_call_ratio(self, ccy: str, period: str | None = None) -> dict:
        """Получение соотношения put/call.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-put-call-ratio
        """
        params = {
            "ccy": ccy,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/option/open-interest-volume-ratio",
            params=params,
        )

    async def get_options_open_interest_volume_expiry(
        self,
        ccy: str,
        period: str | None = None,
    ) -> dict:
        """Получение открытого интереса и объёма опционов по экспирации.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-open-interest-and-volume-expiry
        """
        params = {
            "ccy": ccy,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/option/open-interest-volume-expiry",
            params=params,
        )

    async def get_options_open_interest_volume_strike(
        self,
        ccy: str,
        exp_time: str,
        period: str | None = None,
    ) -> dict:
        """Получение открытого интереса и объёма опционов по страйку.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-open-interest-and-volume-strike
        """
        params = {
            "ccy": ccy,
            "expTime": exp_time,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/option/open-interest-volume-strike",
            params=params,
        )

    async def get_option_taker_flow(self, ccy: str, period: str | None = None) -> dict:
        """Получение потока тейкеров по опционам.

        https://www.okx.com/docs-v5/en/#trading-statistics-rest-api-get-taker-flow
        """
        params = {
            "ccy": ccy,
            "period": period,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/rubik/stat/option/taker-block-volume",
            params=params,
        )

    # topic: Funding Account

    async def get_currencies(self, ccy: str | None = None) -> dict:
        """Получение списка валют.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-currencies
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/currencies",
            params=params,
            signed=True,
        )

    async def get_funding_balance(self, ccy: str | None = None) -> dict:
        """Получение баланса финансового аккаунта.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-balance
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/balances",
            params=params,
            signed=True,
        )

    async def get_non_tradable_assets(self, ccy: str | None = None) -> dict:
        """Получение неторгуемых активов.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-non-tradable-assets
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/non-tradable-assets",
            params=params,
            signed=True,
        )

    async def get_asset_valuation(self, ccy: str | None = None) -> dict:
        """Получение оценки активов аккаунта.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-account-asset-valuation
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/asset-valuation",
            params=params,
            signed=True,
        )

    async def funds_transfer(
        self,
        ccy: str,
        amt: NumberLike,
        from_: str,
        to: str,
        type_: str | None = None,
        sub_acct: str | None = None,
        loan_trans: bool | None = None,
        omit_pos_risk: str | None = None,
        client_id: str | None = None,
    ) -> dict:
        """Перевод средств между аккаунтами.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-funds-transfer
        """
        data = {
            "type": type_,
            "ccy": ccy,
            "amt": amt,
            "from": from_,
            "to": to,
            "subAcct": sub_acct,
            "loanTrans": loan_trans,
            "omitPosRisk": omit_pos_risk,
            "clientId": client_id,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/transfer",
            data=data,
            signed=True,
        )

    async def get_transfer_state(
        self,
        trans_id: str | None = None,
        client_id: str | None = None,
        type_: str | None = None,
    ) -> dict:
        """Получение статуса перевода средств.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-funds-transfer-state
        """
        params = {
            "transId": trans_id,
            "clientId": client_id,
            "type": type_,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/transfer-state",
            params=params,
            signed=True,
        )

    async def get_asset_bills(
        self,
        ccy: str | None = None,
        type_: str | None = None,
        third_party_type: str | None = None,
        client_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории операций финансового аккаунта.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-asset-bills-details
        """
        params = {
            "ccy": ccy,
            "type": type_,
            "thirdPartyType": third_party_type,
            "clientId": client_id,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/bills",
            params=params,
            signed=True,
        )

    async def get_asset_bills_history(
        self,
        ccy: str | None = None,
        type_: str | None = None,
        third_party_type: str | None = None,
        client_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        paging_type: str | None = None,
    ) -> dict:
        """Получение архива истории операций финансового аккаунта.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-asset-bills-history
        """
        params = {
            "ccy": ccy,
            "type": type_,
            "thirdPartyType": third_party_type,
            "clientId": client_id,
            "after": after,
            "before": before,
            "limit": limit,
            "pagingType": paging_type,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/bills-history",
            params=params,
            signed=True,
        )

    async def get_deposit_address(self, ccy: str) -> dict:
        """Получение адреса депозита.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-address
        """
        params = {
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/deposit-address",
            params=params,
            signed=True,
        )

    async def get_deposit_history(
        self,
        ccy: str | None = None,
        dep_id: str | None = None,
        from_wd_id: str | None = None,
        tx_id: str | None = None,
        type_: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории депозитов.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-history
        """
        params = {
            "ccy": ccy,
            "depId": dep_id,
            "fromWdId": from_wd_id,
            "txId": tx_id,
            "type": type_,
            "state": state,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/deposit-history",
            params=params,
            signed=True,
        )

    async def withdrawal(
        self,
        ccy: str,
        amt: NumberLike,
        dest: str,
        to_addr: str,
        to_addr_type: str | None = None,
        chain: str | None = None,
        area_code: str | None = None,
        rcvr_info: dict[str, Any] | None = None,
        client_id: str | None = None,
    ) -> dict:
        """Вывод средств.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-withdrawal
        """
        data = {
            "ccy": ccy,
            "amt": amt,
            "dest": dest,
            "toAddr": to_addr,
            "toAddrType": to_addr_type,
            "chain": chain,
            "areaCode": area_code,
            "rcvrInfo": rcvr_info,
            "clientId": client_id,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/withdrawal",
            data=data,
            signed=True,
        )

    async def cancel_withdrawal(self, wd_id: str) -> dict:
        """Отмена вывода средств.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-cancel-withdrawal
        """
        data = {
            "wdId": wd_id,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/cancel-withdrawal",
            data=data,
            signed=True,
        )

    async def get_withdrawal_history(
        self,
        ccy: str | None = None,
        wd_id: str | None = None,
        client_id: str | None = None,
        tx_id: str | None = None,
        type_: str | None = None,
        state: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории выводов.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history
        """
        params = {
            "ccy": ccy,
            "wdId": wd_id,
            "clientId": client_id,
            "txId": tx_id,
            "type": type_,
            "state": state,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/withdrawal-history",
            params=params,
            signed=True,
        )

    async def get_deposit_withdraw_status(
        self,
        wd_id: str | None = None,
        tx_id: str | None = None,
        ccy: str | None = None,
        to: str | None = None,
        chain: str | None = None,
    ) -> dict:
        """Получение статуса депозита или вывода.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-deposit-withdraw-status
        """
        params = {
            "wdId": wd_id,
            "txId": tx_id,
            "ccy": ccy,
            "to": to,
            "chain": chain,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/deposit-withdraw-status",
            params=params,
            signed=True,
        )

    async def get_exchange_list(self) -> dict:
        """Получение списка бирж (для travel rule).

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-exchange-list-public
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/exchange-list",
        )

    async def apply_monthly_statement(self, month: str | None = None) -> dict:
        """Запрос месячной выписки за последний год.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-apply-for-monthly-statement-last-year
        """
        data = {
            "month": month,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/monthly-statement",
            data=data,
            signed=True,
        )

    async def get_monthly_statement(self, month: str) -> dict:
        """Получение месячной выписки за последний год.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-monthly-statement-last-year
        """
        params = {
            "month": month,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/monthly-statement",
            params=params,
            signed=True,
        )

    async def get_convert_currencies(self) -> dict:
        """Получение валют для конвертации.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-convert-currencies
        """
        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/convert/currencies",
            signed=True,
        )

    async def get_convert_currency_pair(self, from_ccy: str, to_ccy: str) -> dict:
        """Получение пары для конвертации.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-convert-currency-pair
        """
        params = {
            "fromCcy": from_ccy,
            "toCcy": to_ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/convert/currency-pair",
            params=params,
            signed=True,
        )

    async def convert_estimate_quote(
        self,
        base_ccy: str,
        quote_ccy: str,
        side: str,
        rfq_sz: NumberLike,
        rfq_sz_ccy: str,
        cl_q_req_id: str | None = None,
        tag: str | None = None,
        convert_mode: str | None = None,
    ) -> dict:
        """Получение котировки для конвертации.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-estimate-quote
        """
        data = {
            "baseCcy": base_ccy,
            "quoteCcy": quote_ccy,
            "side": side,
            "rfqSz": rfq_sz,
            "rfqSzCcy": rfq_sz_ccy,
            "clQReqId": cl_q_req_id,
            "tag": tag,
            "convertMode": convert_mode,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/convert/estimate-quote",
            data=data,
            signed=True,
        )

    async def convert_trade(
        self,
        quote_id: str,
        base_ccy: str,
        quote_ccy: str,
        side: str,
        sz: NumberLike,
        sz_ccy: str,
        cl_t_req_id: str | None = None,
        tag: str | None = None,
        convert_mode: str | None = None,
    ) -> dict:
        """Конвертация по котировке.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-convert-trade
        """
        data = {
            "quoteId": quote_id,
            "baseCcy": base_ccy,
            "quoteCcy": quote_ccy,
            "side": side,
            "sz": sz,
            "szCcy": sz_ccy,
            "clTReqId": cl_t_req_id,
            "tag": tag,
            "convertMode": convert_mode,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/convert/trade",
            data=data,
            signed=True,
        )

    async def get_convert_history(
        self,
        cl_t_req_id: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
        tag: str | None = None,
    ) -> dict:
        """Получение истории конвертаций.

        https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-convert-history
        """
        params = {
            "clTReqId": cl_t_req_id,
            "after": after,
            "before": before,
            "limit": limit,
            "tag": tag,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/convert/history",
            params=params,
            signed=True,
        )

    async def get_subaccount_funding_balance(self, sub_acct: str, ccy: str | None = None) -> dict:
        """Получение финансового баланса субаккаунта.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-sub-account-funding-balance
        """
        params = {
            "subAcct": sub_acct,
            "ccy": ccy,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/subaccount/balances",
            params=params,
            signed=True,
        )

    async def get_subaccount_transfer_history(
        self,
        ccy: str | None = None,
        type_: str | None = None,
        sub_acct: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории переводов субаккаунтов.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-history-of-sub-account-transfer
        """
        params = {
            "ccy": ccy,
            "type": type_,
            "subAcct": sub_acct,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/subaccount/bills",
            params=params,
            signed=True,
        )

    async def get_managed_subaccount_transfer_history(
        self,
        ccy: str | None = None,
        type_: str | None = None,
        sub_acct: str | None = None,
        sub_uid: str | None = None,
        after: str | None = None,
        before: str | None = None,
        limit: str | None = None,
    ) -> dict:
        """Получение истории переводов управляемых субаккаунтов.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-get-history-of-managed-sub-account-transfer
        """
        params = {
            "ccy": ccy,
            "type": type_,
            "subAcct": sub_acct,
            "subUid": sub_uid,
            "after": after,
            "before": before,
            "limit": limit,
        }

        return await self._make_request(
            "GET",
            endpoint="/api/v5/asset/subaccount/managed-subaccount-bills",
            params=params,
            signed=True,
        )

    async def subaccount_transfer(
        self,
        ccy: str,
        amt: NumberLike,
        from_: str,
        to: str,
        from_sub_account: str,
        to_sub_account: str,
        loan_trans: bool | None = None,
        omit_pos_risk: str | None = None,
    ) -> dict:
        """Перевод средств между субаккаунтами.

        https://www.okx.com/docs-v5/en/#sub-account-rest-api-master-accounts-manage-the-transfers-between-sub-accounts
        """
        data = {
            "ccy": ccy,
            "amt": amt,
            "from": from_,
            "to": to,
            "fromSubAccount": from_sub_account,
            "toSubAccount": to_sub_account,
            "loanTrans": loan_trans,
            "omitPosRisk": omit_pos_risk,
        }

        return await self._make_request(
            "POST",
            endpoint="/api/v5/asset/subaccount/transfer",
            data=data,
            signed=True,
        )
