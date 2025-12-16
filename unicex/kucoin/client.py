__all__ = ["Client"]


from typing import Any, Literal

from unicex._base import BaseClient
from unicex.types import RequestMethod
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с Kucoin API."""

    _BASE_URL: str = "https://api.kucoin.com"
    """Базовый URL для запросов."""

    async def _make_request(
        self,
        method: RequestMethod,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Выполняет HTTP-запрос к эндпоинтам Kucoin API.

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

    async def symbol(
        self,
        trade_type: Literal["SPOT", "FUTURES", "ISOLATED", "CROSS"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение символов и информации о них.

        https://www.kucoin.com/docs-new/rest/ua/get-symbol
        """
        params = {"tradeType": trade_type, "symbol": symbol}

        return await self._make_request("GET", "/api/ua/v1/market/instrument", params=params)

    async def ticker(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение тикеров и информации о них.

        https://www.kucoin.com/docs-new/rest/ua/get-ticker
        """
        params = {"tradeType": trade_type, "symbol": symbol}

        return await self._make_request("GET", "/api/ua/v1/market/ticker", params=params)

    async def open_interest(self) -> dict[str, Any]:
        """Получение открытого интереса.

        https://www.kucoin.com/docs-new/3476287e0
        """
        return await self._make_request("GET", "/api/ua/v1/market/open-interest")

    async def kline(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        symbol: str,
        interval: str,
        start_at: int | None = None,
        end_at: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка свечей.

        https://www.kucoin.com/docs-new/rest/ua/get-klines
        """
        params = {
            "tradeType": trade_type,
            "symbol": symbol,
            "interval": interval,
            "startAt": start_at,
            "endAt": end_at,
        }

        return await self._make_request("GET", "/api/ua/v1/market/kline", params=params)

    async def funding_rate_history(
        self,
        symbol: str,
        start_at: int,
        end_at: int,
    ) -> dict[str, Any]:
        """Получение истории ставок финансирования.

        https://www.kucoin.com/docs-new/rest/ua/get-history-funding-rate
        """
        params = {
            "symbol": symbol,
            "startAt": start_at,
            "endAt": end_at,
        }

        return await self._make_request(
            "GET",
            "/api/ua/v1/market/funding-rate-history",
            params=params,
        )
