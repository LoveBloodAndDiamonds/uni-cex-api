from typing import Any

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    PositionInfoDict,
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
        return [
            item["symbol"]
            for item in raw_data["data"]
            if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: Any) -> TickerDailyDict:
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
        return {item["symbol"]: float(item["lastPr"]) for item in raw_data["data"]}

    @staticmethod
    def klines(raw_data: Any, symbol: str) -> list[KlineDict]:
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
        return {item["symbol"]: float(item["fundingRate"]) * 100 for item in raw_data["data"]}

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
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
        symbol = raw_msg["arg"]["instId"]

        return [
            TradeDict(
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
        return {
            i["symbol"]: OpenInterestItem(
                t=int(i["ts"]),
                v=float(i["holdingAmount"]),
                u="coins",
            )
            for i in raw_data["data"]
        }

    @staticmethod
    def futures_best_bid_ask(raw_data: Any) -> BestBidAskDict:
        return {
            item["symbol"]: BestBidAskItem(
                s=item["symbol"],
                t=int(item["ts"]),
                u=0,  # REST endpoint не возвращает update id
                b=float(item["bidPr"]),
                B=float(item["bidSz"]),
                a=float(item["askPr"]),
                A=float(item["askSz"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def futures_depth(raw_data: Any, symbol: str) -> BookDepthDict:
        data = raw_data["data"]
        return BookDepthDict(
            s=symbol,
            t=int(data["ts"]),
            u=0,  # REST endpoint не возвращает update id
            b=[(float(price), float(quantity)) for price, quantity in data["bids"]],
            a=[(float(price), float(quantity)) for price, quantity in data["asks"]],
        )

    @staticmethod
    def futures_position_info(raw_data: Any) -> PositionInfoDict:
        positions = raw_data["data"]
        if not positions:
            return PositionInfoDict(
                t=raw_data["requestTime"],
                symbol="",
                side="",
                quantity=0,
                entry_price=0,
                mark_price=0,
                liquidation_price=0,
                unrealized_pnl=0,
                realized_pnl=0,
                leverage=0,
            )

        position = positions[0]

        return PositionInfoDict(
            t=int(position["uTime"]),
            symbol=position["symbol"],
            side={"long": "BUY", "short": "SELL"}[position["holdSide"]],  # type: ignore
            quantity=float(position["total"]),
            entry_price=float(position["openPriceAvg"]),
            mark_price=float(position["markPrice"]),
            liquidation_price=float(position["liquidationPrice"]),
            unrealized_pnl=float(position["unrealizedPL"]),
            realized_pnl=float(position["achievedProfits"]) - float(position["deductedFee"]),
            leverage=float(position["leverage"]),
            breakeven_price=float(position["breakEvenPrice"]),
        )

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: Any) -> list[BestBidAskItem]:
        arg = raw_msg["arg"]
        data = raw_msg["data"][0]
        best_bid = data["bids"][0]
        best_ask = data["asks"][0]
        return [
            BestBidAskItem(
                s=arg["instId"],
                t=int(data["ts"]),
                u=int(data["seq"]),
                b=float(best_bid[0]),
                B=float(best_bid[1]),
                a=float(best_ask[0]),
                A=float(best_ask[1]),
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message(raw_msg: Any) -> list[BookDepthDict]:
        data = raw_msg["data"][0]
        return [
            BookDepthDict(
                s=raw_msg["arg"]["instId"],
                t=int(data["ts"]),
                u=int(data["seq"]),
                b=[(float(price), float(quantity)) for price, quantity in data["bids"]],
                a=[(float(price), float(quantity)) for price, quantity in data["asks"]],
            )
        ]
