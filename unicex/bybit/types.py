from typing import Literal

type SpotTimeframe = Literal[
    "1",
    "3",
    "5",
    "15",
    "30",
    "60",
    "120",
    "240",
    "360",
    "720",
    "D",
    "W",
    "M",
]
"""Возможные интервалы для запросов исторических данных на споте."""

type FuturesTimeframe = SpotTimeframe
"""Возможные интервалы для запросов исторических данных на фьючерсах. Такие же как для спота."""

type ProductType = Literal["linear", "inverse", "spot", "options"]
"""Возможные типы рынков."""

type FuturesProductType = Literal["linear", "inverse"]
"""Возможные типы фьючерсных рынков."""

type Side = Literal["Buy", "Sell"]
"""Возможные стороны для торговли."""

type OrderType = Literal["Market", "Limit"]
"""Возможные типы ордеров."""
