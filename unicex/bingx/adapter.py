__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
    KlineDict,
    LiquidationDict,
    OpenInterestItem,
    TickerDailyDict,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с BingX API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        data = raw_data["data"]
        items = data["symbols"] if isinstance(data, dict) and "symbols" in data else data
        return [
            item["symbol"] for item in items if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        items = raw_data["data"]
        result = {}
        for item in items:
            percent_raw = item["priceChangePercent"]
            percent_str = str(percent_raw).strip()
            if percent_str.endswith("%"):
                percent_str = percent_str[:-1]
            result[item["symbol"]] = {
                "p": float(percent_str),
                "v": float(item["volume"]),
                "q": float(item["quoteVolume"]),
            }
        return result

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestItem:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestItem: Словарь со временем и объемом открытого интереса в монетах.
        """
        item = raw_data["data"]
        return OpenInterestItem(t=int(item["time"]), v=float(item["openInterest"]), u="usd")

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        data = raw_data["data"]
        items = data if isinstance(data, list) else [data]
        result: dict[str, float] = {}
        for item in items:
            if "lastFundingRate" in item:
                result[item["symbol"]] = float(item["lastFundingRate"]) * 100
            elif "fundingRate" in item and item["fundingRate"] != "":
                result[item["symbol"]] = float(item["fundingRate"]) * 100
        return result

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последней цене, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        data = raw_data["data"]
        if isinstance(data, list):
            return {
                item["symbol"]: float(item["lastPrice"] if "lastPrice" in item else item["price"])
                for item in data
            }
        if isinstance(data, dict):
            return {data["symbol"]: float(data["price"])}
        return {}

    @staticmethod
    def klines(raw_data: dict) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        data = raw_data["data"]
        items = data["klines"] if isinstance(data, dict) and "klines" in data else data
        if "symbol" in raw_data:
            symbol = raw_data["symbol"]
        elif isinstance(data, dict) and "symbol" in data:
            symbol = data["symbol"]
        else:
            symbol = ""

        if items and isinstance(items[0], dict):
            return [
                KlineDict(
                    s=symbol,
                    t=int(kline["time"]),
                    o=float(kline["open"]),
                    h=float(kline["high"]),
                    l=float(kline["low"]),
                    c=float(kline["close"]),
                    v=float(kline["volume"]),
                    q=0.0,
                    T=None,
                    x=None,
                )
                for kline in sorted(
                    items,
                    key=lambda x: int(x["time"]),
                )
            ]

        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[5]),
                q=float(kline[7]) if len(kline) > 7 else 0.0,
                T=int(kline[6]) if len(kline) > 6 else None,
                x=None,
            )
            for kline in sorted(
                items,
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def Klines_message(msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        ...

    @staticmethod
    def futures_klines_message(msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        ...

    @staticmethod
    def aggtrades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        ...

    @staticmethod
    def futures_aggtrades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        ...

    @staticmethod
    def trades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        return [
            TradeDict(
                t=int(trade["T"]),
                s=str(trade["s"]),
                S="SELL" if bool(trade["m"]) else "BUY",
                p=float(trade["p"]),
                v=float(trade["q"]),
            )
            for trade in sorted(
                msg["data"],
                key=lambda x: int(x["T"]),
            )
        ]

    @staticmethod
    def futures_trades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        return [
            TradeDict(
                t=int(trade["T"]),
                s=str(trade["s"]),
                S="SELL" if bool(trade["m"]) else "BUY",
                p=float(trade["p"]),
                v=float(trade["q"]),
            )
            for trade in sorted(
                msg["data"],
                key=lambda x: int(x["T"]),
            )
        ]

    @staticmethod
    def liquidations_message(msg: Any) -> list[LiquidationDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        ликвидации/ликвидациях в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[LiquidationDict]: Список словарей, где каждый словарь содержит данные о ликвидации.
        """
        ...
