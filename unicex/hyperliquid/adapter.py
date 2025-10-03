__all__ = ["Adapter"]

import time

from unicex.types import (
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Hyperliquid API."""

    @staticmethod
    def tickers(raw_data: list) -> list[str]:
        """Преобразует данные Hyperliquid в список спотовых тикеров.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            list[str]: Список тикеров (например, "PURR/USDC").
        """
        raise NotImplementedError()

    @staticmethod
    def futures_tickers(raw_data: list) -> list[str]:
        """Преобразует данные Hyperliquid в список фьючерсных тикеров.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            list[str]: Список тикеров.
        """
        universe = raw_data[0]["universe"]
        return [item["name"] for item in universe]

    @staticmethod
    def last_price(raw_data: list) -> dict[str, float]:
        """Преобразует данные о последних ценах (spot) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_last_price(raw_data: list) -> dict[str, float]:
        """Преобразует данные о последних ценах (futures) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {universe[i]["name"]: float(item["markPx"]) for i, item in enumerate(metrics)}

    @staticmethod
    def ticker_24hr(raw_data: list) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (spot) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь тикеров и их статистики.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_ticker_24hr(raw_data: list) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (futures) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь тикеров и их статистики.
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {
            universe[i]["name"]: TickerDailyItem(
                p=(float(item["markPx"]) - float(item["prevDayPx"]))
                / float(item["prevDayPx"])
                * 100,
                v=float(item["dayNtlVlm"]) / float(item["oraclePx"]),
                q=float(item["dayNtlVlm"]),
            )
            for i, item in enumerate(metrics)
        }

    @staticmethod
    def funding_rate(raw_data: list) -> dict[str, float]:
        """Преобразует данные о ставках финансирования в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и ставок финансирования (в %).
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {
            universe[i]["name"]: float(item["funding"]) * 100
            for i, item in enumerate(metrics)
            if item.get("funding") is not None
        }

    @staticmethod
    def open_interest(raw_data: list) -> OpenInterestDict:
        """Преобразует данные об открытом интересе в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь тикеров и значений открытого интереса.
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {
            universe[i]["name"]: OpenInterestItem(
                t=int(time.time() * 1000),
                v=float(item["openInterest"]),
            )
            for i, item in enumerate(metrics)
        }
