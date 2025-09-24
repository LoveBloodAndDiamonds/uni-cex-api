__all__ = ["Client"]

from typing import Any

from unicex._base.asyncio import BaseClient
from unicex.types import RequestMethod

from .._mixins import ClientMixin


class Client(ClientMixin, BaseClient):
    """Клиент для работы с Bitget API."""

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Bitget API.

        Если `signed=True`:
            - генерирует `timestamp` и `signature`;
            - добавляет авторизационные заголовки (`ACCESS-KEY`, `ACCESS-PASSPHRASE`, `ACCESS-TIMESTAMP`, `ACCESS-SIGN`).

        Если `signed=False`:
            - выполняет публичный запрос без подписи.

        Параметры:
            method (`RequestMethod`): HTTP-метод (`"GET"`, `"POST"`, и т. п.).
            endpoint (`str`): Относительный путь эндпоинта (например, `"/api/spot/v1/market/tickers"`).
            signed (`bool`): Приватный запрос (с подписью) или публичный. По умолчанию `False`.
            params (`dict[str, Any] | None`): Query-параметры запроса.
            data (`dict[str, Any] | None`): Тело запроса для `POST/PUT`.

        Возвращает:
            `Any`: Ответ API в формате JSON (`dict` или `list`), как вернул сервер.
        """
        url, params, data, headers = self._prepare_request_params(
            method=method,
            endpoint=endpoint,
            signed=signed,
            params=params,
            body=data,
        )
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    # ========== COMMON PUBLIC ==========

    async def server_time(self) -> dict:
        """Получение серверного времени.

        https://www.bitget.com/api-doc/common/intro
        """
        return await self._make_request("GET", "/api/v2/public/time")

    # ========== PUBLIC SPOT ENDPOINTS ==========

    # ========== PRIVATE SPOT ENDPOINTS ==========

    # ========== PUBLIC FUTURES ENDPOINTS ==========

    # ========== PRIVATE FUTURES ENDPOINTS ==========
