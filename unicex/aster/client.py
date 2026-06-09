__all__ = ["Client"]

import json
import time
import urllib.parse
from typing import Any, Literal, Self

import aiohttp
from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount

from unicex._base import BaseClient
from unicex.exceptions import NotAuthorized
from unicex.types import LoggerLike, NumberLike, RequestMethod
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с Aster API.

    Использует авторизацию Aster V3: запросы подписываются приватным ключом
    API-кошелька (EIP-712), вместо устаревшей схемы API key + HMAC.
    """

    _BASE_FUTURES_URL: str = "https://fapi.asterdex.com"
    """Базовый URL для REST API Aster Futures."""

    _SIGN_CHAIN_ID: int = 1666
    """ChainId, используемый в EIP-712 домене при подписи запросов Aster V3."""

    _SIGN_DOMAIN_NAME: str = "AsterSignTransaction"
    """Имя EIP-712 домена для подписи запросов Aster V3."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        private_key: str | bytes | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            session (`aiohttp.ClientSession`): Сессия для выполнения HTTP‑запросов.
            private_key (`str | bytes | None`): Приватный ключ API-кошелька для подписи запросов.
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера, сек.
        """
        super().__init__(
            session=session,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

        # Кошелёк API формируется из приватного ключа. Его адрес используется как signer.
        self._wallet: LocalAccount | None = None
        self._signer: str | None = None
        if private_key is not None:
            # private_key может быть hex-строкой ("0x...") или байтами
            self._wallet = Account.from_key(private_key)
            self._signer = self._wallet.address

        # Последний выданный nonce (микросекунды) для гарантии строгого возрастания.
        self._last_nonce = 0

    @classmethod
    async def create(
        cls,
        private_key: str | bytes | None = None,
        session: aiohttp.ClientSession | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        """Создаёт инстанцию клиента.

        Параметры:
            private_key (`str | bytes | None`): Приватный ключ API-кошелька для подписи запросов.
            session (`aiohttp.ClientSession | None`): Сессия для HTTP‑запросов (если не передана, будет создана).
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимум повторов при ошибках запроса.
            retry_delay (`int | float`): Задержка между повторами, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси.
            timeout (`int`): Таймаут ответа сервера, сек.

        Возвращает:
            `Self`: Созданный экземпляр клиента.
        """
        return cls(
            session=session or aiohttp.ClientSession(),
            private_key=private_key,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    def is_authorized(self) -> bool:
        """Проверяет наличие приватного ключа для доступа к приватным эндпоинтам.

        Возвращает:
            `bool`: Признак наличия приватного ключа.
        """
        return self._wallet is not None

    def _get_headers(self, method: RequestMethod) -> dict[str, str]:
        """Возвращает заголовки для запросов к Aster API."""
        headers = {"Accept": "application/json"}
        if method in {"POST", "PUT", "DELETE"}:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    @staticmethod
    def _normalize_bool_params(params: dict[str, Any]) -> dict[str, Any]:
        """Преобразует bool-параметры в строки "true"/"false"."""
        return {
            k: ("true" if isinstance(v, bool) and v else "false" if isinstance(v, bool) else v)
            for k, v in params.items()
        }

    def _get_nonce(self) -> int:
        """Возвращает строго возрастающий nonce в микросекундах.

        Aster отклоняет повторно использованный nonce, поэтому при совпадении
        времени с предыдущим запросом значение инкрементируется.
        """
        nonce = int(time.time() * 1_000_000)
        if nonce <= self._last_nonce:
            nonce = self._last_nonce + 1
        self._last_nonce = nonce
        return nonce

    def _sign(self, msg: str) -> str:
        """Подписывает строку msg по схеме EIP-712 (Aster V3) приватным ключом.

        Параметры:
            msg (`str`): Строка (url-encoded параметры запроса), которую нужно подписать.

        Возвращает:
            `str`: Подпись в hex-формате с префиксом 0x.
        """
        # Структура EIP-712: домен AsterSignTransaction + тип Message с единственным полем msg.
        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Message": [{"name": "msg", "type": "string"}],
            },
            "primaryType": "Message",
            "domain": {
                "name": self._SIGN_DOMAIN_NAME,
                "version": "1",
                "chainId": self._SIGN_CHAIN_ID,
                "verifyingContract": "0x0000000000000000000000000000000000000000",
            },
            "message": {"msg": msg},
        }

        encoded = encode_typed_data(full_message=typed_data)
        signed = self._wallet.sign_message(encoded)  # type: ignore[union-attr]

        sig = signed.signature.hex()
        return sig if sig.startswith("0x") else f"0x{sig}"

    def _build_signed_query(self, params: dict[str, Any]) -> str:
        """Формирует подписанную query string для приватных эндпоинтов V3.

        Добавляет signer и nonce, кодирует параметры, подписывает строку и
        дописывает параметр signature.

        Параметры:
            params (`dict`): Бизнес-параметры запроса (уже отфильтрованные).

        Возвращает:
            `str`: Готовая query string вида "a=1&...&signer=...&nonce=...&signature=...".
        """
        if not self.is_authorized():
            raise NotAuthorized("Private key is required for private endpoints.")

        # signer и nonce обязательны для подписи Aster V3.
        params = {**params, "signer": self._signer, "nonce": str(self._get_nonce())}

        # Подпись формируется по той же строке, что и отправляется на сервер.
        msg = urllib.parse.urlencode(params)
        signature = self._sign(msg)

        return f"{msg}&signature={signature}"

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        signed: bool = False,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP-запрос к эндпоинтам Aster API.

        Если signed=True, параметры подписываются по схеме Aster V3 (EIP-712) и
        отправляются вместе с signer/nonce/signature в query string запроса.

        Если signed=False, запрос отправляется как публичный.

        Параметры:
            method (`str`): HTTP метод ("GET", "POST", "DELETE" и т.д.).
            url (`str`): Полный URL эндпоинта Aster API.
            signed (`bool`): Нужно ли подписывать запрос.
            params (`dict | None`): Query-параметры.

        Возвращает:
            `dict`: Ответ в формате JSON.
        """
        # Фильтруем None и нормализуем bool в строки "true"/"false".
        params = filter_params(params) if params else {}
        params = self._normalize_bool_params(params)
        headers = self._get_headers(method)

        if not signed:
            return await super()._make_request(
                method=method, url=url, params=params, headers=headers
            )

        # Приватный запрос: вшиваем подписанную query string прямо в URL,
        # чтобы отправляемая строка в точности совпадала с подписанной.
        query = self._build_signed_query(params)
        return await super()._make_request(method=method, url=f"{url}?{query}", headers=headers)

    async def request(
        self, method: RequestMethod, url: str, params: dict, data: dict, signed: bool
    ) -> dict:
        """Выполняет запрос к произвольному endpoint Aster API.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation
        """
        return await self._make_request(method=method, url=url, params=params, signed=signed)

    # topic: futures market data endpoints

    async def futures_ping(self) -> dict:
        """Проверка подключения к REST API.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#test-connectivity
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/ping"

        return await self._make_request("GET", url)

    async def futures_server_time(self) -> dict:
        """Получение серверного времени.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#check-server-time
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/time"

        return await self._make_request("GET", url)

    async def futures_exchange_info(self) -> dict:
        """Получение информации о символах рынка и текущих правилах биржевой торговли.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#exchange-information
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/exchangeInfo"

        return await self._make_request("GET", url)

    async def futures_depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#order-book
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/depth"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#recent-trades-list
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/trades"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#old-trades-lookup-market_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return await self._make_request("GET", url, params=params)

    async def futures_agg_trades(
        self,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение агрегированных сделок на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#compressed-aggregate-trades-list
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/aggTrades"
        params = {
            "symbol": symbol,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_index_price_klines(
        self,
        pair: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей по индексу цены.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#index-price-kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/indexPriceKlines"
        params = {
            "pair": pair,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_mark_price_klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение свечей по марк-цене.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price-kline-candlestick-data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/markPriceKlines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_mark_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение ставки финансирования и цены маркировки.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#mark-price
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/premiumIndex"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_funding_rate(
        self,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории ставок финансирования.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-funding-rate-history
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/fundingRate"
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_funding_info(self) -> list[dict]:
        """Получение информации о ставках финансирования.

        Этого эндпоинта нет в официальной документации.
        Пример ответа:
            ```[
                {
                    "symbol": "GNSUSD",
                    "interestRate": "0",
                    "time": 1773080759003,
                    "fundingIntervalHours": 8,
                    "fundingFeeCap": 0.02,
                    "fundingFeeFloor": -0.02,
                }, ...
            ]
        ```
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/fundingInfo"

        return await self._make_request("GET", url)

    async def futures_ticker_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен и объема за 24 часа.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#id-24hr-ticker-price-change-statistics
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/ticker/24hr"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов).

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#symbol-price-ticker
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/ticker/price"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def futures_ticker_book_ticker(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лучших цен bid/ask в книге ордеров.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#symbol-order-book-ticker
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/ticker/bookTicker"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    # topic: futures account/trade endpoints

    async def futures_position_mode(self, dual_side_position: bool) -> dict:
        """Изменение режима позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-position-mode-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/positionSide/dual"
        params = {"dualSidePosition": dual_side_position}

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_mode_get(self) -> dict:
        """Получение текущего режима позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-current-position-mode-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/positionSide/dual"

        return await self._make_request("GET", url, True)

    async def futures_multi_asset_mode(self, multi_assets_margin: bool) -> dict:
        """Изменение режима мультиактивной маржи.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-multi-assets-mode-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/multiAssetsMargin"
        params = {"multiAssetsMargin": multi_assets_margin}

        return await self._make_request("POST", url, True, params=params)

    async def futures_multi_asset_mode_get(self) -> dict:
        """Получение режима мультиактивной маржи.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-current-multi-assets-mode-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/multiAssetsMargin"

        return await self._make_request("GET", url, True)

    async def futures_order_create(
        self,
        symbol: str,
        side: Literal["BUY", "SELL"],
        type: Literal[
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ],
        position_side: Literal["BOTH", "LONG", "SHORT"] | None = None,
        time_in_force: str | None = None,
        quantity: NumberLike | None = None,
        reduce_only: bool | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stop_price: NumberLike | None = None,
        close_position: bool | None = None,
        activation_price: NumberLike | None = None,
        callback_rate: NumberLike | None = None,
        working_type: Literal["MARK_PRICE", "CONTRACT_PRICE"] | None = None,
        price_protect: Literal["TRUE", "FALSE"] | None = None,
        new_order_resp_type: str | None = None,
    ) -> dict:
        """Создание нового ордера на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#new-order-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "positionSide": position_side,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "reduceOnly": reduce_only,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stopPrice": stop_price,
            "closePosition": close_position,
            "activationPrice": activation_price,
            "callbackRate": callback_rate,
            "workingType": working_type,
            "priceProtect": price_protect,
            "newOrderRespType": new_order_resp_type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_batch_orders_create(self, orders: list[dict]) -> list[dict]:
        """Создание множественных ордеров одновременно на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#place-multiple-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/batchOrders"
        params = {
            "batchOrders": json.dumps(orders, separators=(",", ":")),
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_order_get(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение информации об ордере на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#query-order-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на фьючерсном рынке.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-order-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_orders_cancel_all(self, symbol: str) -> dict:
        """Отмена всех активных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-all-open-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/allOpenOrders"
        params = {"symbol": symbol}

        return await self._make_request("DELETE", url, True, params=params)

    async def futures_batch_orders_cancel(
        self,
        symbol: str,
        order_id_list: list[int] | None = None,
        orig_client_order_id_list: list[str] | None = None,
    ) -> list[dict]:
        """Отмена множественных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#cancel-multiple-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/batchOrders"
        params = {"symbol": symbol}

        if order_id_list:
            params["orderIdList"] = json.dumps(order_id_list, separators=(",", ":"))

        if orig_client_order_id_list:
            params["origClientOrderIdList"] = json.dumps(
                orig_client_order_id_list, separators=(",", ":")
            )

        return await self._make_request("DELETE", url, signed=True, params=params)

    async def futures_countdown_cancel_all(
        self,
        symbol: str,
        countdown_time: int,
    ) -> dict:
        """Автоотмена всех активных ордеров через указанное время.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#auto-cancel-all-open-orders-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/countdownCancelAll"
        params = {
            "symbol": symbol,
            "countdownTime": countdown_time,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_order_open(
        self,
        symbol: str,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Получение активного ордера.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#query-current-open-order-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/openOrder"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_open(self, symbol: str | None = None) -> list[dict]:
        """Получение всех активных ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#current-all-open-orders-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_orders_all(
        self,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех ордеров на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#all-orders-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/allOrders"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_balance(self) -> list[dict]:
        """Получение баланса фьючерсного аккаунта.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#futures-account-balance-v2-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/balance"

        return await self._make_request("GET", url, True)

    async def futures_account(self) -> dict:
        """Получение информации об аккаунте фьючерсов.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#account-information-v4-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/accountWithJoinMargin"

        return await self._make_request("GET", url, True)

    async def futures_leverage_change(self, symbol: str, leverage: int) -> dict:
        """Изменение кредитного плеча на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-initial-leverage-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/leverage"
        params = {"symbol": symbol, "leverage": leverage}

        return await self._make_request("POST", url, True, params=params)

    async def futures_margin_type_change(self, symbol: str, margin_type: str) -> dict:
        """Изменение типа маржи на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#change-margin-type-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/marginType"
        params = {"symbol": symbol, "marginType": margin_type}

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_margin_modify(
        self,
        symbol: str,
        position_side: str | None,
        amount: NumberLike,
        type: int,
    ) -> dict:
        """Изменение изолированной маржи позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#modify-isolated-position-margin-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/positionMargin"
        params = {
            "symbol": symbol,
            "positionSide": position_side,
            "amount": amount,
            "type": type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def futures_position_margin_history(
        self,
        symbol: str,
        type: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории изменений маржи позиции.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-position-margin-change-history-trade
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/positionMargin/history"
        params = {
            "symbol": symbol,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_position_info(self, symbol: str | None = None) -> list[dict]:
        """Получение информации о позициях на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#position-information-v2-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/positionRisk"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_my_trades(
        self,
        symbol: str,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории торгов на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#account-trade-list-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/userTrades"
        params = {
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_income(
        self,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории доходов на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#get-income-historyuser_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/income"
        params = {
            "symbol": symbol,
            "incomeType": income_type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_leverage_brackets(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лимитов по плечу и нотионалу.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#notional-and-leverage-brackets-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/leverageBracket"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_adl_quantile(self, symbol: str | None = None) -> list[dict]:
        """Получение информации об автоматической ликвидации.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#position-adl-quantile-estimation-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/adlQuantile"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def futures_force_orders(
        self,
        symbol: str | None = None,
        auto_close_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории принудительных ордеров пользователя.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#users-force-orders-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/forceOrders"
        params = {
            "symbol": symbol,
            "autoCloseType": auto_close_type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def futures_commission_rate(self, symbol: str) -> dict:
        """Получение комиссионных ставок на фьючерсах.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#user-commission-rate-user_data
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/commissionRate"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    # topic: futures user data streams

    async def futures_listen_key(self) -> dict:
        """Создание ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#start-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/listenKey"

        return await self._make_request("POST", url, True)

    async def futures_renew_listen_key(self) -> dict:
        """Обновление ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#keepalive-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/listenKey"

        return await self._make_request("PUT", url, True)

    async def futures_close_listen_key(self) -> dict:
        """Закрытие ключа прослушивания для подключения к пользовательскому вебсокету.

        https://docs.asterdex.com/product/aster-perpetuals/api/api-documentation#close-user-data-stream-user_stream
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/listenKey"

        return await self._make_request("DELETE", url, True)

    async def open_interest(self) -> dict:
        """Секретный эндпоинт откопанный в недрах фронтенда asterdex.com разработчиком @RushanWork.

        Формат возвращаемых данных:
            ```python
            {'code': '000000',
             'message': None,
             'messageDetail': None,
             'data': [
                {
                'symbol': 'TRUTHUSDT',
                'baseAsset': 'TRUTH',
                'quoteAsset': 'USDT',
                'lastPrice': 0.0126301,
                'highPrice': 0.0138825,
                'lowPrice': 0.012459,
                'baseVolume': 2011775,
                'quoteVolume': 26613.48,
                'openInterest': 85333.69964392  // В USDT
                }, ...
            ]
        ]
        ```
        """
        url = "https://www.asterdex.com/bapi/future/v1/public/future/aster/ticker/pair"

        return await super()._make_request("GET", url, headers=self._get_headers("GET"))
