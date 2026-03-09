__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
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
        return [
            item["symbol"] for item in raw_data if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
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
        return {item["symbol"]: float(item["price"]) for item in raw_data}

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
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
        return {item["symbol"]: float(item["lastFundingRate"]) * 100 for item in raw_data}

    @staticmethod
    def funding_interval(raw_data: list[dict]) -> dict[str, int]:
        return {item["symbol"]: int(item["fundingIntervalHours"]) for item in raw_data}

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        # В ответе нет времени, поэтому используем текущее.
        timestamp = get_timestamp()
        return {
            item["symbol"]: OpenInterestItem(
                t=timestamp,
                v=float(item["openInterest"]) / float(item["lastPrice"]),
                u="coins",
            )
            for item in raw_data.get("data", [])
        }

    @staticmethod
    def futures_best_bid_ask(raw_data: list[dict]) -> BestBidAskDict:
        return {
            item["symbol"]: BestBidAskItem(
                s=item["symbol"],
                t=int(item["time"]),
                u=0,  # REST endpoint не возвращает update id
                b=float(item["bidPrice"]),
                B=float(item["bidQty"]),
                a=float(item["askPrice"]),
                A=float(item["askQty"]),
            )
            for item in raw_data
        }

    @staticmethod
    def futures_depth(raw_data: dict, symbol: str) -> BookDepthDict:
        return BookDepthDict(
            s=symbol,
            t=int(raw_data["E"]),
            u=int(raw_data["lastUpdateId"]),
            b=[(float(price), float(quantity)) for price, quantity in raw_data["bids"]],
            a=[(float(price), float(quantity)) for price, quantity in raw_data["asks"]],
        )

    @staticmethod
    def Klines_message(raw_msg: Any) -> list[KlineDict]:
        kline = raw_msg.get("data", raw_msg)["k"]  # Чтобы корректно обрабатывать multiplex стримы
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
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        data = raw_msg.get("data", raw_msg)  # Чтобы корректно обрабатывать multiplex стримы
        return [
            TradeDict(
                t=data["T"],
                s=data["s"],
                S="SELL" if data["m"] else "BUY",
                p=float(data["p"]),
                v=float(data["q"]),
            )
        ]

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: Any) -> list[BestBidAskItem]:
        data = raw_msg.get("data", raw_msg)
        return [
            BestBidAskItem(
                s=str(data["s"]),
                t=int(data["E"]),
                u=int(data["u"]),
                b=float(data["b"]),
                B=float(data["B"]),
                a=float(data["a"]),
                A=float(data["A"]),
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message(raw_msg: Any) -> list[BookDepthDict]:
        data = raw_msg.get("data", raw_msg)
        return [
            BookDepthDict(
                s=str(data["s"]),
                t=int(data["E"]),
                u=int(data["u"]),
                b=[(float(price), float(quantity)) for price, quantity in data["b"]],
                a=[(float(price), float(quantity)) for price, quantity in data["a"]],
            )
        ]
