__all__ = ["ClientMixin"]

import json
import time
from typing import Any

from unicex.types import RequestMethod
from unicex.utils import (
    dict_to_query_string,
    filter_params,
    generate_hmac_sha256_signature,
    sort_params_by_alphabetical_order,
)


class ClientMixin:
    """Миксин для клиентов Bitget API. Содержит общий функционал для работы с REST API Bitget."""

    _BASE_URL: str = "https://api.bitget.com"
    """Базовый URL для REST API Bitget."""

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
            endpoint (`str`): Относительный путь эндпоинта (например `/api/spot/v1/account/assets`).
            params (`dict[str, Any] | None`): Query-параметры.
            body (`dict[str, Any] | None`): Тело запроса (для POST/PUT).

        Возвращает:
            tuple:
                - `timestamp (str)`: Временная метка в миллисекундах.
                - `signature (str)`: Подпись в формате base64.
        """
        timestamp = str(int(time.time() * 1000))

        path = f"{endpoint}?{dict_to_query_string(params)}" if params else endpoint
        body_str = json.dumps(body) if body else ""
        prehash = f"{timestamp}{method}{path}{body_str}"
        signature = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            prehash,
            "base64",
        )
        return timestamp, signature

    def _get_headers(self, timestamp: str, signature: str) -> dict[str, str]:
        """Возвращает заголовки для REST-запросов Bitget.

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
                    "ACCESS-KEY": self._api_key,  # type: ignore[attr-defined]
                    "ACCESS-PASSPHRASE": self._api_passphrase,  # type: ignore[attr-defined]
                    "ACCESS-TIMESTAMP": timestamp,
                    "ACCESS-SIGN": signature,
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

        # Предобрабатывает параметры запроса и сортирует их в соответствии с требованиями Bitget
        if params:
            params = filter_params(params)
            params = sort_params_by_alphabetical_order(params)

        headers = None
        if signed:
            timestamp, signature = self._sign_message(method, endpoint, params, body)
            headers = self._get_headers(timestamp, signature)
        return url, params, body, headers
