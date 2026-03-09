__all__ = ["Adapter"]

from collections.abc import Callable
from typing import Any

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    KlineDict,
    LiquidationDict,
    OpenInterestDict,
    OpenInterestItem,
    OrderIdDict,
    PositionInfoDict,
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
        return [
            item["symbol"]
            for item in raw_data["result"]["list"]
            if item["symbol"].endswith("USDT") or not only_usdt
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
                u="coins",
            )
            for item in raw_data["result"]["list"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        return {
            item["symbol"]: float(item["fundingRate"]) * 100
            for item in raw_data["result"]["list"]
            if item["fundingRate"]
        }

    @staticmethod
    def funding_interval(raw_data: dict) -> dict[str, int]:
        return {
            item["symbol"]: int(item["fundingInterval"]) // 60
            for item in raw_data["result"]["list"]
        }

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["result"]["list"]}

    @staticmethod
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
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
    def futures_depth(raw_data: dict) -> BookDepthDict:
        result = raw_data["result"]
        return BookDepthDict(
            s=result["s"],
            t=int(result["ts"]),
            u=int(result["u"]),
            b=[(float(price), float(quantity)) for price, quantity in result["b"]],
            a=[(float(price), float(quantity)) for price, quantity in result["a"]],
        )

    @staticmethod
    def futures_order_create(raw_data: dict) -> OrderIdDict:
        result = raw_data["result"]
        return OrderIdDict(
            t=int(raw_data["time"]),
            id=result["orderId"],
            cloid=result.get("orderLinkId", "") or "",
        )

    @staticmethod
    def futures_position_info(raw_data: dict) -> PositionInfoDict:
        positions = raw_data["result"]["list"]
        if not positions:
            raise ValueError(f"Positions list are empty: {raw_data}.")

        position = positions[0]

        return PositionInfoDict(
            t=int(position.get("updatedTime") or raw_data["time"]),
            symbol=position["symbol"],
            side=position.get("side", "").upper(),
            quantity=float(position["size"]),
            entry_price=float(position.get("avgPrice") or 0.0),
            mark_price=float(position["markPrice"]),
            liquidation_price=float(position.get("liqPrice") or 0.0),
            unrealized_pnl=float(position.get("unrealisedPnl") or 0.0),
            realized_pnl=float(position.get("curRealisedPnl") or 0.0),
            leverage=float(position["leverage"]),
            notional=float(position.get("positionValue") or 0.0),
            breakeven_price=float(position.get("breakEvenPrice") or 0.0),
        )

    @staticmethod
    def klines(raw_data: dict) -> list[KlineDict]:
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
    def futures_partial_book_depth_message() -> Callable[[Any], list[BookDepthDict]]:
        state: dict[str, dict[str, dict[float, float]]] = {}

        @catch_adapter_errors
        def _wrapper(raw_msg: Any) -> list[BookDepthDict]:
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
                BookDepthDict(
                    s=symbol,
                    t=int(raw_msg["ts"]),
                    u=int(data["u"]),
                    b=sorted(bids_state.items(), key=lambda item: item[0], reverse=True),
                    a=sorted(asks_state.items(), key=lambda item: item[0]),
                )
            ]

        return _wrapper
