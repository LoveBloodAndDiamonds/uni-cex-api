__all__ = [
    "percent_greater",
    "percent_less",
]


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
