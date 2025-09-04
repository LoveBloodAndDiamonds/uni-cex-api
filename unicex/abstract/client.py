__all__ = [
    "BaseAsyncClient",
    "BaseSyncClient",
]

import asyncio
import logging
import time
from itertools import cycle
from typing import Any, Self

import aiohttp
import requests

from unicex.types import JsonLike, RequestMethod


class _BaseClient:
    """Базовый класс для создания клиентов для работы с API."""

    @staticmethod
    def filter_params(params: dict) -> dict:
        """Фильтрует параметры запроса, удаляя None-значения."""
        return {k: v for k, v in params.items() if v is not None}

    def __str__(self) -> str:
        return "APIClient"

    def __repr__(self) -> str:
        return "<APIClient>"


class BaseSyncClient(_BaseClient):
    """Базовый синхронный класс для создания клиентов для работы с API."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        session: requests.Session | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (str | None): Ключ API для аутентификации.
            api_secret (str | None): Секретный ключ API для аутентификации.
            session (requests.Session): Сессия для выполнения HTTP-запросов.
            logger (logging.Logger | None): Логгер для вывода информации.
            max_retries (int): Максимальное количество повторных попыток запроса.
            retry_delay (int | float): Задержка между повторными попытками.
            proxies (list[str] | None): Список HTTP(S) прокси для циклического использования.
            timeout (int): Максимальное время ожидания ответа от сервера.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = session or requests.Session()
        self._logger = logger or logging.getLogger()
        self._max_retries = max(max_retries, 1)
        self._retry_delay = max(retry_delay, 0)
        self._proxies_cycle = cycle(proxies) if proxies else None
        self._timeout = timeout

    def close(self) -> None:
        """Закрывает сессию."""
        self._session.close()

    def __enter__(self) -> Self:
        """Вход в контекст."""
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
        headers: dict[str, Any] | None = None,
    ):
        """Выполняет HTTP-запрос к API биржи.

        Параметры:
            method (RequestMethod): HTTP-метод запроса.
            url (str): Полный URL API.
            params (dict[str, Any] | None): Параметры запроса (query string).
            data (dict[str, Any] | None): Тело запроса для POST/PUT.
            headers (dict[str, Any] | None): Заголовки запроса.

        Возвращает:
            Ответ API в формате JSON.
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
                    json=data if method in {"POST", "PUT"} else None,
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

    def _handle_response(self, response: requests.Response):
        """Функция обрабатывает ответ от HTTP запроса.

        Параметры:
            response (requests.Response): Ответ от HTTP запроса.

        Возвращает:
            Обработанный ответ в виде словаря или списка.
        """
        response.raise_for_status()
        result = response.json()

        try:
            result_str: str = str(result)
            self._logger.debug(
                f"Response: {result_str[:100]} {'...' if len(result_str) > 100 else ''}"
            )
        except Exception as e:
            self._logger.error(f"Error while log response: {e}")

        return result


class BaseAsyncClient(_BaseClient):
    """Базовый асинхронный класс для создания клиентов для работы с API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str | None = None,
        api_secret: str | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            api_key (str | None): Ключ API для аутентификации.
            api_secret (str | None): Секретный ключ API для аутентификации.
            session (aiohttp.ClientSession): Сессия для выполнения HTTP-запросов.
            logger (logging.Logger | None): Логгер для вывода информации.
            max_retries (int): Максимальное количество повторных попыток запроса.
            retry_delay (int | float): Задержка между повторными попытками.
            proxies (list[str] | None): Список HTTP(S) прокси для циклического использования.
            timeout (int): Максимальное время ожидания ответа от сервера.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._session = session
        self._logger = logger or logging.getLogger()
        self._max_retries = max(max_retries, 1)
        self._retry_delay = max(retry_delay, 0)
        self._proxies_cycle = cycle(proxies) if proxies else None
        self._timeout = timeout

    @classmethod
    async def create(
        cls,
        api_key: str | None = None,
        api_secret: str | None = None,
        session: aiohttp.ClientSession | None = None,
        logger: logging.Logger | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        """Создает инстанцию клиента.

        Создать клиент можно и через __init__, но в таком случае session: `aiohttp.ClientSession` - обязательный параметр.

        Возвращает:
            Созданный экземпляр клиента.
        """
        return cls(
            session=session or aiohttp.ClientSession(),
            api_key=api_key,
            api_secret=api_secret,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Закрывает сессию."""
        await self._session.close()

    async def __aenter__(self) -> Self:
        """Вход в асинхронный контекст."""
        return self

    async def __aexit__(self, *_) -> None:
        """Выход из асинхронного контекста."""
        await self.close()

    async def _make_request(
        self,
        method: RequestMethod,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> JsonLike:
        """Выполняет HTTP-запрос к API биржи.

        Параметры:
            method (RequestMethod): HTTP-метод запроса.
            url (str): Полный URL API.
            params (dict[str, Any] | None): Параметры запроса (query string).
            data (dict[str, Any] | None): Тело запроса для POST/PUT.
            headers (dict[str, Any] | None): Заголовки запроса.

        Возвращает:
            Ответ API в формате JSON.
        """
        self._logger.debug(
            f"Request: {method} {url} | Params: {params} | Data: {data} | Headers: {headers}"
        )

        errors = []
        for attempt in range(1, self._max_retries + 1):
            try:
                async with self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data if method in {"POST", "PUT"} else None,  # Передача тела запроса
                    headers=headers,
                    proxy=next(self._proxies_cycle) if self._proxies_cycle else None,
                    timeout=aiohttp.ClientTimeout(total=self._timeout) if self._timeout else None,
                ) as response:
                    return await self._handle_response(response=response)

            except (aiohttp.ServerTimeoutError, aiohttp.ConnectionTimeoutError) as e:
                errors.append(e)
                self._logger.debug(
                    f"Attempt {attempt}/{self._max_retries} failed: {type(e)} -> {e}"
                )
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay)

        raise ConnectionError(
            f"Connection error after {self._max_retries} request on {method} {url}. Errors: {errors}"
        ) from errors[-1]

    async def _handle_response(self, response: aiohttp.ClientResponse) -> JsonLike:
        """Функция обрабатывает ответ от HTTP запроса.

        Параметры:
            response (requests.Response): Ответ от HTTP запроса.

        Возвращает:
            Обработанный ответ в виде словаря или списка.
        """
        response.raise_for_status()
        result = await response.json()

        try:
            result_str: str = str(result)
            self._logger.debug(
                f"Response: {result_str[:100]} {'...' if len(result_str) > 100 else ''}"
            )
        except Exception as e:
            self._logger.error(f"Error while log response: {e}")

        return result
