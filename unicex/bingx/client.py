__all__ = ["Client"]


from typing import Any

from unicex._base import BaseClient
from unicex.types import RequestMethod
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с BingX API."""

    _BASE_URL: str = "https://open-api.bingx.com"
    """Базовый URL для REST API BingX."""

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Выполняет HTTP-запрос к эндпоинтам BingX API.

        Параметры:
            method (str): HTTP метод запроса ("GET", "POST", "DELETE" и т.д.).
            endpoint (str): URL эндпоинта Kucoin API.
            params (dict | None): Параметры запроса.

        Возвращает:
            dict: Ответ в формате JSON.
        """
        # Составляем URL для запроса
        url = self._BASE_URL + endpoint

        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}

        # Выполняем запрос
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
        )
