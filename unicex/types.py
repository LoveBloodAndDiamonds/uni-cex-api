"""Модуль, который предоставляет типы данных для работы с библиотекой."""

__all__ = [
    "TickerDailyDict",
    "TickerDailyItem",
    "KlineDict",
    "TradeDict",
    "AggTradeDict",
    "RequestMethod",
    "LoggerLike",
    "AccountType",
    "OpenInterestDict",
    "OpenInterestItem",
]

from logging import Logger as LoggingLogger
from typing import Literal, TypedDict

import loguru

type LoggerLike = LoggingLogger | loguru.Logger
"""Объединение логгеров: loguru._logger.Logger или logging.Logger."""

type RequestMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
"""Типы методов HTTP запросов."""


class TickerDailyItem(TypedDict):
    """Статистика одного тикера за последние 24 часа."""

    p: float
    """Изменение цены за 24 ч."""

    v: float
    """Объем торгов за 24 ч. в монетах."""

    q: float
    """Объем торгов за 24 ч. в долларах."""


type TickerDailyDict = dict[str, TickerDailyItem]
"""Статистика тикеров за последние 24 часа."""


class KlineDict(TypedDict):
    """Модель свечи."""

    s: str
    """Символ."""

    t: int
    """Время открытия. В миллисекундах."""

    o: float
    """Цена открытия свечи."""

    h: float
    """Верхняя точка свечи."""

    l: float  # noqa
    """Нижняя точка свечи."""

    c: float
    """Цена закрытия свечи."""

    v: float
    """Объем свечи. В монетах."""

    q: float
    """Объем свечи. В долларах."""

    T: int | None
    """Время закрытия. В миллисекундах."""

    x: bool | None
    """Флаг закрыта ли свеча."""


class TradeDict(TypedDict):
    """Модель сделки."""

    t: int
    """Время сделки. В миллисекундах."""

    s: str
    """Символ."""

    S: Literal["BUY", "SELL"]
    """Направление сделки."""

    p: float
    """Цена сделки."""

    v: float
    """Объем сделки. В монетах."""


class AggTradeDict(TradeDict):
    """Модель агрегированной сделки."""

    pass


class OpenInterestItem(TypedDict):
    """Модель одного элемента открытого интереса."""

    t: int
    """Время. В миллисекундах."""

    v: float
    """Открытый интерес. В монетах."""


type OpenInterestDict = dict[str, OpenInterestItem]
"""Модель открытого интереса."""


type AccountType = Literal["SPOT", "FUTURES"]
"""Тип аккаунта."""
