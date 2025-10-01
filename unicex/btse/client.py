__all__ = ["Client"]

import hashlib
import hmac
import json
import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с BTSE API."""

    _BASE_URL: str = "https://api.btse.com/spot"
    """Базовый URL для REST API BTSE."""

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

        if not self.is_authorized():
            raise NotAuthorized("Api key is required to private endpoints")

        request_nonce = str(int(time.time() * 1000))
        body_str = (
            json.dumps(data, separators=(",", ":"), sort_keys=True)
            if data and method == "POST"
            else ""
        )
        payload = f"{endpoint}{request_nonce}{body_str}"
        signature = hmac.new(
            self._api_secret.encode("utf-8"),  # type: ignore[attr-defined]
            payload.encode("utf-8"),
            hashlib.sha384,
        ).hexdigest()

        headers.update(
            {
                "request-api": self._api_key,  # type: ignore[attr-defined]
                "request-nonce": request_nonce,
                "request-sign": signature,
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
        """Выполняет HTTP-запрос к BTSE API."""
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
            endpoint (`str`): Относительный путь эндпоинта BTSE API.
            params (`dict | None`): Query-параметры запроса.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ BTSE API.
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
        return await self._make_request("GET", "/api/v3.2/time")
