__all__ = ["Adapter"]


from unicex.types import TickerDailyDict, TickerDailyItem
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
    def open_inerest(raw_data: dict) -> dict[str, float]:
        return {item["symbol"]: float(item["openInterest"]) for item in raw_data["result"]["list"]}

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        return {
            item["symbol"]: float(item["fundingRate"] * 100) for item in raw_data["result"]["list"]
        }
