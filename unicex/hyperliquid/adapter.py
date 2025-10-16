__all__ = ["Adapter"]

import time

from unicex.types import (
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
)

# from unicex.utils import catch_adapter_errors, decorate_all_methods
from .exchange_info import ExchangeInfo


# @decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Hyperliquid API."""

    @staticmethod
    def tickers(raw_data: dict, resolve_symbols: bool) -> list[str]:
        """Преобразует данные Hyperliquid в список спотовых тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            list[str]: Список тикеров (например, "@123").
        """
        if resolve_symbols:
            return [ExchangeInfo.resolve_spot_symbol(item["name"]) for item in raw_data["universe"]]
        else:
            return [item["name"] for item in raw_data["universe"]]

    @staticmethod
    def futures_tickers(raw_data: dict) -> list[str]:
        """Преобразует данные Hyperliquid в список фьючерсных тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[str]: Список тикеров (например, "@123").
        """
        return [item["name"] for item in raw_data["universe"]]

    @staticmethod
    def last_price(raw_data: dict, resolve_symbols: bool) -> dict[str, float]:
        """Преобразует данные о последних ценах (spot) в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        if resolve_symbols:
            return {
                ExchangeInfo.resolve_spot_symbol(token): float(price)
                for token, price in raw_data.items()
                if token.startswith("@")
            }
        else:
            return {
                token: float(price) for token, price in raw_data.items() if token.startswith("@")
            }

    @staticmethod
    def futures_last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует данные о последних ценах (futures) в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        return {k: float(v) for k, v in raw_data.items() if not k.startswith("@")}

    @staticmethod
    def ticker_24hr(raw_data: list, resolve_symbols: bool) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (spot) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, тикеры маппятся из вида "@123" в "BTC".

        Возвращает:
            TickerDailyDict: Словарь тикеров и их статистики.
        """
        metrics = raw_data[1]
        result: TickerDailyDict = {}

        for item in metrics:
            try:
                coin = item["coin"]

                if resolve_symbols:
                    coin = ExchangeInfo.resolve_spot_symbol(coin) or coin

                prev_day_px = float(item.get("prevDayPx") or "0")
                mid_px = float(item.get("midPx") or "0")
                mark_px = float(item.get("markPx") or "0")
                day_ntl_vlm = float(item.get("dayNtlVlm") or "0")

                p = round(((mark_px - prev_day_px) / prev_day_px * 100), 2) if prev_day_px else 0.0
                v = (day_ntl_vlm / mid_px) if mid_px else 0.0
                q = day_ntl_vlm

                if coin in result:
                    # В случае с конфликтом оставляем ту монету, в которой больше дневного объема, т.к
                    # для 6 монет (на 07.10.2025) встречаются пары к USDH, которые повторяют идентификатор.
                    # Проблема не критичная - т.к. флаг resolve_symbols по идее использовать должен редко.
                    prev_ticker_daily = result[coin]
                    curr_ticker_daily = TickerDailyItem(p=p, v=v, q=q)
                    if prev_ticker_daily["q"] > curr_ticker_daily["q"]:
                        result[coin] = prev_ticker_daily
                    else:
                        result[coin] = curr_ticker_daily
                else:
                    result[coin] = TickerDailyItem(p=p, v=v, q=q)

            except (KeyError, TypeError, ValueError):
                continue

        return result

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

        result: TickerDailyDict = {}

        for i, item in enumerate(metrics):
            try:
                prev_day_px = float(item.get("prevDayPx", 0) or "0")
                oracle_px = float(item.get("oraclePx", 0) or "0")
                mark_px = float(item.get("markPx", 0) or "0")
                day_ntl_vlm = float(item.get("dayNtlVlm", 0) or "0")

                p = ((mark_px - prev_day_px) / prev_day_px * 100) if prev_day_px else 0.0
                v = (day_ntl_vlm / oracle_px) if oracle_px else 0.0
                q = day_ntl_vlm

                result[universe[i]["name"]] = TickerDailyItem(p=p, v=v, q=q)
            except (KeyError, TypeError, ValueError):
                continue

        return result

    @staticmethod
    def klines(raw_data: list[dict], resolve_symbols: bool) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, тикер маппится из вида "@123" в "BTC".

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s=kline["s"]
                if not resolve_symbols
                else ExchangeInfo.resolve_spot_symbol(kline["s"]),
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["v"]) * float(kline["c"]),
                T=kline["T"],
                x=None,
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x["t"]),
            )
        ]

    @staticmethod
    def futures_klines(raw_data: list[dict]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s=kline["s"],
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["v"]) * float(kline["c"]),
                T=kline["T"],
                x=None,
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x["t"]),
            )
        ]

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
