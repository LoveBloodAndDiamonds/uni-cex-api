from typing import Literal

ProductType = Literal["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"]
"""Тип рынков фьючерсов."""

Side = Literal["buy", "sell"]
"""Сторона сделки."""

OrderType = Literal["limit", "market"]
"""Тип ордера."""

TimeInForce = Literal["gtc", "ioc", "fok", "post_only"]
"""Политика исполнения ордера."""

MarginMode = Literal["crossed", "isolated"]
"""Режим маржи."""
