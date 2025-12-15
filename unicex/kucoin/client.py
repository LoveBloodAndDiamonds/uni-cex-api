__all__ = ["Client"]


from typing import Any, Literal

from unicex._base import BaseClient


class Client(BaseClient):
    """Клиент для работы с Kucoin API."""

    _BASE_URL: str = "https://api.kucoin.com"
    """Базовый URL для запросов."""

    async def symbol(
        self,
        trade_type: Literal["SPOT", "FUTURES", "ISOLATED", "CROSS"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение символов и информации о них.

        https://www.kucoin.com/docs-new/rest/ua/get-symbol
        """
        url = self._BASE_URL + "/api/ua/v1/market/instrument"
        params = {"tradeType": trade_type}
        if symbol:
            params["symbol"] = symbol

        return await self._make_request("GET", url, params=params)

    async def ticker(
        self,
        trade_type: Literal["SPOT", "FUTURES"],
        symbol: str | None = None,
    ) -> dict[str, Any]:
        """Получение тикеров и информации о них.

        https://www.kucoin.com/docs-new/rest/ua/get-ticker
        """
        url = self._BASE_URL + "/api/ua/v1/market/ticker"
        params = {"tradeType": trade_type}
        if symbol:
            params["symbol"] = symbol

        return await self._make_request("GET", url, params=params)

    async def open_interest(self) -> dict[str, Any]:
        """Получение открытого интереса.

        https://www.kucoin.com/docs-new/3476287e0
        """
        url = self._BASE_URL + "/api/ua/v1/market/open-interest"

        return await self._make_request("GET", url)
