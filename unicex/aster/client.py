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
from unicex.exceptions import NotAuthorized, ResponseError
from unicex.types import LoggerLike, NumberLike, RequestMethod
from unicex.utils import filter_params


class Client(BaseClient):
    """Клиент для работы с Aster API.

    Использует авторизацию Aster V3: запросы подписываются приватным ключом
    API-кошелька (EIP-712), вместо устаревшей схемы API key + HMAC.
    """

    _BASE_FUTURES_URL: str = "https://fapi.asterdex.com"
    """Базовый URL для REST API Aster Futures."""

    _BASE_SPOT_URL: str = "https://sapi.asterdex.com"
    """Базовый URL для REST API Aster Spot."""

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
        nonce_window: int | None = None,
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
            nonce_window (`int | None`): Срок жизни изменяющих запросов в мс (1–60000), считая
                от их nonce. Не обработанный вовремя запрос отклоняется с ошибкой `-4227`.
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
            wallet = Account.from_key(private_key)
            self._wallet = wallet
            self._signer = wallet.address

        # Последний выданный nonce (микросекунды) для гарантии строгого возрастания.
        self._last_nonce = 0
        self._nonce_window = nonce_window

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
        nonce_window: int | None = None,
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
            nonce_window (`int | None`): Срок жизни изменяющих запросов в мс (1–60000).

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
            nonce_window=nonce_window,
        )

    @property
    def last_nonce(self) -> int:
        """Nonce последнего подписанного запроса (нужен для guarded-отмены размещённого ордера)."""
        return self._last_nonce

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

    def _build_signed_query(self, params: dict[str, Any], nonce: int | None = None) -> str:
        """Формирует подписанную query string для приватных эндпоинтов V3.

        Добавляет signer и nonce, кодирует параметры, подписывает строку и
        дописывает параметр signature.

        Параметры:
            params (`dict`): Бизнес-параметры запроса (уже отфильтрованные).
            nonce (`int | None`): Явный nonce (для guarded-отмены — nonce исходного ордера).

        Возвращает:
            `str`: Готовая query string вида "a=1&...&signer=...&nonce=...&signature=...".
        """
        if not self.is_authorized():
            raise NotAuthorized("Private key is required for private endpoints.")

        # signer и nonce обязательны для подписи Aster V3.
        nonce = nonce if nonce is not None else self._get_nonce()
        params = {**params, "signer": self._signer, "nonce": str(nonce)}

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
        nonce: int | None = None,
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
            nonce (`int | None`): Явный nonce для подписи (по умолчанию — новый).

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
        # nonceWindow действует только на изменяющие запросы, которые идут через sequencer
        if self._nonce_window is not None and method != "GET" and "nonceWindow" not in params:
            params["nonceWindow"] = self._nonce_window
        query = self._build_signed_query(params, nonce)
        return await super()._make_request(method=method, url=f"{url}?{query}", headers=headers)

    def _validate_response(
        self, status_code: int, response_text: str, response_json: dict[str, Any]
    ) -> None:
        """Выбрасывает ResponseError, если биржа вернула ошибку с HTTP 200.

        Ошибки Aster имеют отрицательный числовой `code` (например, `-5050 DEPOSIT_REQUIRED`:
        приватные V3-эндпоинты доступны только после депозита на основной кошелёк).
        """
        if not isinstance(response_json, dict):
            return
        code = response_json.get("code")
        if isinstance(code, int) and code < 0:
            raise ResponseError(
                response_json.get("msg", ""),
                code=str(code),
                status_code=status_code,
                response_text=response_text,
                response_json=response_json,
            )

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

    async def futures_funding_info(self, symbol: str | None = None) -> list[dict]:
        """Получение настроек фандинга: интервал, ограничения ставки.

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
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

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

    async def futures_index_references(self, symbol: str) -> dict:
        """Состав индексной цены: биржи и их веса.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/indexreferences"
        params = {
            "symbol": symbol,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_remaining_openable_notional(self, symbol: str, leverage: int) -> dict:
        """Оставшийся нотионал, доступный для открытия при заданном плече.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/remainingOpenableNotionalValue"
        params = {
            "symbol": symbol,
            "leverage": leverage,
        }

        return await self._make_request("GET", url, params=params)

    async def futures_asset_logos(self) -> dict:
        """Ссылки на логотипы всех активов.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/common/asset/all-asset-logo"

        return await self._make_request("GET", url)

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
        peg_price_type: Literal["COUNTERPARTY_1", "QUEUE_1"] | None = None,
        stp_mode: Literal["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"] | None = None,
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
            "pegPriceType": peg_price_type,
            "stpMode": stp_mode,
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
        client_tran_id: str | None = None,
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
            "clientTranId": client_tran_id,
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
        order_id: int | None = None,
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
            "orderId": order_id,
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
        url = self._BASE_FUTURES_URL + "/fapi/v3/leverageBrackets"
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

    async def futures_order_modify(
        self,
        symbol: str,
        quantity: NumberLike,
        price: NumberLike,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
        side: str | None = None,
    ) -> dict:
        """Изменение лимитного ордера.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/order"
        params = {
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
        }

        return await self._make_request("PUT", url, signed=True, params=params)

    async def futures_batch_orders_modify(self, batch_orders: list[Any]) -> dict:
        """Пакетное изменение лимитных ордеров.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/batchOrders"
        params = {
            "batchOrders": json.dumps(batch_orders, separators=(",", ":")),
        }

        return await self._make_request("PUT", url, signed=True, params=params)

    async def futures_chase_order_create(
        self,
        symbol: str,
        side: str,
        quantity_unit: str,
        quantity: NumberLike,
        position_side: str | None = None,
        reduce_only: str | None = None,
        chase_offset: NumberLike | None = None,
        chase_offset_type: str | None = None,
        max_chase_offset: NumberLike | None = None,
        max_chase_offset_type: str | None = None,
        time_in_force: str | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Размещение chase-ордера (лимитный ордер, следующий за лучшей ценой).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/chase"
        params = {
            "symbol": symbol,
            "side": side,
            "positionSide": position_side,
            "quantityUnit": quantity_unit,
            "quantity": quantity,
            "reduceOnly": reduce_only,
            "chaseOffset": chase_offset,
            "chaseOffsetType": chase_offset_type,
            "maxChaseOffset": max_chase_offset,
            "maxChaseOffsetType": max_chase_offset_type,
            "timeInForce": time_in_force,
            "clientStrategyId": client_strategy_id,
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_strategy_order_create(
        self,
        strategy_type: str,
        sub_order_list: list[Any],
        client_strategy_id: str | None = None,
        builder: str | None = None,
        fee_rate: NumberLike | None = None,
    ) -> dict:
        """Размещение стратегического ордера.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/placeStrategyOrder"
        params = {
            "clientStrategyId": client_strategy_id,
            "strategyType": strategy_type,
            "subOrderList": json.dumps(sub_order_list, separators=(",", ":")),
            "builder": builder,
            "feeRate": fee_rate,
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_strategy_order_update(
        self,
        strategy_id: int,
        strategy_type: str,
        sub_order_list: list[Any],
    ) -> dict:
        """Изменение стратегического ордера.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/updateStrategyOrder"
        params = {
            "strategyId": strategy_id,
            "strategyType": strategy_type,
            "subOrderList": json.dumps(sub_order_list, separators=(",", ":")),
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_strategy_open_orders(
        self,
        strategy_type: str,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
    ) -> dict:
        """Активные стратегические ордера.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/strategyOpenOrder"
        params = {
            "strategyId": strategy_id,
            "clientStrategyId": client_strategy_id,
            "strategyType": strategy_type,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_strategy_orders_history(
        self,
        strategy_type: str,
        strategy_id: int | None = None,
        client_strategy_id: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """История стратегических ордеров.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/strategyHistoryOrder"
        params = {
            "strategyId": strategy_id,
            "clientStrategyId": client_strategy_id,
            "strategyType": strategy_type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_stp_mode_change(self, stp_mode: str) -> dict:
        """Изменение режима защиты от самоисполнения (STP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/stpMode"
        params = {
            "stpMode": stp_mode,
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_stp_mode(self) -> dict:
        """Текущий режим защиты от самоисполнения (STP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/stpMode"

        return await self._make_request("GET", url, signed=True)

    async def futures_mmp_update(
        self,
        symbol: str,
        window_time_in_milliseconds: int,
        frozen_time_in_milliseconds: int,
        qty_limit: int | None = None,
        value_limit: int | None = None,
        delta_limit: int | None = None,
    ) -> dict:
        """Настройка защиты маркет-мейкера (MMP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/mmp"
        params = {
            "symbol": symbol,
            "windowTimeInMilliseconds": window_time_in_milliseconds,
            "frozenTimeInMilliseconds": frozen_time_in_milliseconds,
            "qtyLimit": qty_limit,
            "valueLimit": value_limit,
            "deltaLimit": delta_limit,
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_mmp(self, symbol: str | None = None) -> dict:
        """Настройки защиты маркет-мейкера (MMP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/mmp"
        params = {
            "symbol": symbol,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_mmp_delete(self, symbol: str) -> dict:
        """Удаление настроек защиты маркет-мейкера (MMP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/mmp"
        params = {
            "symbol": symbol,
        }

        return await self._make_request("DELETE", url, signed=True, params=params)

    async def futures_mmp_reset(self, symbol: str) -> dict:
        """Сброс срабатывания защиты маркет-мейкера (MMP).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/mmpReset"
        params = {
            "symbol": symbol,
        }

        return await self._make_request("POST", url, signed=True, params=params)

    async def futures_noop(self) -> dict:
        """Пустое действие для инвалидации ожидающих nonce.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/noop"

        return await self._make_request("POST", url, signed=True)

    async def futures_asset_exchange(self) -> dict:
        """Ручной обмен активов в режиме мультиактивной маржи.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/assetExchange"

        return await self._make_request("POST", url, signed=True)

    async def futures_income_page(
        self,
        symbol: str | None = None,
        income_type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """История доходов с постраничной навигацией.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/incomePage"
        params = {
            "symbol": symbol,
            "incomeType": income_type,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_referral_invitee_info(self, address: str) -> dict:
        """Информация о приглашённом пользователе.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/referral/inviteeInfo"
        params = {
            "address": address,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_direct_announcements(
        self,
        page: int | None = None,
        size: int | None = None,
    ) -> dict:
        """Персональные объявления пользователя.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/announcement/direct"
        params = {
            "page": page,
            "size": size,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_direct_announcement(self, id: int) -> dict:
        """Персональное объявление по идентификатору.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/announcement/directById"
        params = {
            "id": id,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_approved_users(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Пользователи, подтвердившие builder-код.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/approvedUserList"
        params = {
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_accounts(
        self,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Аккаунты пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userAccounts"
        params = {
            "userAddresses": user_addresses,
            "symbol": symbol,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_orders(
        self,
        user_addresses: str | None = None,
        symbol: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Ордера пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userAllOrders"
        params = {
            "userAddresses": user_addresses,
            "symbol": symbol,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_balances(
        self,
        user_addresses: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Балансы пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userBalances"
        params = {
            "userAddresses": user_addresses,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_commission_rates(
        self,
        symbol: str,
        user_addresses: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Ставки комиссии пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userCommissionRates"
        params = {
            "userAddresses": user_addresses,
            "symbol": symbol,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_commissions(
        self,
        user_addresses: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Комиссии builder-кода по сделкам пользователей.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userCommissions"
        params = {
            "userAddresses": user_addresses,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_open_orders(
        self,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Активные ордера пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userOpenOrders"
        params = {
            "userAddresses": user_addresses,
            "symbol": symbol,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_positions(
        self,
        user_addresses: str | None = None,
        symbol: str | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Позиции пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userPositionRisk"
        params = {
            "userAddresses": user_addresses,
            "symbol": symbol,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_builder_user_trades(
        self,
        user_addresses: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        page: int | None = None,
        limit: int | None = None,
    ) -> dict:
        """Сделки пользователей builder-кода.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/builder/userTrades"
        params = {
            "userAddresses": user_addresses,
            "startTime": start_time,
            "endTime": end_time,
            "page": page,
            "limit": limit,
        }

        return await self._make_request("GET", url, signed=True, params=params)

    async def futures_guarded_order_cancel(
        self,
        symbol: str,
        order_nonce: int,
        order_id: int | None = None,
        orig_client_order_id: str | None = None,
    ) -> dict:
        """Отмена ордера с защитой по nonce, с которым ордер был размещён (`client.last_nonce`).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/guardedCancelOrder"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("DELETE", url, True, params=params, nonce=order_nonce)

    async def futures_guarded_batch_orders_cancel(
        self,
        symbol: str,
        order_nonce: int,
        order_id_list: list[int] | None = None,
        orig_client_order_id_list: list[str] | None = None,
    ) -> dict:
        """Отмена нескольких ордеров с защитой по nonce, с которым они были размещены.

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/guardedBatchOrders"
        params = {
            "symbol": symbol,
            "orderIdList": json.dumps(order_id_list, separators=(",", ":"))
            if order_id_list
            else None,
            "origClientOrderIdList": json.dumps(orig_client_order_id_list, separators=(",", ":"))
            if orig_client_order_id_list
            else None,
        }

        return await self._make_request("DELETE", url, True, params=params, nonce=order_nonce)

    async def futures_account_without_join_margin(self) -> dict:
        """Информация об аккаунте без учёта мультиактивной маржи (`joinMargin=false`).

        https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-futures-api-v3.md
        """
        url = self._BASE_FUTURES_URL + "/fapi/v3/account"

        return await self._make_request("GET", url, True)

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

    # topic: spot market data endpoints

    async def ping(self) -> dict:
        """Проверка подключения к спотовому REST API.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/ping"

        return await self._make_request("GET", url)

    async def server_time(self) -> dict:
        """Получение серверного времени спотового рынка.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/time"

        return await self._make_request("GET", url)

    async def exchange_info(self) -> dict:
        """Получение торговых правил и информации о спотовых символах.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/exchangeInfo"

        return await self._make_request("GET", url)

    async def depth(self, symbol: str, limit: int | None = None) -> dict:
        """Получение книги ордеров на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/depth"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def trades(self, symbol: str, limit: int | None = None) -> list[dict]:
        """Получение последних сделок на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/trades"
        params = {"symbol": symbol, "limit": limit}

        return await self._make_request("GET", url, params=params)

    async def historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> list[dict]:
        """Получение исторических сделок на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/historicalTrades"
        params = {"symbol": symbol, "limit": limit, "fromId": from_id}

        return await self._make_request("GET", url, params=params)

    async def agg_trades(
        self,
        symbol: str,
        from_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение агрегированных сделок на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/aggTrades"
        params = {
            "symbol": symbol,
            "fromId": from_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def klines(
        self,
        symbol: str,
        interval: str,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Получение исторических свечей на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, params=params)

    async def ticker_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение статистики изменения цен за 24 часа на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/24hr"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def ticker_opt_24hr(self, symbol: str | None = None) -> dict | list[dict]:
        """Альтернативная статистика за 24 часа на споте (формат с `ticker_id`, `last_price`).

        В документации упомянут без описания: https://github.com/asterdex/api-docs/blob/master/V3(Recommended)/EN/aster-finance-spot-api-v3.md
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/opt/24hr"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def ticker_price(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение последней цены тикера(ов) на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/price"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def ticker_book_ticker(self, symbol: str | None = None) -> dict | list[dict]:
        """Получение лучших цен bid/ask в книге ордеров на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/ticker/bookTicker"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, params=params)

    async def commission_rate(self, symbol: str) -> dict:
        """Получение комиссионных ставок по символу на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/commissionRate"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    # topic: spot account/trade endpoints

    async def noop(self) -> dict:
        """Отменяет ранее отправленные, ещё не выполненные транзакции (nonce должен совпадать).

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/noop"

        return await self._make_request("POST", url, True)

    async def order_create(
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
        ],
        time_in_force: str | None = None,
        quantity: NumberLike | None = None,
        quote_order_qty: NumberLike | None = None,
        price: NumberLike | None = None,
        new_client_order_id: str | None = None,
        stop_price: NumberLike | None = None,
        self_trading_protection_mode: Literal[1, 2, 4, 8] | None = None,
    ) -> dict:
        """Создание нового ордера на споте.

        self_trading_protection_mode: 1 (NONE), 2 (CANCEL_TAKER), 4 (CANCEL_MAKER), 8 (CANCEL_BOTH).

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "timeInForce": time_in_force,
            "quantity": quantity,
            "quoteOrderQty": quote_order_qty,
            "price": price,
            "newClientOrderId": new_client_order_id,
            "stopPrice": stop_price,
            "selfTradingProtectionMode": self_trading_protection_mode,
        }

        return await self._make_request("POST", url, True, params=params)

    async def order_cancel(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Отмена активного ордера на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("DELETE", url, True, params=params)

    async def order_get(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Получение информации об ордере на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def order_open(
        self, symbol: str, order_id: int | None = None, orig_client_order_id: str | None = None
    ) -> dict:
        """Получение активного ордера на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrder"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "origClientOrderId": orig_client_order_id,
        }

        return await self._make_request("GET", url, True, params=params)

    async def orders_open(self, symbol: str | None = None) -> list[dict]:
        """Получение всех активных ордеров на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/openOrders"
        params = {"symbol": symbol}

        return await self._make_request("GET", url, True, params=params)

    async def orders_cancel_all(
        self,
        symbol: str,
        order_id_list: list[int] | None = None,
        orig_client_order_id_list: list[str] | None = None,
    ) -> dict:
        """Отмена всех активных ордеров на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/allOpenOrders"
        params = {"symbol": symbol}

        if order_id_list:
            params["orderIdList"] = json.dumps(order_id_list, separators=(",", ":"))

        if orig_client_order_id_list:
            params["origClientOrderIdList"] = json.dumps(
                orig_client_order_id_list, separators=(",", ":")
            )

        return await self._make_request("DELETE", url, True, params=params)

    async def orders_all(
        self,
        symbol: str,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение всех ордеров на споте (активных, отменённых, исполненных).

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/allOrders"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def account(self) -> dict:
        """Получение информации о спотовом аккаунте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/account"

        return await self._make_request("GET", url, True)

    async def my_trades(
        self,
        symbol: str | None = None,
        order_id: int | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        from_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории торгов аккаунта на споте.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/userTrades"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "startTime": start_time,
            "endTime": end_time,
            "fromId": from_id,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def transaction_history(
        self,
        asset: str | None = None,
        type: str | None = None,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        """Получение истории транзакций спотового аккаунта.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/transactionHistory"
        params = {
            "asset": asset,
            "type": type,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        return await self._make_request("GET", url, True, params=params)

    async def asset_transfer(
        self, amount: NumberLike, asset: str, client_tran_id: str, kind_type: str
    ) -> dict:
        """Перевод средств между спотовым и фьючерсным кошельками.

        kind_type: FUTURE_SPOT (фьючерс -> спот) / SPOT_FUTURE (спот -> фьючерс).

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/asset/wallet/transfer"
        params = {
            "amount": amount,
            "asset": asset,
            "clientTranId": client_tran_id,
            "kindType": kind_type,
        }

        return await self._make_request("POST", url, True, params=params)

    async def withdraw_fee(self, chain_id: str, asset: str) -> dict:
        """Получение оценки комиссии за вывод средств со спота.

        chain_id: 1(ETH), 56(BSC), 42161(Arbitrum).

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/aster/withdraw/estimateFee"
        params = {"chainId": chain_id, "asset": asset}

        return await self._make_request("GET", url, True, params=params)

    async def withdraw(
        self,
        chain_id: str,
        asset: str,
        amount: NumberLike,
        fee: NumberLike,
        receiver: str,
        user_nonce: str,
        user_signature: str,
    ) -> dict:
        """Вывод средств со спотового аккаунта.

        chain_id: 1(ETH), 56(BSC), 42161(Arbitrum).

        Эндпоинт требует отдельную EIP-712 подпись действия (домен "Aster", тип "Action"),
        которую вызывающий код должен сформировать заранее и передать в user_signature
        вместе с соответствующим user_nonce (микросекунды). Сам запрос дополнительно
        подписывается стандартной подписью V3.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/aster/user-withdraw"
        params = {
            "chainId": chain_id,
            "asset": asset,
            "amount": amount,
            "fee": fee,
            "receiver": receiver,
            "userNonce": user_nonce,
            "userSignature": user_signature,
        }

        return await self._make_request("POST", url, True, params=params)

    # topic: spot user data streams

    async def listen_key(self) -> dict:
        """Создание ключа прослушивания спотового пользовательского вебсокета.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/listenKey"

        return await self._make_request("POST", url, True)

    async def renew_listen_key(self, listen_key: str | None = None) -> dict:
        """Продление ключа прослушивания спотового пользовательского вебсокета.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/listenKey"
        params = {"listenKey": listen_key}

        return await self._make_request("PUT", url, True, params=params)

    async def close_listen_key(self, listen_key: str | None = None) -> dict:
        """Закрытие ключа прослушивания спотового пользовательского вебсокета.

        https://docs.asterdex.com/product/aster-spot/api/api-documentation
        """
        url = self._BASE_SPOT_URL + "/api/v3/listenKey"
        params = {"listenKey": listen_key}

        return await self._make_request("DELETE", url, True, params=params)
