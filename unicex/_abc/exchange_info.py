__all__ = ["IExchangeInfo"]

import asyncio
import math
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

import aiohttp
from loguru import logger

from unicex.enums import MarketType
from unicex.types import TickerInfoItem, TickersInfoDict

if TYPE_CHECKING:
    import loguru


class IExchangeInfo(ABC):
    """Интерфейс для наследников, которые предзагружают и обновляют информацию о бирже."""

    _loaded: bool
    """Флаг, указывающий, была ли информация о бирже загружена."""

    _running: bool
    """Флаг, указывающий, запущена ли фоновая задача для обновления информации о бирже."""

    _tickers_info: TickersInfoDict
    """Словарь с информацией о округлении для каждого тикера."""

    _futures_tickers_info: TickersInfoDict
    """Словарь с информацией о округлении и размере контракта (если есть) для каждого тикера."""

    _logger: "loguru.Logger"
    """Логгер для записи сообщений о работе с биржей."""

    exchange_name: ClassVar[str] = "not_defined_exchange"
    """Название биржи, на которой работает класс."""

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
                cls._logger.error(f"Error loading exchange data for {cls.exchange_name}: {e}")
            for _ in range(update_interval_seconds):
                if not cls._running:
                    break
                await asyncio.sleep(1)

    @classmethod
    async def load_exchange_info(cls) -> None:
        """Принудительно вызывает загрузку информации о бирже."""
        async with aiohttp.ClientSession() as session:
            try:
                await cls._load_spot_exchange_info(session)
                cls._logger.debug(f"Loaded spot exchange data for {cls.exchange_name} ")
            except Exception as e:
                cls._logger.error(f"Error loading spot exchange data for {cls.exchange_name}: {e}")
            try:
                await cls._load_futures_exchange_info(session)
                cls._logger.debug(f"Loaded futures exchange data for {cls.exchange_name} ")
            except Exception as e:
                cls._logger.error(
                    f"Error loading futures exchange data for {cls.exchange_name}: {e}"
                )
        cls._loaded = True

    @classmethod
    @abstractmethod
    async def _load_spot_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для спотового рынка."""
        ...

    @classmethod
    @abstractmethod
    async def _load_futures_exchange_info(cls, session: aiohttp.ClientSession) -> None:
        """Загружает информацию о бирже для фьючерсного рынка."""
        ...

    @classmethod
    def get_ticker_info(
        cls, symbol: str, market_type: MarketType = MarketType.SPOT
    ) -> TickerInfoItem:  # type: ignore[reportReturnType]
        """Возвращает информацию о тикере по его символу."""
        try:
            if market_type == MarketType.SPOT:
                return cls._tickers_info[symbol]
            return cls._futures_tickers_info[symbol]
        except KeyError as e:
            cls._handle_key_error(e, symbol)

    @classmethod
    def get_futures_ticker_info(cls, symbol: str) -> TickerInfoItem:
        """Возвращает информацию о тикере фьючерсов по его символу."""
        return cls.get_ticker_info(symbol, MarketType.FUTURES)

    @classmethod
    def round_price(
        cls, symbol: str, price: float, market_type: MarketType = MarketType.SPOT
    ) -> float:  # type: ignore
        """Округляет цену до ближайшего возможного значения."""
        try:
            if market_type == MarketType.SPOT:
                precision = cls._tickers_info[symbol]["tick_precision"]
                step = cls._tickers_info[symbol]["tick_step"]
            else:
                precision = cls._futures_tickers_info[symbol]["tick_precision"]
                step = cls._futures_tickers_info[symbol]["tick_step"]
            if precision:
                return cls._floor_round(price, precision)
            return cls._floor_to_step(price, step)  # type: ignore
        except KeyError as e:
            cls._handle_key_error(e, symbol)

    @classmethod
    def round_quantity(
        cls, symbol: str, quantity: float, market_type: MarketType = MarketType.SPOT
    ) -> float:  # type: ignore
        """Округляет объем до ближайшего возможного значения."""
        try:
            if market_type == MarketType.SPOT:
                precision = cls._tickers_info[symbol]["size_precision"]
                step = cls._tickers_info[symbol]["size_step"]
            else:
                precision = cls._futures_tickers_info[symbol]["size_precision"]
                step = cls._futures_tickers_info[symbol]["size_step"]
            if precision:
                return cls._floor_round(quantity, precision)
            return cls._floor_to_step(quantity, step)  # type: ignore
        except KeyError as e:
            cls._handle_key_error(e, symbol)

    @classmethod
    def round_futures_price(cls, symbol: str, price: float) -> float:
        """Округляет цену до ближайшего возможного значения на фьючерсах."""
        return cls.round_price(symbol, price, MarketType.FUTURES)

    @classmethod
    def round_futures_quantity(cls, symbol: str, quantity: float) -> float:
        """Округляет объем до ближайшего возможного значения на фьючерсах."""
        return cls.round_quantity(symbol, quantity, MarketType.FUTURES)

    @staticmethod
    def _floor_to_step(value: float, step: float) -> float:
        """Округляет число вниз до ближайшего кратного шага.

        Принимает:
            value (float): Исходное число.
            step: (float): Шаг округления (> 0).

        Возвращает:
            Число, округлённое вниз до кратного step.

        Примеры:
            >>> floor_to_step(0.16, 0.05)
            0.15
            >>> floor_to_step(16, 5)
            15
            >>> floor_to_step(1.2345, 0.01)
            1.23
            >>> floor_to_step(-1.23, 0.1)
            -1.3
            >>> floor_to_step(100, 25)
            100

        """
        if step <= 0:
            raise ValueError("step must be > 0")
        result = math.floor(value / step) * step
        digits = abs(Decimal(str(step)).as_tuple().exponent)  # type: ignore
        return round(result, digits)

    @staticmethod
    def _floor_round(value: float, digits: int) -> float:
        """Округляет число вниз до указанного количества знаков после запятой."""
        factor = 10**digits
        return math.floor(value * factor) / factor

    @classmethod
    def _handle_key_error(cls, exception: KeyError, symbol: str) -> None:
        """Обрабатывает KeyError при получении информации о тикере."""
        cls._check_loaded()
        raise KeyError(f"Symbol {symbol} not found") from exception

    @classmethod
    def _check_loaded(cls) -> None:
        """Проверяет, загружены ли данные об обмене."""
        if not cls._loaded:
            raise ValueError("Exchange data not loaded") from None
