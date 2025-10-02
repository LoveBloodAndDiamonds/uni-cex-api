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
    """Адаптер для унификации данных с Mexc API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        return [item["symbol"] for item in raw_data if only_usdt or item["symbol"].endswith("USDT")]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        return [
            item["symbol"]
            for item in raw_data["data"]
            if only_usdt or item["symbol"].endswith("USDT")
        ]

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: dict) -> dict[str, float]:
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["data"]}

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        return {
            item["symbol"]: TickerDailyItem(
                p=round(float(item["priceChangePercent"]) * 100, 2),  # Конвертируем в проценты
                v=float(item["volume"]),
                q=float(item["quoteVolume"]),
            )
            for item in raw_data
        }

    @staticmethod
    def futures_ticker_24hr(raw_data: dict) -> TickerDailyDict:
        return {
            item["symbol"]: TickerDailyItem(
                p=float(item["riseFallRate"]) * 100,
                v=float(item["volume24"]),
                q=float(item["amount24"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        return {
            item["symbol"]: OpenInterestItem(t=item["timestamp"], v=float(item["holdVol"]))
            for item in raw_data["data"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        return {item["symbol"]: float(item["fundingRate"]) * 100 for item in raw_data["data"]}

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        return [
            KlineDict(
                s=symbol,
                t=kline[0],
                o=kline[1],
                h=kline[2],
                l=kline[3],
                c=kline[4],
                v=kline[5],
                q=kline[7],
                T=kline[6],
                x=None,
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x[0]),  # Bitget присылает пачку трейдов в обратном порядке
            )
        ]

    @staticmethod
    def futures_klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        # Пример raw_data:
        # {
        #     "success": true,
        #     "code": 0,
        #     "data": {
        #         "time": [
        #             1609740600
        #         ],
        #         "open": [
        #             33016.5
        #         ],
        #         "close": [
        #             33040.5
        #         ],
        #         "high": [
        #             33094.0
        #         ],
        #         "low": [
        #             32995.0
        #         ],
        #         "vol": [
        #             67332.0
        #         ],
        #         "amount": [
        #             222515.85925
        #         ]
        #     }
        # }
        pass
