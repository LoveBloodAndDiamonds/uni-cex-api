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
    """Адаптер для унификации данных с Bybit API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        return [
            item["symbol"]
            for item in raw_data["result"]["list"]
            if only_usdt or item["symbol"].endswith("USDT")
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
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
        return {
            item["symbol"]: OpenInterestItem(
                t=raw_data["time"],
                v=float(item["openInterest"]),
            )
            for item in raw_data["result"]["list"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        return {
            item["symbol"]: float(item["fundingRate"] * 100) for item in raw_data["result"]["list"]
        }

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["result"]["list"]}

    @staticmethod
    def kline(raw_data: dict) -> list[KlineDict]:
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
