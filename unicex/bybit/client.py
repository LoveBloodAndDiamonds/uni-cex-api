__all__ = ["Client"]


import json
import time
from typing import Any, Literal

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import RequestMethod
from unicex.utils import filter_params, generate_hmac_sha256_signature


class Client(BaseClient):
    """Клиент для работы с Bybit API."""

    _BASE_URL: str = "https://api.bybit.com"
    """Базовый URL для REST API Bybit."""

    _RECV_WINDOW: str = "5000"
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self, timestamp: str, signature: str | None = None) -> dict:
        """Возвращает заголовки для запросов к Bybit API.

        Параметры:
            timestamp (str): Временная метка запроса в миллисекундах.
            signature (str | None): Подпись запроса, если запрос авторизированый.
        """
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if signature:
            headers["X-BAPI-API-KEY"] = self._api_key  # type: ignore
            headers["X-BAPI-SIGN-TYPE"] = "2"
            headers["X-BAPI-SIGN"] = signature
            headers["X-BAPI-RECV-WINDOW"] = self._RECV_WINDOW
            headers["X-BAPI-TIMESTAMP"] = timestamp
        return headers

    def _generate_signature(self, timestamp: str, payload: dict) -> str:
        """Генерация подписи.

        Источник: https://github.com/bybit-exchange/api-usage-examples/blob/master/V5_demo/api_demo/Encryption_HMAC.py
        """
        # Проверяем наличие апи ключей для подписи запроса
        if not self._api_key or not self._api_secret:
            raise NotAuthorized("API key and secret are required to private endpoints.")

        dumped_payload = json.dumps(payload)
        prepared_query_string = timestamp + self._api_key + self._RECV_WINDOW + dumped_payload
        return generate_hmac_sha256_signature(self._api_secret, prepared_query_string)

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bybit API с поддержкой подписи.

        Если signed=True, формируется подпись для приватных endpoint'ов.
        Если signed=False, запрос отправляется как обычный публичный, через
        базовый _make_request без обработки подписи.

        Параметры:
            method (str): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            url (str): Полный URL эндпоинта Bybit API.
            params (dict | None): Параметры запроса. Передаются в body, если запрос типа "POST", иначе в query_params
            signed (bool): Нужно ли подписывать запрос.

        Возвращает:
            dict: Ответ в формате JSON.
        """
        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}

        # Генерируем временную метку
        timestamp = str(int(time.time() * 1000))

        # Проверяем нужно ли подписывать запрос
        if not signed:
            headers = self._get_headers(timestamp)
            return super()._make_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
            )

        # Формируем payload
        payload = params

        # Генерируем строку для подписи
        signature = self._generate_signature(timestamp, payload)

        # Генерируем заголовки (вкл. в себя подпись и апи ключ)
        headers = self._get_headers(timestamp, signature)

        if method == "POST":  # Отправляем параметры в тело запроса
            return await super()._make_request(
                method=method,
                url=url,
                data=payload,
                headers=headers,
            )
        else:  # Иначе параметры добавляем к query string
            return await super()._make_request(
                method=method,
                url=url,
                params=payload,
                headers=headers,
            )

    # topic: market

    async def ping(self) -> dict:
        """Проверка подключения к REST API.

        https://bybit-exchange.github.io/docs/v5/market/time
        """
        url = self._BASE_URL + "/v5/market/time"
        return await self._make_request("GET", url)

    async def klines(
        self,
        symbol: str,
        interval: str,
        category: Literal["spot", "linear", "inverse"],
        start: int | None = None,
        end: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Исторические свечи.

        https://bybit-exchange.github.io/docs/v5/market/kline
        """
        url = self._BASE_URL + "/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "start": start,
            "end": end,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)
