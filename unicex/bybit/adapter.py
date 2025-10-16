__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
    KlineDict,
    LiquidationDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Bybit API."""

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
            for item in raw_data["result"]["list"]
            if item["symbol"].endswith("USDT") or not only_usdt
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
                p=round(float(item["price24hPcnt"]) * 100, 2),
                v=float(item["volume24h"]),
                q=float(item["turnover24h"]),
            )
            for item in raw_data["result"]["list"]
        }

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь, где ключ - тикер, а значение - агрегированные данные открытого интереса.
        """
        return {
            item["symbol"]: OpenInterestItem(
                t=raw_data["time"],
                v=float(item["openInterest"]),
            )
            for item in raw_data["result"]["list"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        return {
            item["symbol"]: float(item["fundingRate"]) * 100
            for item in raw_data["result"]["list"]
            if item["fundingRate"]
        }

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последней цене, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["result"]["list"]}

    @staticmethod
    def klines(raw_data: dict) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s=raw_data["result"]["symbol"],
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
                raw_data["result"]["list"],
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def Klines_message(raw_msg: Any) -> list[KlineDict]:
        """Преобразует вебсокет-сообщение с данными о свечах в унифицированный формат.

        Параметры:
        raw_msg (`Any`): Сырое сообщение из вебсокета Bybit.

        Возвращает:
          `list[KlineDict]`: Список свечей в унифицированном формате.
        """
        symbol = raw_msg["topic"].split(".")[-1]
        return [
            KlineDict(
                s=symbol,
                t=kline["start"],
                o=float(kline["open"]),
                h=float(kline["high"]),
                l=float(kline["low"]),
                c=float(kline["close"]),
                v=float(kline["volume"]),
                q=float(kline["turnover"]),
                T=kline["end"],
                x=kline["confirm"],
            )
            for kline in sorted(
                raw_msg["data"],
                key=lambda x: int(x["start"]),
            )
        ]

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        """Преобразует вебсокет-сообщение с данными о сделках в унифицированный формат.

        Параметры:
        raw_msg (`Any`): Сырое сообщение из вебсокета Bybit.

        Возвращает:
          `list[TradeDict]`: Список сделок в унифицированном формате.
        """
        return [
            TradeDict(
                t=trade["T"],
                s=trade["s"],
                S=trade["S"].upper(),
                p=float(trade["p"]),
                v=float(trade["v"]),
            )
            for trade in sorted(
                raw_msg["data"],
                key=lambda x: int(x["T"]),
            )
        ]

    @staticmethod
    def liquidations_message(raw_msg: Any) -> list[LiquidationDict]:
        """Преобразует вебсокет-сообщение с данными о ликвидациях в унифицированный формат.

        Параметры:
        raw_msg (`Any`): Сырое сообщение из вебсокета Bybit.

        Возвращает:
          `list[LiquidationDict]`: Список ликвидаций в унифицированном формате.
        """
        return [
            LiquidationDict(
                t=liquidation["T"],
                s=liquidation["s"],
                S=liquidation["S"].upper(),
                v=float(liquidation["v"]),
                p=float(liquidation["p"]),
            )
            for liquidation in sorted(
                raw_msg["data"],
                key=lambda x: int(x["T"]),
            )
        ]
