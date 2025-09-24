"""Модуль, который описывает перечисления."""

__all__ = [
    "MarketType",
    "Exchange",
    "Timeframe",
    "Side",
]

from enum import StrEnum


class MarketType(StrEnum):
    """Перечисление типов криптовалютных рынков."""

    FUTURES = "FUTURES"
    SPOT = "SPOT"

    def __add__(self, exchange: "Exchange") -> tuple["Exchange", "MarketType"]:
        """Возвращает кортеж из биржи и типа рынка."""
        return exchange, self


class Exchange(StrEnum):
    """Перечисление бирж."""

    BINANCE = "BINANCE"
    BYBIT = "BYBIT"
    BITGET = "BITGET"

    def __add__(self, market_type: "MarketType") -> tuple["Exchange", "MarketType"]:
        """Возвращает кортеж из биржи и типа рынка."""
        return self, market_type


class Side(StrEnum):
    """Перечисление сторон сделки."""

    BUY = "BUY"
    SELL = "SELL"


class Timeframe(StrEnum):
    """Перечисление таймфреймов."""

    MIN_1 = "1m"
    MIN_3 = "3m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"

    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"

    DAY_1 = "1d"
    DAY_3 = "3d"

    WEEK_1 = "1w"

    MONTH_1 = "1M"

    @property
    def mapping(self) -> dict[Exchange, dict["Timeframe", str]]:
        """Возвращает словарь с маппингом таймфреймов для каждой биржи."""
        return {
            Exchange.BINANCE: {
                Timeframe.MIN_1: "1m",
                Timeframe.MIN_3: "3m",
                Timeframe.MIN_5: "5m",
                Timeframe.MIN_15: "15m",
                Timeframe.MIN_30: "30m",
                Timeframe.HOUR_1: "1h",
                Timeframe.HOUR_2: "2h",
                Timeframe.HOUR_4: "4h",
                Timeframe.HOUR_6: "6h",
                Timeframe.HOUR_8: "8h",
                Timeframe.HOUR_12: "12h",
                Timeframe.DAY_1: "1d",
                Timeframe.DAY_3: "3d",
                Timeframe.WEEK_1: "1w",
                Timeframe.MONTH_1: "1M",
            },
            Exchange.BYBIT: {
                Timeframe.MIN_1: "1",
                Timeframe.MIN_3: "3",
                Timeframe.MIN_5: "5",
                Timeframe.MIN_15: "15",
                Timeframe.MIN_30: "30",
                Timeframe.HOUR_1: "60",
                Timeframe.HOUR_2: "120",
                Timeframe.HOUR_4: "240",
                Timeframe.HOUR_6: "360",
                Timeframe.HOUR_12: "720",
                Timeframe.DAY_1: "D",
                Timeframe.WEEK_1: "W",
                Timeframe.MONTH_1: "M",
            },
            Exchange.BITGET: {
                Timeframe.MIN_1: "1m",
                Timeframe.MIN_5: "5m",
                Timeframe.MIN_15: "15m",
                Timeframe.MIN_30: "30m",
                Timeframe.HOUR_1: "1h",
                Timeframe.HOUR_4: "4h",
                Timeframe.HOUR_6: "6h",
                Timeframe.HOUR_12: "12h",
                Timeframe.DAY_1: "1d",
                Timeframe.DAY_3: "3d",
                Timeframe.WEEK_1: "1w",
                Timeframe.MONTH_1: "1M",
            },
        }

    def to_exchange_format(self, exchange: Exchange) -> str:
        """Конвертирует таймфрейм в формат, подходящий для указанной биржи."""
        try:
            return self.mapping[exchange][self]  # noqa
        except KeyError as e:
            raise ValueError(
                f"Timeframe {self.value} is not supported for exchange {exchange.value}"
            ) from e

    @property
    def to_seconds(self) -> int:
        """Возвращает количество секунд для таймфрейма."""
        unit_map = {
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "M": 2592000,
        }  # Условно 30 дней в месяце
        value, unit = int(self.value[:-1]), self.value[-1]
        return value * unit_map[unit]
