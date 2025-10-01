__all__ = ["Client"]


import time
from typing import Any

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с MEXC Spot API."""

    _BASE_URL: str = "https://api.mexc.com"
    """Базовый URL для REST API MEXC."""

    _RECV_WINDOW: str = "5000"
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, signed: bool = False) -> dict:
        """Формирует заголовки запроса."""
        headers = {"Content-Type": "application/json"}
        if signed:
            if not self._api_key:
                raise NotAuthorized("API key is required for private endpoints.")
            headers["X-MEXC-APIKEY"] = self._api_key
        return headers

    def _generate_signature(self, payload: dict) -> str:
        """Генерирует подпись на основе данных запроса."""
        if not self._api_secret:
            raise NotAuthorized("API secret is required for private endpoints.")

        query_string = dict_to_query_string(payload)
        return generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
            "hex",
        )

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Mexc API.

        Если signed=True, формируется подпись для приватных endpoint'ов:
            - Если переданы params — подпись добавляется в параметры запроса.
            - Если передан data — подпись добавляется в тело запроса.

        Если signed=False, запрос отправляется как публичный.

        Параметры:
            method (`str`): HTTP метод ("GET", "POST", "DELETE" и т.д.).
            endpoint (`str`): URL эндпоинта Mexc API.
            params (`dict | None`): Query-параметры.
            signed (`bool`): Нужно ли подписывать запрос.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        # Формируем полный URL для запроса
        url = self._BASE_URL + endpoint

        # Фильтруем параметры
        payload = filter_params(params) if params else {}

        # Генериуем подпись, если запрос авторизованый
        if signed:
            # Генерируем подпись
            payload["timestamp"] = int(time.time() * 1000)
            payload["recvWindow"] = self._RECV_WINDOW
            payload["signature"] = self._generate_signature(payload)

        # Формируем заголовки запроса
        headers = self._get_headers(signed=signed)

        # GET → query params, POST → body
        # if method == "POST":
        #     return await super()._make_request(
        #         method=method,
        #         url=url,
        #         data=payload,
        #         headers=headers,
        #     )
        # else:
        return await super()._make_request(
            method=method,
            url=url,
            params=payload,
            headers=headers,
        )

    async def request(
        self, method: RequestMethod, endpoint: str, params: dict, signed: bool
    ) -> dict:
        """Специальный метод для выполнения запросов на эндпоинты, которые не обернуты в клиенте.

        Параметры:
            method (RequestMethod): Метод запроса (GET, POST, PUT, DELETE).
            endpoint (str): URL эндпоинта.
            params (dict): Параметры запроса.
            signed (bool): Флаг, указывающий, требуется ли подпись запроса.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        return await self._make_request(
            method=method, endpoint=endpoint, params=params, signed=signed
        )

    # topic: Market
