from __future__ import annotations

import time

__all__ = ["Adapter"]

from unicex.types import (
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Gateio API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ о тикерах в список символов.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре c USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["currency_pair"]
            for item in raw_data
            if not only_usdt or item["currency_pair"].endswith("USDT")
        ]

    @staticmethod
    def futures_tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ о фьючерсных тикерах в список символов.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре c USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["contract"]
            for item in raw_data
            if not only_usdt or item["contract"].endswith("USDT")
        ]

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует данные о последних ценах (spot) в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ — тикер, а значение — последняя цена.
        """
        return {item["currency_pair"]: float(item["last"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует данные о последних ценах (futures) в унифицированный формат."""
        return {item["contract"]: float(item["last"]) for item in raw_data}

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (spot) в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ — тикер, а значение — агрегированная статистика.
        """
        return {
            item["currency_pair"]: TickerDailyItem(
                p=float(item["change_percentage"]),
                v=float(item["base_volume"]),
                q=float(item["quote_volume"]),
            )
            for item in raw_data
        }

    @staticmethod
    def futures_ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (futures) в унифицированный формат."""
        return {
            item["contract"]: TickerDailyItem(
                p=float(item["change_percentage"]),
                v=float(item["volume_24h_base"]),
                q=float(item["volume_24h_quote"]),
            )
            for item in raw_data
        }

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        """Преобразует данные о свечах в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[5]),
                q=float(kline[6]),
                T=None,
                x=None,
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def futures_klines(raw_data: list[dict], symbol: str) -> list[KlineDict]:
        """Преобразует данные о свечах в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
        return [
            KlineDict(
                s=symbol,
                t=int(kline["t"]) * 1000,  # переводим секунды → миллисекунды
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["sum"]),  # "sum" = объем в $ (quote volume)
                T=None,
                x=None,
            )
            for kline in sorted(raw_data, key=lambda x: int(x["t"]))
        ]

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует данные о ставках финансирования в унифицированный формат."""
        return {
            item["contract"]: float(item["funding_rate"]) * 100
            for item in raw_data
            if item.get("funding_rate") is not None
        }

    @staticmethod
    def open_interest(raw_data: list[dict]) -> OpenInterestDict:
        """Преобразует данные об открытом интересе в унифицированный формат."""
        return {
            item["contract"]: OpenInterestItem(
                t=int(time.time() * 1000),
                v=float(item["total_size"]) * float(item["quanto_multiplier"]),
            )
            for item in raw_data
        }
