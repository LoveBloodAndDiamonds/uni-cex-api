__all__ = ["Adapter"]

import time

from loguru import logger

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    BookDepthDict,
    FundingInfoDict,
    FundingInfoItem,
    KlineDict,
    LiquidationDict,
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
    """Адаптер для унификации данных с Binance API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        result = []
        for item in raw_data:
            try:
                if item["symbol"].endswith("USDT") or not only_usdt:
                    result.append(item["symbol"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = TickerDailyItem(
                    p=float(item["priceChangePercent"]),
                    q=float(item["quoteVolume"]),  # объём в долларах
                    v=float(item["volume"]),  # объём в монетах
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = float(item["price"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        result = []
        for kline in sorted(raw_data, key=lambda x: int(x[0])):
            try:
                result.append(
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
                )
            except Exception as e:
                logger.error(f"Item {kline} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = float(item["lastFundingRate"]) * 100
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_interval(raw_data: list[dict]) -> dict[str, int]:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = int(item["fundingIntervalHours"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_next_time(raw_data: list[dict]) -> dict[str, int]:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = int(item["nextFundingTime"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_info(mark_data: list[dict], funding_data: list[dict]) -> FundingInfoDict:
        intervals = {}
        for item in funding_data:
            try:
                intervals[item["symbol"]] = int(item["fundingIntervalHours"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")

        result = {}
        for item in mark_data:
            try:
                result[item["symbol"]] = FundingInfoItem(
                    v=float(item["lastFundingRate"]) * 100,
                    i=intervals.get(item["symbol"], 0),
                    T=int(item["nextFundingTime"]),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestItem:
        return OpenInterestItem(
            t=raw_data["time"],
            v=float(raw_data["openInterest"]),
            u="coins",
        )

    @staticmethod
    def futures_best_bid_ask(raw_data: list[dict]) -> BestBidAskDict:
        result = {}
        for item in raw_data:
            try:
                result[item["symbol"]] = BestBidAskItem(
                    s=item["symbol"],
                    t=int(item["time"]),
                    u=0,  # REST endpoint не возвращает update id
                    b=float(item["bidPrice"]),
                    B=float(item["bidQty"]),
                    a=float(item["askPrice"]),
                    A=float(item["askQty"]),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_depth(raw_data: dict, symbol: str) -> BookDepthDict:
        bids: list[tuple[float, float]] = []
        asks: list[tuple[float, float]] = []
        for price, quantity in raw_data["bids"]:
            try:
                bids.append((float(price), float(quantity)))
            except Exception as e:
                logger.error(f"Item {(price, quantity)} iteration {type(e)} error: {e}")
        for price, quantity in raw_data["asks"]:
            try:
                asks.append((float(price), float(quantity)))
            except Exception as e:
                logger.error(f"Item {(price, quantity)} iteration {type(e)} error: {e}")
        return BookDepthDict(
            s=symbol,
            t=int(raw_data["E"]),
            u=int(raw_data["lastUpdateId"]),
            b=bids,
            a=asks,
        )

    @staticmethod
    def futures_delistings(exchange_info: dict) -> dict[str, int]:
        # Стандартная дата доставки для бессрочных контрактов (4133404800000 = 2100-12-31)
        _PERPETUAL_DELIVERY_DATE = 4133404800000

        now = int(time.time() * 1000)

        result = {}
        for item in exchange_info["symbols"]:
            try:
                symbol = item["symbol"]
                delivery_ts = item["deliveryDate"]

                if not symbol.endswith("USDT"):
                    continue
                if delivery_ts == _PERPETUAL_DELIVERY_DATE or delivery_ts <= now:
                    continue

                result[symbol] = delivery_ts
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")

        return result

    @staticmethod
    def futures_order_create(raw_data: dict) -> OrderIdDict:
        return OrderIdDict(
            t=int(raw_data["updateTime"]),
            id=str(raw_data["orderId"]),
            cloid=str(raw_data.get("clientOrderId", "")),
        )

    @staticmethod
    def futures_position_info(raw_data: list[dict], symbol: str) -> PositionInfoDict:
        position = raw_data[0]
        position_amount = float(position["positionAmt"])
        return PositionInfoDict(
            t=int(position["updateTime"]),
            symbol=position["symbol"],
            side="BUY" if position_amount >= 0 else "SELL",
            quantity=abs(position_amount),
            entry_price=float(position["entryPrice"]),
            mark_price=float(position["markPrice"]),
            liquidation_price=float(position["liquidationPrice"]),
            unrealized_pnl=float(position["unRealizedProfit"]),
            realized_pnl=0,
            leverage=float(position["leverage"]),
            notional=abs(float(position["notional"])),
            breakeven_price=float(position.get("breakEvenPrice", 0)),
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

        bids: list[tuple[float, float]] = []
        asks: list[tuple[float, float]] = []
        for price, quantity in msg["b"]:
            try:
                bids.append((float(price), float(quantity)))
            except Exception as e:
                logger.error(f"Item {(price, quantity)} iteration {type(e)} error: {e}")
        for price, quantity in msg["a"]:
            try:
                asks.append((float(price), float(quantity)))
            except Exception as e:
                logger.error(f"Item {(price, quantity)} iteration {type(e)} error: {e}")

        return [
            BookDepthDict(
                s=msg["s"],
                t=int(msg["E"]),
                u=int(msg["u"]),
                b=bids,
                a=asks,
            )
        ]
