__all__ = ["Adapter"]


from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    LiquidationDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Binance API."""

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
                q=float(item["quoteVolume"]),  # объём в долларах
                v=float(item["volume"]),  # объём в монетах
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
            for kline in sorted(
                raw_data,
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        return {item["symbol"]: float(item["lastFundingRate"]) * 100 for item in raw_data}

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestItem:
        return OpenInterestItem(
            t=raw_data["time"],
            v=float(raw_data["openInterest"]),
            u="coins",
        )

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
    def klines_message(raw_msg: dict) -> list[KlineDict]:
        # Обрабатываем обертку в случае с multiplex stream
        kline = raw_msg.get("data", raw_msg)["k"]
        return [
            KlineDict(
                s=kline["s"],
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),  # Используем quote volume (в USDT)
                q=float(kline["q"]),  # Используем quote volume (в USDT)
                T=kline["T"],
                x=kline["x"],
            )
        ]

    @staticmethod
    def trades_message(raw_msg: dict) -> list[TradeDict]:
        msg = raw_msg.get("data", raw_msg)
        return [
            TradeDict(
                t=int(msg["T"]),
                s=str(msg["s"]),
                S="SELL" if bool(msg["m"]) else "BUY",
                p=float(msg["p"]),
                v=float(msg["q"]),
            )
        ]

    @staticmethod
    def liquidations_message(raw_msg: dict) -> list[LiquidationDict]:
        msg = raw_msg.get("data", raw_msg)
        liquidation = msg["o"]

        return [
            LiquidationDict(
                t=int(liquidation["T"]),
                s=str(liquidation["s"]),
                S="SHORT" if str(liquidation["S"]) == "BUY" else "LONG",
                v=float(liquidation["q"]),
                p=float(liquidation["ap"]),
            )
        ]

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: dict) -> list[BestBidAskItem]:
        msg = raw_msg.get("data", raw_msg)

        return [
            BestBidAskItem(
                s=msg["s"],
                t=int(msg["E"]),
                u=int(msg["u"]),
                b=float(msg["b"]),
                B=float(msg["B"]),
                a=float(msg["a"]),
                A=float(msg["A"]),
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message(raw_msg: dict) -> list[BookDepthDict]:
        msg = raw_msg.get("data", raw_msg)

        return [
            BookDepthDict(
                s=msg["s"],
                t=int(msg["E"]),
                u=int(msg["u"]),
                b=[(float(price), float(quantity)) for price, quantity in msg["b"]],
                a=[(float(price), float(quantity)) for price, quantity in msg["a"]],
            )
        ]
