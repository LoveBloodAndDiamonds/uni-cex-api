__all__ = ["ClientMixin", "WebsocketManagerMixin", "UserWebsocketMixin"]

import time
from typing import Any

from unicex.exceptions import NotAuthorized, NotSupported
from unicex.utils import dict_to_query_string, filter_params, generate_hmac_sha256_signature

from .types import AccountType


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
            - добавляет timestamp и recvWindow;
            - формирует HMAC SHA256 подпись;
            - возвращает заголовки с X-MBX-APIKEY.

        Если signed=False:
            - возвращает только отфильтрованные params/data.

        Параметры:
            signed (bool): Нужно ли подписывать запрос.
            params (dict | None): Параметры для query string.
            data (dict | None): Параметры для тела запроса.

        Возвращает:
            tuple:
                - payload (dict): Параметры/тело запроса с подписью (если нужно).
                - headers (dict | None): Заголовки для запроса или None.
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
        )

        headers = self._get_headers()
        return payload, headers


class WebsocketManagerMixin:
    """Миксин для менеджеров вебсокетов Binance. Содержит общий функционал для работы с WS API Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    def _generate_stream_url(
        self,
        type: str,
        url: str,
        symbol: str | None = None,
        symbols: list[str] | None = None,
    ) -> str:
        """Генерирует URL для вебсокета Binance. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (StreamType): Тип вебсокета.
            url (str): Базовый URL для вебсокета.
            symbol (str | None): Символ для подписки.
            symbols (list[str] | None): Список символов для подписки.

        Возвращает:
            str: URL для вебсокета.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if symbol:
            return f"{url}/ws/{symbol.lower()}@{type}"
        if symbols:
            streams = "/".join(f"{s.lower()}@{type}" for s in symbols)
            return f"{url}/stream?streams={streams}"
        return f"{url}/ws/{type}"


class UserWebsocketMixin:
    """Миксин для пользовательского вебсокета Binance. Содержит общий функционал для работы с пользовательским WS API Binance."""

    _BASE_SPOT_WSS: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_WSS: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    _RENEW_INTERVAL: int = 30 * 60
    """Интервал продления listenKey (сек.)"""

    @classmethod
    def _create_ws_url(cls, type: AccountType, listen_key: str) -> str:
        """Создает URL для подключения к WebSocket."""
        if type == "FUTURES":
            return f"{cls._BASE_FUTURES_WSS}/ws/{listen_key}"
        if type == "SPOT":
            return f"{cls._BASE_SPOT_WSS}/ws/{listen_key}"
        raise NotSupported(f"Account type '{type}' not supported")
