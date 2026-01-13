__all__ = ["IUniWebsocketManager"]

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, overload

from loguru import logger as _logger

from unicex._base import BaseClient, Websocket
from unicex.enums import Timeframe
from unicex.exceptions import AdapterError
from unicex.types import LoggerLike

from .uni_client import IUniClient

type CallbackType = Callable[[Any], Awaitable[None]]


class IUniWebsocketManager(ABC):
    """Интерфейс менеджера унифицированных вебсокетов."""

    def __init__(
        self, client: BaseClient | IUniClient | None = None, logger: LoggerLike | None = None
    ) -> None:
        """Инициализирует унифицированный менеджер вебсокетов.

        Параметры:
            client (`BaseClient | IUniClient | None`): Клиент или унифицированный клиент. Нужен для подключения к приватным топикам.
            logger (`LoggerLike | None`): Логгер для записи логов.
        """
        if isinstance(client, IUniClient):
            client = client.client
        self._client = client
        self._logger = logger or _logger

    def _make_wrapper(
        self, adapter_func: Callable[[dict], Any], callback: CallbackType
    ) -> CallbackType:
        """Создает обертку над callback, применяя адаптер к сырым сообщениям."""

        async def _wrapper(raw_msg: dict) -> None:
            try:
                adapted = adapter_func(raw_msg)
            except Exception as e:
                if isinstance(e, AdapterError):
                    try:
                        if self._is_service_message(raw_msg):
                            return
                    except Exception as err:
                        self._logger.error(f"Failed to handle adapter error: {e}")
                        raise err from e
                self._logger.warning(f"Failed to adapt message: {e}")
                return
            if isinstance(adapted, list):
                for item in adapted:
                    await callback(item)
            else:
                await callback(adapted)

        return _wrapper

    def _is_service_message(self, raw_msg: Any) -> bool:
        """Дополнительно обрабатывает ошибку адаптации сообщения на случай, если это сервисное сообщение, например `ping` или `subscribe`.

        Переопределяется в каждом наследнике в связи с разным форматом входящих данных.
        """
        return False

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета для управления соединением.
        """
        ...

    @overload
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def futures_klines(
        self,
        callback: CallbackType,
        timeframe: Timeframe,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим свечей (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            timeframe (`Timeframe`): Временной интервал свечей.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        ...

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def trades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        ...

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (spot) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        ...

    @overload
    def futures_trades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_trades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def futures_trades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        ...

    @overload
    def futures_aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: str,
        symbols: None = None,
    ) -> Websocket: ...

    @overload
    def futures_aggtrades(
        self,
        callback: CallbackType,
        *,
        symbol: None = None,
        symbols: Sequence[str],
    ) -> Websocket: ...

    @abstractmethod
    def futures_aggtrades(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Открывает стрим агрегированных сделок (futures) с унификацией сообщений.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Должен быть указан либо `symbol`, либо `symbols`.

        Возвращает:
            `Websocket`: Экземпляр вебсокета.
        """
        ...
