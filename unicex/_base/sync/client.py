__all__ = ["BaseClient"]

import time
from itertools import cycle
from typing import Any, Self

import requests
from loguru import logger as _logger

from unicex.exceptions import UniCexException
from unicex.types import LoggerLike, RequestMethod


class BaseClient:
    """Базовый синхронный класс для работы с API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        session: requests.Session | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (`str | None`): Ключ API для аутентификации.
            api_secret (`str | None`): Секретный ключ API для аутентификации.
            api_passphrase (`str | None`): Пароль API для аутентификации (Bitget).
            session (`requests.Session | None`): Сессия для выполнения HTTP‑запросов.
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера, сек.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._api_passphrase = api_passphrase
        self._session = session or requests.Session()
        self._logger = logger or _logger
        self._max_retries = max(max_retries, 1)
        self._retry_delay = max(retry_delay, 0)
        self._proxies_cycle = cycle(proxies) if proxies else None
        self._timeout = timeout

    def close(self) -> None:
        """Закрывает сессию."""
        self._session.close()

    def is_authorized(self) -> bool:
        """Проверяет наличие API‑ключей у клиента.

        Возвращает:
            `bool`: Признак наличия ключей.
        """
        return self._api_key is not None and self._api_secret is not None

    def __enter__(self) -> Self:
        """Вход в контекст.

        Возвращает:
            `Self`: Текущий экземпляр клиента.
        """
        return self

    def __exit__(self, *_):
        """Выход из контекста."""
        self.close()

    def _make_request(
        self,
        method: RequestMethod,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Выполняет HTTP‑запрос к API биржи.

        Параметры:
            method (`RequestMethod`): HTTP‑метод запроса.
            url (`str`): Полный URL API.
            params (`dict[str, Any] | None`): Параметры запроса (query string).
            data (`dict[str, Any] | None`): Тело запроса (application/x-www-form-urlencoded).
            json (`dict[str, Any] | None`): Тело запроса (application/json).
            headers (`dict[str, Any] | None`): Заголовки запроса.

        Возвращает:
            `dict | list`: Ответ API в формате JSON.
        """
        self._logger.debug(
            f"Request: {method} {url} | Params: {params} | Data: {data} | Headers: {headers}"
        )

        errors = []
        for attempt in range(1, self._max_retries + 1):
            try:
                proxies = (
                    (lambda p: {"http": p, "https": p})(next(self._proxies_cycle))
                    if self._proxies_cycle
                    else None
                )

                response: requests.Response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data if data is not None else None,
                    json=json if json is not None else None,
                    headers=headers,
                    proxies=proxies,
                    timeout=self._timeout,
                )
                return self._handle_response(response)

            except requests.Timeout as e:
                errors.append(e)
                self._logger.error(
                    f"Attempt {attempt}/{self._max_retries} failed: {type(e)} -> {e}"
                )
                if attempt < self._max_retries:
                    time.sleep(self._retry_delay)

        raise ConnectionError(
            f"Connection error after {self._max_retries} request on {method} {url}. Errors: {errors}"
        ) from errors[-1]

    def _handle_response(self, response: requests.Response) -> Any:
        """Обрабатывает HTTP‑ответ.

        Параметры:
            response (`requests.Response`): Ответ HTTP‑запроса.

        Возвращает:
            `dict | list`: Ответ API в формате JSON.
        """
        try:
            response.raise_for_status()
        except Exception as e:
            raise UniCexException(
                f"HTTP error: {e}. Response: {response.text}. Status code: {response.status_code}"
            ) from e

        if not response.content:
            raise UniCexException(f"Empty response. Status code: {response.status_code}")

        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise UniCexException(
                f"JSONDecodeError error: {e}. Response: {response.text}. Status code: {response.status_code}"
            ) from e

        try:
            result_str: str = str(result)
            self._logger.debug(
                f"Response: {result_str[:100]} {'...' if len(result_str) > 100 else ''}"
            )
        except Exception as e:
            self._logger.error(f"Error while log response: {e}")

        return result
