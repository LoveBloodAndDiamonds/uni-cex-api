__all__ = [
    "TickerDailyDict",
    "KlineDict",
]

from typing import Literal, TypedDict

type JsonLike = dict | list
type RequestMethod = Literal["GET", "POST", "PUT", "DELETE"]


class TickerDailyDict(TypedDict):
    """Статистика тикера за последние 24 часа."""

    p: float
    """Изменение цены за 24 ч."""

    v: float
    """Объем торгов за 24 ч. в монетах."""

    q: float
    """Объем торгов за 24 ч. в долларах."""


class KlineDict(TypedDict):
    """Модель свечи."""

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

    T: int | None
    """Время закрытия. В миллисекундах."""

    x: bool | None
    """Флаг закрыта ли свеча."""
