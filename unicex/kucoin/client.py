__all__ = ["Client"]

import json
import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Kucoin API."""

    _BASE_URL: str = "https://api.kucoin.com"
    """Базовый URL для REST API Kucoin."""

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
        data = filter_params(data) if data else None
        url = f"{self._BASE_URL}{endpoint}"

        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if not signed:
            return url, params, data, headers

        if not self._api_key or not self._api_secret or not self._api_passphrase:  # type: ignore[attr-defined]
            raise NotAuthorized("Api key is required to private endpoints")

        timestamp = str(int(time.time() * 1000))
        query_string = f"?{dict_to_query_string(params)}" if params else ""
        body_string = json.dumps(data, separators=(",", ":")) if data else ""
        sign_payload = f"{timestamp}{method.upper()}{endpoint}{query_string}{body_string}"
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            sign_payload,
            "base64",
        )

        headers.update(  # type: ignore[attr-defined]
            {
                "KC-API-KEY": self._api_key,
                "KC-API-SIGN": signature,
                "KC-API-TIMESTAMP": timestamp,
                "KC-API-PASSPHRASE": self._api_passphrase,
                "KC-API-KEY-VERSION": "2",
            }
        )
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
        """Выполняет HTTP-запрос к Kucoin API."""
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
            endpoint (`str`): Относительный путь эндпоинта Kucoin API.
            params (`dict | None`): Query-параметры запроса.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ Kucoin API.
        """
        return await self._make_request(
            method=method,
            endpoint=endpoint,
            params=params,
            data=data,
            signed=signed,
        )

    async def server_time(self) -> dict:
        """Получение серверного времени."""
        return await self._make_request("GET", "/api/v1/timestamp")
