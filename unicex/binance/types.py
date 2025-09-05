from typing import Literal

type SpotTimeframe = Literal[
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]
"""Возможные интервалы для запросов исторических данных на споте."""

type FuturesTimeframe = Literal[
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]
"""Возможные интервалы для запросов исторических данных на фьючерсах."""

type Side = Literal["BUY", "SELL"]
"""Возможные стороны для торговли."""

type OrderType = Literal[
    "LIMIT",
    "MARKET",
    "STOP_LOSS",
    "STOP_LOSS_LIMIT",
    "TAKE_PROFIT",
    "TAKE_PROFIT_LIMIT",
    "LIMIT_MAKER",
]
"""Возможные типы ордеров."""

type NewOrderRespType = Literal["ACK", "RESULT", "FULL"]
"""Возможные типы ответов на запросы создания ордеров."""

type TimeInForce = Literal["GTC", "IOC", "FOK"]
"""Возможные типы действия ордера."""

type SelfTradePreventionMode = Literal["EXPIRE_TAKER", "EXPIRE_MAKER", "EXPIRE_BOTH"]
"""Возможные режимы предотвращения самообмена."""
