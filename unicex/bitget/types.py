from typing import Literal

BusinessType = Literal["mix", "spot"]
"""Тип торговой линии (контракты / спот)."""

MergeDepthPrecision = Literal["scale0", "scale1", "scale2", "scale3", "scale4", "scale5"]
"""Точность стакана (объединение по цене)."""

MergeDepthLimit = Literal["1", "5", "15", "50", "max"]
"""Лимит объединения стакана."""

OrderbookDepthType = Literal["step0", "step1", "step2", "step3", "step4", "step5"]
"""Тип стакана (объединение по цене)."""

SpotGranularity = Literal[
    "1min",
    "3min",
    "5min",
    "15min",
    "30min",
    "1h",
    "4h",
    "6h",
    "12h",
    "1day",
    "3day",
    "1week",
    "1M",
    "6Hutc",
    "12Hutc",
    "1Dutc",
    "3Dutc",
    "1Wutc",
    "1Mutc",
]
"""Таймфрейм (granularity) для свечей."""

KlineType = Literal["market", "index"]
"""Тип свечей."""

ProductType = Literal["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"]
"""Тип рынков фьючерсов."""

Side = Literal["buy", "sell"]
"""Сторона сделки."""

OrderType = Literal["limit", "market"]
"""Тип ордера."""

TimeInForce = Literal["gtc", "ioc", "fok", "post_only"]
"""Политика исполнения ордера."""

TpslType = Literal["normal", "tpsl"]
"""Тип ордера тейк-профит/стоп-лосс."""

StpMode = Literal["none", "cancel_taker", "cancel_maker", "cancel_both"]
"""Режим стоп-тейк (Self Trade Prevention)."""

BatchMode = Literal["single", "multiple"]
"""Режим батч ордеров."""

PlanType = Literal["amount", "total"]
"""Тип отложенного ордера."""

TriggerType = Literal["fill_price", "mark_price"]
"""Триггер для срабатывания отложенного ордера."""

AssetType = Literal["hold_only", "all"]
"""Тип активов."""

MarginMode = Literal["crossed", "isolated"]
"""Режим маржи."""
