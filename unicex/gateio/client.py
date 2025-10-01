__all__ = ["Client"]

import hashlib
import hmac
import json
import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params


class Client(BaseClient):
    """Клиент для работы с Gateio API."""

    _BASE_URL: str = "https://api.gateio.ws"
    """Базовый URL для REST API Gate.io."""

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
            raise NotAuthorized("Api key is required to private endpoints")

        payload_string = json.dumps(data, separators=(",", ":")) if data else ""
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

    async def server_time(self) -> dict:
        """Получение серверного времени."""
        return await self._make_request("GET", "/api/v4/spot/time")
