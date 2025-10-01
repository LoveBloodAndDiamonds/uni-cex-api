__all__ = ["Client"]

import datetime
import json
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с OKX API."""

    _BASE_URL: str = "https://www.okx.com"
    """Базовый URL для REST API OKX."""

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
        if self._api_key:  # type: ignore[attr-defined]
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

        headers = None
        if signed:
            if not self._api_key or not self._api_secret or not self._api_passphrase:
                raise NotAuthorized(
                    "API key, secret, and passphrase are required for private endpoints"
                )

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

    # topic: public

    async def get_server_time(self) -> dict:
        """Получение серверного времени.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-system-time
        """
        return await self._make_request("GET", "/api/v5/public/time")

    # topic: trading

    async def create_order(
        self,
        inst_id: str,
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
        ],
        sz: str,
        px: str | None = None,
        cl_ord_id: str | None = None,
        td_mode: str = "cash",
    ) -> dict:
        """Создание ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-place-order
        """
        body = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
            "px": px,
            "clOrdId": cl_ord_id,
        }

        return await self._make_request("POST", "/api/v5/trade/order", signed=True, data=body)

    async def cancel_order(
        self, inst_id: str, ord_id: str | None = None, cl_ord_id: str | None = None
    ) -> dict:
        """Отмена ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-post-cancel-order
        """
        body = {"instId": inst_id, "ordId": ord_id, "clOrdId": cl_ord_id}

        return await self._make_request(
            "POST", "/api/v5/trade/cancel-order", signed=True, data=body
        )

    async def get_order_status(
        self, inst_id: str, ord_id: str | None = None, cl_ord_id: str | None = None
    ) -> dict:
        """Получение статуса ордера.

        https://www.okx.com/docs-v5/en/#order-book-trading-trade-get-order-details
        """
        params = {"instId": inst_id, "ordId": ord_id, "clOrdId": cl_ord_id}

        return await self._make_request("GET", "/api/v5/trade/order", signed=True, params=params)

    # topic: account

    async def get_balances(self, ccy: str | None = None) -> dict:
        """Получение балансов аккаунта.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-balance
        """
        params = {"ccy": ccy}

        return await self._make_request(
            "GET", "/api/v5/account/balance", signed=True, params=params
        )

    async def get_positions(self, inst_id: str | None = None, inst_type: str | None = None) -> dict:
        """Получение позиций.

        https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-positions
        """
        params = {"instId": inst_id, "instType": inst_type}

        return await self._make_request(
            "GET", "/api/v5/account/positions", signed=True, params=params
        )
