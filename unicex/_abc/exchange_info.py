__all__ = ["IExchangeInfo"]

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loguru import logger

from unicex.types import TickersInfoDict

if TYPE_CHECKING:
    import loguru


class IExchangeInfo(ABC):
    """Интерфейс для наследников, которые предзагружают и обновляют информацию о бирже."""

    _loaded: bool
    """Флаг, указывающий, была ли информация о бирже загружена."""

    _running: bool
    """Флаг, указывающий, запущена ли фоновая задача для обновления информации о бирже."""

    _tickers_info: TickersInfoDict
    """Словарь с информацией о округлении и размере контракта (если есть) для каждого тикера."""

    _logger: "loguru.Logger"
    """Логгер для записи сообщений о работе с биржей."""

    def __init_subclass__(cls, **kwargs):
        """Инициализация подкласса. Функция нужна, чтобы у каждого наследника была своя копия атрибутов."""
        super().__init_subclass__(**kwargs)
        cls._tickers_info = {}
        cls._loaded = False
        cls._running = False
        cls._logger = logger

    @classmethod
    async def start(cls, update_interval_seconds: int = 60 * 60) -> None:
        """Запускает фоновую задачу с бесконечным циклом для загрузки данных."""
        cls._running = True
        asyncio.create_task(cls._load_exchange_info_loop(update_interval_seconds))

    @classmethod
    async def stop(cls) -> None:
        """Останавливает фоновую задачу для обновления информации о бирже."""
        cls._running = False

    @classmethod
    async def set_logger(cls, logger: "loguru.Logger") -> None:
        """Устанавливает логгер для записи сообщений о работе с биржей."""
        cls._logger = logger

    @classmethod
    async def _load_exchange_info_loop(cls, update_interval_seconds: int) -> None:
        """Запускает бесконечный цикл для загрузки данных о бирже."""
        while cls._running:
            try:
                await cls.load_exchange_info()
            except Exception as e:
                cls._logger.error(f"Error loading exchange data: {e}")
            for _ in range(update_interval_seconds):
                if not cls._running:
                    break
                await asyncio.sleep(1)

    @classmethod
    async def load_exchange_info(cls) -> None:
        """Принудительно вызывает загрузку информации о бирже."""
        await cls._load_exchange_info()
        cls._loaded = True
        cls._logger.debug("Exchange data loaded")

    @classmethod
    @abstractmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        ...

    @classmethod
    def get_price_precisions(cls, symbol: str) -> int:
        """Возвращает количество знаков после запятой для тикера."""
        try:
            return cls._tickers_info[symbol]["price"]
        except KeyError as e:
            if not cls._loaded:
                raise ValueError("Exchange data not loaded") from None
            raise KeyError(f"Symbol {symbol} not found") from e

    @classmethod
    def get_quantity_precisions(cls, symbol: str) -> int:
        """Возвращает количество знаков после запятой для объема."""
        try:
            return cls._tickers_info[symbol]["quantity"]
        except KeyError as e:
            if not cls._loaded:
                raise ValueError("Exchange data not loaded") from None
            raise KeyError(f"Symbol {symbol} not found") from e

    @classmethod
    def get_contract_multiplier(cls, symbol: str) -> float | None:
        """Возвращает множитель контракта."""
        try:
            return cls._tickers_info[symbol]["contract_multiplier"]
        except KeyError as e:
            if not cls._loaded:
                raise ValueError("Exchange data not loaded") from None
            raise KeyError(f"Symbol {symbol} not found") from e

    @classmethod
    def round_price(cls, symbol: str, price: float) -> float:
        """Округляет цену до ближайшего возможного значения."""
        try:
            precision = cls._tickers_info[symbol]["price"]
        except KeyError as e:
            if not cls._loaded:
                raise ValueError("Exchange data not loaded") from None
            raise KeyError(f"Symbol {symbol} not found") from e
        return round(price, precision)

    @classmethod
    def round_quantity(cls, symbol: str, quantity: float) -> float:
        """Округляет объем до ближайшего возможного значения."""
        try:
            precision = cls._tickers_info[symbol]["quantity"]
        except KeyError as e:
            if not cls._loaded:
                raise ValueError("Exchange data not loaded") from None
            raise KeyError(f"Symbol {symbol} not found") from e
        return round(quantity, precision)
