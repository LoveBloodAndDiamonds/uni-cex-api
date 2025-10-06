__all__ = ["IExchangeInfo"]

import asyncio
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING

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
    @abstractmethod
    async def _load_exchange_info(cls) -> None:
        """Загружает информацию о бирже."""
        ...

    @classmethod
    def round_price(
        cls, symbol: str, price: float, market_type: MarketType = MarketType.SPOT
    ) -> float:
        """Округляет цену до ближайшего возможного значения."""
        try:
            if market_type == MarketType.SPOT:
                precision = cls._tickers_info[symbol]["tick_precision"]
            else:
                precision = cls._futures_tickers_info[symbol]["tick_precision"]
        except KeyError as e:
            cls._handle_key_error(e, symbol)
        return round(price, precision)

    @classmethod
    def round_quantity(
        cls, symbol: str, quantity: float, market_type: MarketType = MarketType.SPOT
    ) -> float:
        """Округляет объем до ближайшего возможного значения."""
        try:
            if market_type == MarketType.SPOT:
                precision = cls._tickers_info[symbol]["size_precision"]
            else:
                precision = cls._futures_tickers_info[symbol]["size_precision"]
        except KeyError as e:
            cls._handle_key_error(e, symbol)
        return round(quantity, precision)

    @classmethod
    def round_futures_price(cls, symbol: str, price: float) -> float:
        """Округляет цену до ближайшего возможного значения на фьючерсах."""
        return cls.round_price(symbol, price, MarketType.FUTURES)

    @classmethod
    def round_futures_quantity(cls, symbol: str, quantity: float) -> float:
        """Округляет объем до ближайшего возможного значения на фьючерсах."""
        return cls.round_quantity(symbol, quantity, MarketType.FUTURES)

    @staticmethod
    def _step_size_to_precision(tick_size: str | int | float) -> int:
        """Возвращает precision для round(x, precision) по шагу цены/объёма.

        Работает только для шагов — степеней 10.
        Примеры:
            "0.0001" ->  4
            "0.01"   ->  2
            "0.1"    ->  1
            "1"      ->  0
            "10"     -> -1
            "100"    -> -2
        """
        d = Decimal(str(tick_size)).normalize()
        if d <= 0:
            raise ValueError("tick_size must be > 0")

        t = d.as_tuple()
        # Степень десяти даёт один значащий разряд = 1 (1eN)
        if t.digits == (1,):
            return -t.exponent  # type: ignore

        # Иначе это не степень 10 (например, 0.5, 5 и т.п.)
        raise ValueError(
            f"tick_size={tick_size} is not a power of 10; cannot map to round() precision."
        )

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
