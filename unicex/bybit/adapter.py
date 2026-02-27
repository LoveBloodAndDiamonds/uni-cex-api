__all__ = ["Adapter"]

from collections.abc import Callable
from typing import Any

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    KlineDict,
    LiquidationDict,
    OpenInterestDict,
    OpenInterestItem,
    PartialBookDepthDict,
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
                u="coins",
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
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
        """Преобразует сырой ответ, в котором содержатся данные о лучших bid/ask фьючерсов в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            BestBidAskDict: Словарь, где ключ - тикер, а значение - лучший бид и аск.
        """
        return {
            item["symbol"]: BestBidAskItem(
                s=item["symbol"],
                t=int(raw_data["time"]),
                u=0,  # REST endpoint не возвращает update id
                b=float(item["bid1Price"]),
                B=float(item["bid1Size"]),
                a=float(item["ask1Price"]),
                A=float(item["ask1Size"]),
            )
            for item in raw_data["result"]["list"]
        }

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
                S="SHORT" if str(liquidation["S"]) == "buy" else "LONG",
                v=float(liquidation["v"]),
                p=float(liquidation["p"]),
            )
            for liquidation in sorted(
                raw_msg["data"],
                key=lambda x: int(x["T"]),
            )
        ]

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: Any) -> list[BestBidAskItem]:
        """Преобразует вебсокет-сообщение с лучшими бидом и аском в унифицированный формат.

        Параметры:
          raw_msg (`Any`): Сырое сообщение из вебсокета Bybit.

        Возвращает:
          `list[BestBidAskDict]`: Список обновлений лучших бидов и асков в унифицированном формате.
        """
        data = raw_msg["data"]
        bid = data["b"][0]
        ask = data["a"][0]
        return [
            BestBidAskItem(
                s=data["s"],
                t=int(raw_msg["ts"]),
                u=int(data["u"]),
                b=float(bid[0]),
                B=float(bid[1]),
                a=float(ask[0]),
                A=float(ask[1]),
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message() -> Callable[[Any], list[PartialBookDepthDict]]:
        """Создает обертку для сборки полного стакана Bybit из snapshot и delta.

        Возвращает:
          `Callable[[Any], list[PartialBookDepthDict]]`: Функция адаптации одного raw-сообщения.
        """
        state: dict[str, dict[str, dict[float, float]]] = {}

        @catch_adapter_errors
        def _wrapper(raw_msg: Any) -> list[PartialBookDepthDict]:
            """Преобразует одно сообщение orderbook с учетом накопленного состояния."""
            data = raw_msg["data"]
            symbol = data["s"]

            symbol_state = state.setdefault(symbol, {"b": {}, "a": {}})
            bids_state = symbol_state["b"]
            asks_state = symbol_state["a"]

            if raw_msg.get("type") == "snapshot":
                bids_state.clear()
                asks_state.clear()

            for raw_price, raw_quantity in data["b"]:
                price = float(raw_price)
                quantity = float(raw_quantity)
                if quantity == 0.0:
                    bids_state.pop(price, None)
                else:
                    bids_state[price] = quantity

            for raw_price, raw_quantity in data["a"]:
                price = float(raw_price)
                quantity = float(raw_quantity)
                if quantity == 0.0:
                    asks_state.pop(price, None)
                else:
                    asks_state[price] = quantity

            return [
                PartialBookDepthDict(
                    s=symbol,
                    t=int(raw_msg["ts"]),
                    u=int(data["u"]),
                    b=sorted(bids_state.items(), key=lambda item: item[0], reverse=True),
                    a=sorted(asks_state.items(), key=lambda item: item[0]),
                )
            ]

        return _wrapper
