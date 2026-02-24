"""Модуль, который предоставляет типы данных для работы с библиотекой."""

__all__ = [
    "TickerDailyDict",
    "TickerDailyItem",
    "KlineDict",
    "TradeDict",
    "RequestMethod",
    "LoggerLike",
    "NumberLike",
    "OpenInterestDict",
    "OpenInterestItem",
    "TickerInfoItem",
    "TickersInfoDict",
    "LiquidationDict",
    "BestBidAskDict",
    "PartialBookDepthDict",
]

from logging import Logger as LoggingLogger
from typing import Literal, TypedDict

import loguru

type LoggerLike = LoggingLogger | loguru.Logger
"""Объединение логгеров: loguru._logger.Logger или logging.Logger."""

type RequestMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]
"""Типы методов HTTP запросов."""

type NumberLike = str | int | float
"""
Числовое значение для аргументов API-клиентов.
API бирж принимают числа как str, int или float — значение
передаётся без преобразований и сериализуется HTTP-клиентом.
"""


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

    T: int | None  # `None` means untrackable
    """Время закрытия. В миллисекундах."""

    x: bool | None  # `None` means untrackable
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


class OpenInterestItem(TypedDict):
    """Модель одного элемента открытого интереса."""

    t: int
    """Время. В миллисекундах."""

    v: float
    """Открытый интерес."""

    u: Literal["coins", "usd"]
    """Единица измерения открытого интереса."""


type OpenInterestDict = dict[str, OpenInterestItem]
"""Модель открытого интереса."""


class LiquidationDict(TypedDict):
    """Модель ликвидации."""

    t: int
    """Время. В миллисекундах."""

    s: str
    """Символ."""

    S: Literal["LONG", "SHORT"]
    """Сторона ликвидации."""

    v: float
    """Объем ликвидации. В монетах."""

    p: float
    """Цена ликвидации."""


class TickerInfoItem(TypedDict):
    """Информация о размерах тиков, ступеней цены и множителя контракта (если есть) для тикера.

    На некоторых биржах удобнее делать округление через precisions, на некоторых через step,
    потому что иногда встречаются шаги, которые не являются степенью 10. Поэтому обязательно
    должны быть определены tick_precision ИЛИ tick_step, а так же size_precision ИЛИ size_step.
    """

    tick_precision: int | None
    """Количество знаков после запятой для цены."""

    tick_step: float | None
    """Шаг одного деления для цены."""

    size_precision: int | None
    """Количество знаков после запятой для объема."""

    size_step: float | None
    """Шаг одного деления для объема."""

    contract_size: float | None
    """Множитель контракта (если есть)."""


type TickersInfoDict = dict[str, TickerInfoItem]
"""Информация о размерах тиков, ступеней цены и множителя контракта (если есть) для всех тикеров."""


class BestBidAskDict(TypedDict):
    """Модель обновления лучшего аска и бида через вебсокет."""

    t: int
    """Время события в миллисекундах."""

    u: int
    """Айди обновления."""

    b: float
    """Цена лучшего бида."""

    B: float
    """Объем лучшего бида."""

    a: float
    """Цена лучшего аска."""

    A: float
    """Объем лучшего аска."""


class PartialBookDepthDict(TypedDict):
    """Модель обновления ближайших N асков и бидов через вебсокет."""

    t: int
    """Время события в миллисекундах."""

    u: int
    """Айди обновления."""

    b: list[tuple[float, float]]  # price, quantity
    """Лучшие биды. Два значения: цена и объем."""

    a: list[tuple[float, float]]  # price, quantity
    """Лучшие аски. Два значения: цена и объем."""
