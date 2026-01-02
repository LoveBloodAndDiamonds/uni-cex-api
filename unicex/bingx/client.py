__all__ = ["Client"]


from typing import Any

from unicex._base import BaseClient
from unicex.types import RequestMethod
from unicex.utils import filter_params, get_timestamp


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

        # Добавляем timestap в параметры, если он не указан
        if params and "timestamp" in params and not params["timestamp"]:
            params["timestamp"] = get_timestamp()

        # Фильтруем параметры от None значений
        params = filter_params(params) if params else {}

        # Выполняем запрос
        return await super()._make_request(
            method=method,
            url=url,
            params=params,
        )

    async def futures_contracts(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка USDT-M бессрочных фьючерсных контрактов.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/USDT-M%20Perp%20Futures%20symbols
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/contracts", params=params)

    async def futures_order_book(
        self,
        symbol: str,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение стакана ордеров.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Order%20Book
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/depth", params=params)

    async def futures_trades(
        self,
        symbol: str,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка последних сделок.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Recent%20Trades%20List
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/trades", params=params)

    async def futures_mark_price(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение цены маркировки и ставки финансирования.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Mark%20Price%20and%20Funding%20Rate
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/premiumIndex", params=params)

    async def futures_funding_rate_history(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение истории ставок финансирования.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Get%20Funding%20Rate%20History
        """
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/fundingRate", params=params)

    async def futures_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение свечей.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Kline%2FCandlestick%20Data
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v3/quote/klines", params=params)

    async def open_interest(
        self,
        symbol: str,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение статистики открытого интереса.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Open%20Interest%20Statistics
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/openInterest", params=params)

    async def futures_ticker_24hr(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение 24-часовой статистики тикера.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/24hr%20Ticker%20Price%20Change%20Statistics
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/ticker", params=params)

    async def futures_historical_trades(
        self,
        symbol: str | None = None,
        from_id: int | None = None,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение исторических сделок.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Query%20historical%20transaction%20orders
        """
        params = {
            "fromId": from_id,
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request(
            "GET",
            "/openApi/swap/v1/market/historicalTrades",
            params=params,
        )

    async def futures_book_ticker(
        self,
        symbol: str,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение лучшего бид/аск по символу.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Symbol%20Order%20Book%20Ticker
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v2/quote/bookTicker", params=params)

    async def futures_mark_price_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение свечей цены маркировки.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Mark%20Price%20Kline-Candlestick%20Data
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request(
            "GET",
            "/openApi/swap/v1/market/markPriceKlines",
            params=params,
        )

    async def futures_ticker_price(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение последней цены тикера.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Symbol%20Price%20Ticker
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v1/ticker/price", params=params)

    async def futures_trading_rules(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение торговых правил.

        https://bingx-api.github.io/docs-v3/#/en/Swap/Market%20Data/Trading%20Rules
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/swap/v1/tradingRules", params=params)

    async def symbols(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка спотовых торговых пар.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Spot%20trading%20symbols
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v1/common/symbols", params=params)

    async def trades(
        self,
        symbol: str,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение списка последних сделок.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Recent%20Trades%20List
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v1/market/trades", params=params)

    async def order_book(
        self,
        symbol: str,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение стакана ордеров.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Order%20Book
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v1/market/depth", params=params)

    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение свечей.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Kline-Candlestick%20Data
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v2/market/kline", params=params)

    async def ticker_24hr(
        self,
        symbol: str | None = None,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение 24-часовой статистики тикера.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/24hr%20Ticker%20Price%20Change%20Statistics
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v1/ticker/24hr", params=params)

    async def order_book_agg(
        self,
        symbol: str,
        depth: int,
        type_: str,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение агрегированного стакана ордеров.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Order%20Book%20aggregation
        """
        params = {
            "symbol": symbol,
            "depth": depth,
            "type": type_,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v2/market/depth", params=params)

    async def ticker_price(
        self,
        symbol: str,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение последней цены тикера.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Price%20Ticker
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v2/ticker/price", params=params)

    async def book_ticker(
        self,
        symbol: str,
        timestamp: int | None = None,
        recv_window: int | None = None,
    ) -> dict[str, Any]:
        """Получение лучшего бид/аск по символу.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Symbol%20Order%20Book%20Ticker
        """
        params = {
            "symbol": symbol,
            "timestamp": timestamp,
            "recvWindow": recv_window,
        }

        return await self._make_request("GET", "/openApi/spot/v1/ticker/bookTicker", params=params)

    async def historical_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Получение исторических свечей.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Historical%20K-line
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", "/openApi/market/his/v1/kline", params=params)

    async def historical_trades(
        self,
        symbol: str,
        limit: int | None = None,
        from_id: str | None = None,
    ) -> dict[str, Any]:
        """Получение исторических сделок.

        https://bingx-api.github.io/docs-v3/#/en/Spot/Market%20Data/Old%20Trade%20Lookup
        """
        params = {
            "symbol": symbol,
            "limit": limit,
            "fromId": from_id,
        }

        return await self._make_request("GET", "/openApi/market/his/v1/trade", params=params)
