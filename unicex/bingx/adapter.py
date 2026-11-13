__all__ = ["Adapter"]

import time
from typing import Any

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
    TickerDailyDict,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с BingX API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        data = raw_data["data"]
        items = data["symbols"] if isinstance(data, dict) and "symbols" in data else data
        return [
            item["symbol"] for item in items if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        items = raw_data["data"]
        result = {}
        for item in items:
            percent_raw = item["priceChangePercent"]
            percent_str = str(percent_raw).strip()
            if percent_str.endswith("%"):
                percent_str = percent_str[:-1]
            result[item["symbol"]] = {
                "p": float(percent_str),
                "v": float(item["volume"]),
                "q": float(item["quoteVolume"]),
            }
        return result

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestItem:
        item = raw_data["data"]
        return OpenInterestItem(t=int(item["time"]), v=float(item["openInterest"]), u="usd")

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        data = raw_data["data"]
        items = data if isinstance(data, list) else [data]
        result: dict[str, float] = {}
        for item in items:
            if "lastFundingRate" in item:
                result[item["symbol"]] = float(item["lastFundingRate"]) * 100
            elif "fundingRate" in item and item["fundingRate"] != "":
                result[item["symbol"]] = float(item["fundingRate"]) * 100
        return result

    @staticmethod
    def _premium_items(raw_data: dict) -> list[dict]:
        data = raw_data["data"]
        return data if isinstance(data, list) else [data]

    @staticmethod
    def funding_interval(raw_data: dict) -> dict[str, int]:
        result = {}
        for item in Adapter._premium_items(raw_data):
            try:
                result[item["symbol"]] = int(item["fundingIntervalHours"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_next_time(raw_data: dict) -> dict[str, int]:
        result = {}
        for item in Adapter._premium_items(raw_data):
            try:
                result[item["symbol"]] = int(item["nextFundingTime"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_info(raw_data: dict) -> FundingInfoDict:
        result = {}
        for item in Adapter._premium_items(raw_data):
            try:
                result[item["symbol"]] = FundingInfoItem(
                    v=float(item["lastFundingRate"]) * 100,
                    i=int(item.get("fundingIntervalHours") or 0),
                    T=int(item.get("nextFundingTime") or 0),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
        # Без символа — из списка 24h-тикеров, с символом — из bookTicker
        data = raw_data["data"]
        result = {}
        if isinstance(data, dict) and "book_ticker" in data:
            item = data["book_ticker"]
            result[item["symbol"]] = BestBidAskItem(
                s=item["symbol"],
                t=int(item["time"]),
                u=int(item.get("lastUpdateId") or 0),
                b=float(item["bid_price"]),
                B=float(item["bid_qty"]),
                a=float(item["ask_price"]),
                A=float(item["ask_qty"]),
            )
            return result
        for item in data if isinstance(data, list) else [data]:
            try:
                if not (item.get("bidPrice") and item.get("askPrice")):
                    continue
                result[item["symbol"]] = BestBidAskItem(
                    s=item["symbol"],
                    t=int(item["closeTime"]),
                    u=0,
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
        # bids/asks — в монетах (совпадают с bidsCoin/asksCoin)
        data = raw_data["data"]
        return BookDepthDict(
            s=symbol,
            t=int(data["T"]),
            u=0,
            b=[(float(p), float(v)) for p, v in data["bids"]],
            a=[(float(p), float(v)) for p, v in data["asks"]],
        )

    @staticmethod
    def futures_delistings(raw_data: dict) -> dict[str, int]:
        # offTime — время отключения контракта, 0 — не запланировано
        now = int(time.time() * 1000)
        result = {}
        for item in raw_data["data"]:
            try:
                off_time = int(item.get("offTime") or 0)
                if off_time > now:
                    result[item["symbol"]] = off_time
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        data = raw_data["data"]
        if isinstance(data, list):
            return {
                item["symbol"]: float(item["lastPrice"] if "lastPrice" in item else item["price"])
                for item in data
            }
        if isinstance(data, dict):
            return {data["symbol"]: float(data["price"])}
        return {}

    @staticmethod
    def klines(raw_data: dict) -> list[KlineDict]:
        data = raw_data["data"]
        items = data["klines"] if isinstance(data, dict) and "klines" in data else data
        if "symbol" in raw_data:
            symbol = raw_data["symbol"]
        elif isinstance(data, dict) and "symbol" in data:
            symbol = data["symbol"]
        else:
            symbol = ""

        if items and isinstance(items[0], dict):
            return [
                KlineDict(
                    s=symbol,
                    t=int(kline["time"]),
                    o=float(kline["open"]),
                    h=float(kline["high"]),
                    l=float(kline["low"]),
                    c=float(kline["close"]),
                    v=float(kline["volume"]),
                    q=0.0,
                    T=None,
                    x=None,
                )
                for kline in sorted(
                    items,
                    key=lambda x: int(x["time"]),
                )
            ]

        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[5]),
                q=float(kline[7]) if len(kline) > 7 else 0.0,
                T=int(kline[6]) if len(kline) > 6 else None,
                x=None,
            )
            for kline in sorted(
                items,
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def Klines_message(msg: Any) -> list[KlineDict]: ...

    @staticmethod
    def futures_klines_message(msg: Any) -> list[KlineDict]: ...

    @staticmethod
    def aggtrades_message(msg: Any) -> list[TradeDict]: ...

    @staticmethod
    def futures_aggtrades_message(msg: Any) -> list[TradeDict]: ...

    @staticmethod
    def trades_message(msg: Any) -> list[TradeDict]:
        # Фьючерсы присылают список сделок, спот — одну сделку объектом
        data = msg["data"]
        trades = data if isinstance(data, list) else [data]
        return [
            TradeDict(
                t=int(trade["T"]),
                s=str(trade["s"]),
                S="SELL" if bool(trade["m"]) else "BUY",
                p=float(trade["p"]),
                v=float(trade["q"]),
            )
            for trade in sorted(
                trades,
                key=lambda x: int(x["T"]),
            )
        ]

    @staticmethod
    def liquidations_message(msg: Any) -> list[LiquidationDict]: ...
