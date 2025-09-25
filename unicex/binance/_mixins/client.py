__all__ = ["ClientMixin"]

import time
from typing import Any

from unicex.exceptions import NotAuthorized
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature


class ClientMixin:
    """Миксин для клиентов Binance API. Содержит общий функционал для работы с REST API Binance."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""

    _RECV_WINDOW: int = 5000
    """Стандартный интервал времени для получения ответа от сервера."""

    def _get_headers(self) -> dict:
        """Возвращает заголовки для запросов к Binance API."""
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
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Подготавливает payload и заголовки для запроса.

        Если signed=True:
            - добавляет подпись и все обязательные параметры в заголовки

        Если signed=False:
            - возвращает только отфильтрованные params/data.

        Параметры:
            signed (`bool`): Нужно ли подписывать запрос.
            params (`dict | None`): Параметры для query string.
            data (`dict | None`): Параметры для тела запроса.

        Возвращает:
            tuple:
                - payload (`dict`): Параметры/тело запроса с подписью (если нужно).
                - headers (`dict | None`): Заголовки для запроса или None.
        """
        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}
        data = filter_params(data) if data else {}

        if not signed:
            return {"params": params, "data": data}, None

        if not self._api_key or not self._api_secret:  # type: ignore[attr-defined]
            raise NotAuthorized("Api key is required to private endpoints")

        # Объединяем все параметры в payload
        payload = {**params, **data}
        payload["timestamp"] = int(time.time() * 1000)
        payload["recvWindow"] = self._RECV_WINDOW

        # Генерируем подпись
        query_string = dict_to_query_string(payload)
        payload["signature"] = generate_hmac_sha256_signature(
            self._api_secret,  # type: ignore[attr-defined]
            query_string,
            "hex",
        )

        headers = self._get_headers()
        return payload, headers
