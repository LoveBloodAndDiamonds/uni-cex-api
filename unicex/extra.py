"""Модуль, который предоставляет дополнительные функции, которые могут пригодиться в работе."""

__all__ = [
    "percent_greater",
    "percent_less",
    "TimeoutTracker",
    "generate_ex_link",
    "generate_tv_link",
    "generate_cg_link",
]

import time

from .enums import Exchange, MarketType
from .exceptions import NotSupported


def percent_greater(higher: float, lower: float) -> float:
    """Возвращает на сколько процентов `higher` больше `lower`.

    Можно воспринимать полученное значение как если вести линейку на tradingview.com от меньшего значения к большему.

    Например:
        ```python
        percent_greater(120, 100)
        >> 20.0
        ```

    Возвращает:
        `float`: На сколько процентов `higher` больше `lower`.
    """
    if lower == 0:
        return float("inf")
    return (higher / lower - 1) * 100


def percent_less(higher: float, lower: float) -> float:
    """Возвращает на сколько процентов `lower` меньше `higher`.

    Можно воспринимать полученное значение как если вести линейку на tradingview.com от большего значения к меньшему.

    Например:
        ```python
        percent_less(120, 100)
        >> 16.67777777777777
        ```

    Возвращает:
        `float`: На сколько процентов `lower` меньше `higher`.
    """
    if lower == 0:
        return float("inf")
    return (1 - lower / higher) * 100


class TimeoutTracker[T]:
    """Универсальный менеджер для управления таймаутами любых объектов.
    Позволяет временно блокировать объекты на заданный промежуток времени.
    """

    def __init__(self) -> None:
        """Инициализирует пустой словарь для отслеживания заблокированных объектов."""
        self._blocked_items: dict[T, float] = {}

    def is_blocked(self, item: T) -> bool:
        """Проверяет, находится ли объект в состоянии блокировки.
        Если срок блокировки истёк, удаляет объект из списка.

        Параметры:
            item (`T`): Объект, который нужно проверить.

        Возвращает:
            `bool`: True, если объект заблокирован, иначе False.
        """
        if item in self._blocked_items:
            if time.time() < self._blocked_items[item]:
                return True
            else:
                del self._blocked_items[item]
        return False

    def block(self, item: T, duration: int) -> None:
        """Блокирует объект на указанное количество секунд.

        Параметры:
            item (`T`): Объект, который нужно заблокировать.
            duration (`int`): Длительность блокировки в секундах.
        """
        self._blocked_items[item] = time.time() + duration


def generate_ex_link(exchange: Exchange, market_type: MarketType, symbol: str):
    """Генерирует ссылку на биржу.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка на биржу.
    """
    ticker = symbol.removesuffix("USDT").removesuffix("_USDT").removesuffix("-USDT")
    if exchange == Exchange.BINANCE:
        if market_type == MarketType.FUTURES:
            return f"https://www.binance.com/en/futures/{symbol}"
        else:
            return f"https://www.binance.com/en/trade/{ticker}_USDT?type=spot"
    elif exchange == Exchange.BYBIT:
        if market_type == MarketType.FUTURES:
            return f"https://www.bybit.com/trade/usdt/{symbol}"
        else:
            return f"https://www.bybit.com/en/trade/spot/{ticker}/USDT"
    elif exchange == Exchange.BITGET:
        if market_type == MarketType.FUTURES:
            return f"https://www.bitget.com/ru/futures/usdt/{symbol}"
        else:
            return f"https://www.bitget.com/ru/spot/{symbol}"
    else:
        raise NotSupported(f"Exchange {exchange} is not supported")


def generate_tv_link(exchange: Exchange, market_type: MarketType, symbol: str) -> str:
    """Генерирует ссылку для TradingView.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка для TradingView.
    """
    if market_type == MarketType.FUTURES:
        return f"https://www.tradingview.com/chart/?symbol={exchange}:{symbol}.P"
    elif market_type == MarketType.SPOT:
        return f"https://www.tradingview.com/chart/?symbol={exchange}:{symbol}"
    else:
        raise NotSupported(f"Unsupported market type: {market_type}")


def generate_cg_link(exchange: Exchange, market_type: MarketType, symbol: str) -> str:
    """Генерирует ссылку для CoinGlass.

    Параметры:
        exchange (`Exchange`): Биржа.
        market_type (`MarketType`): Тип рынка.
        symbol (`str`): Символ.

    Возвращает:
        `str`: Ссылка для CoinGlass.
    """
    if market_type == MarketType.FUTURES:
        if exchange == Exchange.BITGET:
            # https://www.coinglass.com/tv/ru/Bitget_ETHUSDT_UMCBL
            return f"https://www.coinglass.com/tv/ru/{exchange.capitalize()}_{symbol}_UMCBL"
        else:
            # Стандартный вид ссылки (Подходит для BYBIT и BINANCE)
            return f"https://www.coinglass.com/tv/ru/{exchange.capitalize()}_{symbol}"
    elif market_type == MarketType.SPOT:
        if exchange == Exchange.BITGET:
            # Для спота нет ссылки на койнгласс
            return f"https://www.coinglass.com/tv/ru/{exchange.capitalize()}_{symbol}_UMCBL"
        else:
            # Стандартный вид ссылки (Подходит для BYBIT и BINANCE)
            return f"https://www.coinglass.com/tv/ru/SPOT_{exchange.capitalize()}_{symbol}"
    else:
        raise NotSupported(f"Market type {market_type} is not supported")
