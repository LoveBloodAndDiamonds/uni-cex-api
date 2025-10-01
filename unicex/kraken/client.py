__all__ = ["Client"]

import asyncio
import base64
import hashlib
import hmac
import time
from typing import Any

import aiohttp

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params


class Client(BaseClient):
    """Клиент для работы с Kraken API."""

    _BASE_URL: str = "https://api.kraken.com"
    """Базовый URL для REST API Kraken."""

    def _prepare_request(
        self,
        *,
        method: RequestMethod,
        endpoint: str,
        signed: bool,
        params: dict[str, Any] | None,
        data: dict[str, Any] | None,
    ) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None, dict[str, str], str | None]:
        """Формирует параметры и заголовки для HTTP-запроса."""
        params = filter_params(params) if params else None
        data = filter_params(data) if data else None
        url = f"{self._BASE_URL}{endpoint}"

        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if not signed:
            return url, params, data, headers, None

        if not self.is_authorized():
            raise NotAuthorized("Api key is required to private endpoints")

        nonce = str(int(time.time() * 1000))
        body = data.copy() if data else {}
        body.setdefault("nonce", nonce)

        postdata = dict_to_query_string(body)
        message = endpoint.encode() + hashlib.sha256((nonce + postdata).encode()).digest()
        signature = hmac.new(
            base64.b64decode(self._api_secret),  # type: ignore[attr-defined]
            message,
            hashlib.sha512,
        ).digest()
        headers.update(
            {
                "API-Key": self._api_key,  # type: ignore[attr-defined]
                "API-Sign": base64.b64encode(signature).decode(),
            }
        )
        return url, params, body, headers, postdata

    async def _make_form_request(
        self,
        *,
        method: RequestMethod,
        url: str,
        params: dict[str, Any] | None,
        headers: dict[str, str],
        payload: str,
    ) -> Any:
        """Выполняет запрос с телом в формате x-www-form-urlencoded."""
        errors: list[Exception] = []
        for attempt in range(1, self._max_retries + 1):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=payload,
                    headers=headers,
                    proxy=next(self._proxies_cycle) if self._proxies_cycle else None,
                    timeout=aiohttp.ClientTimeout(total=self._timeout) if self._timeout else None,
                ) as response:
                    return await self._handle_response(response=response)
            except (aiohttp.ServerTimeoutError, aiohttp.ConnectionTimeoutError) as error:
                errors.append(error)
                self._logger.debug(
                    f"Attempt {attempt}/{self._max_retries} failed: {type(error)} -> {error}"
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay)
        raise ConnectionError(
            f"Connection error after {self._max_retries} request on {method} {url}. Errors: {errors}"
        ) from errors[-1]

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к Kraken API."""
        url, params, data, headers, payload = self._prepare_request(
            method=method,
            endpoint=endpoint,
            signed=signed,
            params=params,
            data=data,
        )
        if payload is not None and method in {"POST", "PUT"}:
            return await self._make_form_request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                payload=payload,
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
            endpoint (`str`): Относительный путь эндпоинта Kraken API.
            params (`dict | None`): Query-параметры запроса.
            data (`dict | None`): Тело запроса.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ Kraken API.
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
        return await self._make_request("GET", "/0/public/Time")
