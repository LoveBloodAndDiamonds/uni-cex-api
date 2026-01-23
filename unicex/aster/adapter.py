__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods, get_timestamp


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Aster API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"] for item in raw_data if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return {
            item["symbol"]: TickerDailyItem(
                p=float(item["priceChangePercent"]),
                q=float(item["quoteVolume"]),
                v=float(item["volume"]),
            )
            for item in raw_data
        }

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ с ценами тикеров в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["price"]) for item in raw_data}

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
        return [
            KlineDict(
                s=symbol,
                t=kline[0],
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[5]),
                q=float(kline[7]),
                T=kline[6],
                x=None,
            )
            for kline in sorted(raw_data, key=lambda x: int(x[0]))
        ]

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        return {item["symbol"]: float(item["lastFundingRate"]) * 100 for item in raw_data}

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь, где ключ - тикер, а значение - открытый интерес в USDT.
        """
        # В ответе нет времени, поэтому используем текущее.
        timestamp = get_timestamp()
        return {
            item["symbol"]: OpenInterestItem(
                t=timestamp,
                v=float(item["openInterest"]),
                u="usd",
            )
            for item in raw_data.get("data", [])
        }

    @staticmethod
    def Klines_message(msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        kline = msg.get("data", msg)["k"]
        return [
            KlineDict(
                s=kline["s"],
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["q"]),
                T=kline["T"],
                x=kline["x"],
            )
        ]

    @staticmethod
    def futures_klines_message(msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return Adapter.Klines_message(msg)

    @staticmethod
    def aggtrades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        data = msg.get("data", msg)
        return [
            TradeDict(
                t=int(data["T"]),
                s=str(data["s"]),
                S="SELL" if bool(data["m"]) else "BUY",
                p=float(data["p"]),
                v=float(data["q"]),
            )
        ]

    @staticmethod
    def futures_aggtrades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        return Adapter.aggtrades_message(msg)

    @staticmethod
    def trades_message(msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        data = msg.get("data", msg)
        return [
            TradeDict(
                t=int(data["T"]),
                s=str(data["s"]),
                S="SELL" if bool(data["m"]) else "BUY",
                p=float(data["p"]),
                v=float(data["q"]),
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
        return Adapter.trades_message(msg)
