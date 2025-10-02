from typing import Any

from unicex.types import (
    AggTradeDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Bitget API."""

    @staticmethod
    def tickers(raw_data: Any, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"]
            for item in raw_data["data"]
            if not only_usdt or item["symbol"].endswith("USDT")
        ]

    @staticmethod
    def ticker_24hr(raw_data: Any) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return {
            item["symbol"]: TickerDailyItem(
                p=round(float(item["change24h"]) * 100, 2),  # конвертируем в проценты
                v=float(item["baseVolume"]),  # объём в COIN
                q=float(item["usdtVolume"]),  # объём в USDT
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def last_price(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["lastPr"]) for item in raw_data["data"]}

    @staticmethod
    def klines(raw_data: Any, symbol: str) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в
        унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            symbol (str): Тикер, для которого нужно преобразовать данные.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
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
                raw_data["data"],
                key=lambda x: int(x[0]),  # Bitget присылает пачку трейдов в обратном порядке
            )
        ]

    @staticmethod
    def funding_rate(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования
        тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        return {item["symbol"]: float(item["fundingRate"]) * 100 for item in raw_data["data"]}

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        symbol = raw_msg["arg"]["instId"]

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
                raw_msg["data"],
                key=lambda x: int(x[0]),  # Bitget присылает пачку трейдов в обратном порядке
            )
        ]

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение вебсокета со сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[TradeDict]: Список сделок в унифицированном формате.
        """
        symbol = raw_msg["arg"]["instId"]

        return [
            AggTradeDict(
                t=int(trade["ts"]),
                s=symbol,
                S=trade["side"].upper(),
                p=float(trade["price"]),
                v=float(trade["size"]),
            )
            for trade in sorted(
                raw_msg["data"],
                key=lambda x: int(x["ts"]),  # Bitget присылает пачку трейдов в обратном порядке
            )
        ]

    @staticmethod
    def open_interest(raw_data: Any) -> OpenInterestDict:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        объеме открытых позиций в унифицированный вид.

        Параметры:
            raw_data (Any): Сырое сообщение с вебсокета.

        Возвращает:
            `OpenInterestDict`: Cловарь, где ключи - название тикера, а значения - объемы открытых позиций в монетах.
        """
        return {
            i["symbol"]: OpenInterestItem(
                t=int(i["ts"]),
                v=float(i["holdingAmount"]),
            )
            for i in raw_data["data"]
        }
