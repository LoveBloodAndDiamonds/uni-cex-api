__all__ = ["Client"]

import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Bitrue API."""

    _BASE_URL: str = "https://www.bitrue.com"
    """Базовый URL для REST API Bitrue."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self) -> dict[str, str]:
        """Возвращает заголовки для авторизованных запросов."""
        headers = {"Accept": "application/json"}
        if self._api_key:  # type: ignore[attr-defined]
            headers["X-MBX-APIKEY"] = self._api_key  # type: ignore[attr-defined]
        return headers

    def _prepare_payload(
        self,
        *,
        signed: bool,
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> tuple[dict[str, Any], dict[str, str] | None]:
        """Подготавливает payload и заголовки для запроса."""
        params = filter_params(params) if params else {}
        data = filter_params(data) if data else {}

        if not signed:
            return {"params": params, "data": data}, None

        if not self.is_authorized():
            raise NotAuthorized("Api key is required to private endpoints")

        payload = {**params, **data}
        payload["timestamp"] = int(time.time() * 1000)
        payload["recvWindow"] = self._RECV_WINDOW

        query_string = dict_to_query_string(payload)
        payload["signature"] = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
        )

        headers = self._get_headers()
        return payload, headers

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к Bitrue API."""
        url = f"{self._BASE_URL}{endpoint}"
        has_body = bool(data)
        payload, headers = self._prepare_payload(signed=signed, params=params, data=data)

        if not signed:
            return await super()._make_request(
                method=method,
                url=url,
                params=payload["params"],
                data=payload["data"],
                headers=headers,
            )

        if has_body:
            return await super()._make_request(
                method=method,
                url=url,
                data=payload,
                headers=headers,
            )
        return await super()._make_request(
            method=method,
            url=url,
            params=payload,
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
            endpoint (`str`): Относительный путь эндпоинта Bitrue API.
            params (`dict | None`): Query-параметры запроса.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ Bitrue API.
        """
        return await self._make_request(
            method=method,
            endpoint=endpoint,
            params=params,
            data=data,
            signed=signed,
        )

    async def server_time(self) -> dict:
        """Получение серверного времени.

        https://www.bitrue.com/api_docs_includes_file/spot/index.html#general-endpoints
        """
        return await self._make_request("GET", "/api/v1/time")
