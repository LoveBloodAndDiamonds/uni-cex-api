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
    "BestBidAskItem",
    "BestBidAskDict",
    "BookDepthDict",
    "OrderIdDict",
    "PositionInfoDict",
    "FundingInfoItem",
    "FundingInfoDict",
]

from logging import Logger as LoggingLogger
from typing import Literal, NotRequired, TypedDict

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


class BestBidAskItem(TypedDict):
    """Модель одного элемента лучшего бида и аска."""

    s: str
    """Символ."""

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


type BestBidAskDict = dict[str, BestBidAskItem]
"""Модель лучших бидов и асков."""


class BookDepthDict(TypedDict):
    """Модель обновления ближайших N асков и бидов через вебсокет."""

    s: str
    """Символ."""

    t: int
    """Время события в миллисекундах."""

    u: int
    """Айди обновления."""

    a: list[tuple[float, float]]  # price, quantity
    """Лучшие аски (те, кто продает, выше в стакане)
    в порядке удаления от спреда. Два значения: цена и объем."""

    b: list[tuple[float, float]]  # price, quantity
    """Лучшие биды (те, кто покупают, ниже в стакане)
    в порядке удаления от спреда. Два значения: цена и объем."""


class OrderIdDict(TypedDict):
    """Базовая информация о айди ордера."""

    t: int
    """Время события в миллисекундах."""

    id: str
    """Айди ордера."""

    cloid: str
    """Клиентский айди ордера."""


class PositionInfoDict(TypedDict):
    """Информация о позиции."""

    t: int
    """Время ответа в миллисекундах."""

    symbol: str  # "" if position is not opened
    """Торговая пара."""

    side: Literal["BUY", "SELL", ""]  # "" if position is not opened
    """Направление позиции."""

    quantity: float  # 0 if position is not opened
    """Объем позиции в монетах."""

    entry_price: float  # 0 if position is not opened
    """Средняя цена входа в позицию."""

    mark_price: float  # 0 if position is not opened
    """Цена маркировки на тикере."""

    liquidation_price: float  # 0 if position is not opened
    """Цена ликвидации позиции."""

    unrealized_pnl: float  # 0 if position is not opened
    """Нереализованный PNL."""

    realized_pnl: float  # 0 if position is not opened
    """Реализованный PNL."""

    leverage: float  # 0 if position is not opened
    """Торговое плечо."""

    # Not required attrs for the future updates
    # Supports not on all exchanges

    notional: NotRequired[float]
    """Размер позиции в долларах."""

    breakeven_price: NotRequired[float]
    """Цена безубытка."""


class FundingInfoItem(TypedDict):
    """Полная информация о фандинге для одного тикера."""

    rate: float
    """Текущая ставка фандинга в процентах."""

    interval: int
    """Интервал списания фандинга в часах."""

    next_time: int
    """Время в миллисекундах - время следующего списания."""


type FundingInfoDict = dict[str, FundingInfoItem]
"""Полная информация о фандинге для всех тикеров."""
