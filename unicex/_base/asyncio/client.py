__all__ = ["BaseClient"]

import asyncio
from itertools import cycle
from typing import Any, Self

import aiohttp
from loguru import logger as _logger

from unicex.types import LoggerLike, RequestMethod


class BaseClient:
    """Базовый асинхронный класс для работы с API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> None:
        """Инициализация клиента.

        Параметры:
            session (`aiohttp.ClientSession`): Сессия для выполнения HTTP‑запросов.
            api_key (`str | None`): Ключ API для аутентификации.
            api_secret (`str | None`): Секретный ключ API для аутентификации.
            api_passphrase (`str | None`): Пароль API для аутентификации (Bitget).
            logger (`LoggerLike | None`): Логгер для вывода информации.
            max_retries (`int`): Максимальное количество повторных попыток запроса.
            retry_delay (`int | float`): Задержка между повторными попытками, сек.
            proxies (`list[str] | None`): Список HTTP(S)‑прокси для циклического использования.
            timeout (`int`): Максимальное время ожидания ответа от сервера, сек.
        """
        self._api_key = api_key
        self._api_secret = api_secret
        self._api_passphrase = api_passphrase
        self._session = session
        self._logger = logger or _logger
        self._max_retries = max(max_retries, 1)
        self._retry_delay = max(retry_delay, 0)
        self._proxies_cycle = cycle(proxies) if proxies else None
        self._timeout = timeout

    @classmethod
    async def create(
        cls,
        api_key: str | None = None,
        api_secret: str | None = None,
        api_passphrase: str | None = None,
        session: aiohttp.ClientSession | None = None,
        logger: LoggerLike | None = None,
        max_retries: int = 3,
        retry_delay: int | float = 0.1,
        proxies: list[str] | None = None,
        timeout: int = 10,
    ) -> Self:
        """Создаёт инстанцию клиента.

        Параметры:
            api_key (`str | None`): Ключ API для аутентификации.
            api_secret (`str | None`): Секретный ключ API для аутентификации.
            api_passphrase (`str | None`): Пароль API для аутентификации (Bitget).
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
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            logger=logger,
            max_retries=max_retries,
            retry_delay=retry_delay,
            proxies=proxies,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Закрывает сессию."""
        await self._session.close()

    def is_authorized(self) -> bool:
        """Проверяет наличие API‑ключей у клиента.

        Возвращает:
            `bool`: Признак наличия ключей.
        """
        return self._api_key is not None and self._api_secret is not None

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
    ) -> Any:
        """Выполняет HTTP‑запрос к API биржи.

        Параметры:
            method (`RequestMethod`): HTTP‑метод запроса.
            url (`str`): Полный URL API.
            params (`dict[str, Any] | None`): Параметры запроса (query string).
            data (`dict[str, Any] | None`): Тело запроса для POST/PUT.
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

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Обрабатывает HTTP‑ответ.

        Параметры:
            response (`aiohttp.ClientResponse`): Ответ HTTP‑запроса.

        Возвращает:
            `dict | list`: Ответ API в формате JSON.
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
