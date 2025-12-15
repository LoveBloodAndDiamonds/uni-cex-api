__all__ = ["Adapter"]

from typing import Any

from unicex.types import OpenInterestDict, OpenInterestItem, TickerDailyDict, TickerDailyItem
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Kucoin API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"]
            for item in raw_data["data"]["list"]
            if item["symbol"].endswith("USDTM") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return {
            item["symbol"]: TickerDailyItem(
                p=(
                    round((float(item["lastPrice"]) / float(item["open"]) - 1) * 100, 2)
                    if float(item["open"]) != 0
                    else 0.0
                ),
                v=float(item["baseVolume"]),
                q=float(item["quoteVolume"]),
            )
            for item in raw_data["data"]["list"]
        }

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последней цене, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["data"]["list"]}

    @staticmethod
    def open_interest(raw_data: dict[str, Any]) -> OpenInterestDict:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь, где ключ - тикер, а значение - агрегированные данные открытого интереса.
        """
        return {
            item["symbol"]: OpenInterestItem(
                t=item["ts"],
                v=float(item["openInterest"]),
            )
            for item in raw_data["data"]
        }
