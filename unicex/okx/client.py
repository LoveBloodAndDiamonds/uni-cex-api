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

    # topic: Order Book Trading
    # sub-topic: Market Data

    async def tickers(
        self,
        inst_type: Literal["SPOT", "SWAP", "FUTURES", "OPTION"],
        inst_family: Literal["FUTURES", "SWAP", "OPTION"] | None = None,
    ) -> dict:
        """Получение информации о тикерах.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-tickers

        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
        }
        return await self._make_request("GET", endpoint="/api/v5/market/tickers", params=params)

    async def candles(
        self,
        inst_id: str,
        bar: str | None = None,
        after: int | None = None,
        before: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Получение свечей.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
        """
        params = {
            "instId": inst_id,
            "bar": bar,
            "after": after,
            "before": before,
            "limit": limit,
        }
        return await self._make_request("GET", endpoint="/api/v5/market/candles", params=params)

    # topic: Public Data
    # sub-topic: REST API

    async def get_funding_rate(self, inst_id: str) -> dict:
        """Получение информации о ставке финансирования.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate
        """
        params = {
            "instId": inst_id,
        }
        return await self._make_request(
            "GET", endpoint="/api/v5/public/funding-rate", params=params
        )

    async def get_open_interest(
        self,
        inst_type: Literal["SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
        inst_id: str | None = None,
    ) -> dict:
        """Получение информации по открытому интересу.

        https://www.okx.com/docs-v5/en/#public-data-rest-api-get-open-interest
        """
        params = {
            "instType": inst_type,
            "instFamily": inst_family,
            "instId": inst_id,
        }
        return await self._make_request(
            "GET", endpoint="/api/v5/public/open-interest", params=params
        )
