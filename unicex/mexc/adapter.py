__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
    BestBidAskDict,
    BestBidAskItem,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods

from .exchange_info import ExchangeInfo


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Mexc API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        return [
            item["symbol"] for item in raw_data if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        return [
            item["symbol"]
            for item in raw_data["data"]
            if item["symbol"].endswith("USDT") or not only_usdt
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
        result = {}
        for item in raw_data["data"]:
            symbol = item["symbol"]
            result[symbol] = TickerDailyItem(
                p=round(float(item["riseFallRate"]) * 100, 2),
                v=float(item["volume24"]) * Adapter._get_contract_size(symbol),
                q=float(item["amount24"]),
            )
        return result

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        result = {}
        for item in raw_data["data"]:
            symbol = item["symbol"]
            result[symbol] = OpenInterestItem(
                t=item["timestamp"],
                v=float(item["holdVol"]) * Adapter._get_contract_size(symbol),
                u="coins",
            )
        return result

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        return {
            item["symbol"]: float(item["fundingRate"]) * 100
            for item in raw_data["data"]
            if "fundingRate" in item  # В некоторых элементах item нет ключа 'fundingRate'
        }

    @staticmethod
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
        data = raw_data["data"]
        items = data if isinstance(data, list) else [data]
        return {
            item["symbol"]: BestBidAskItem(
                s=item["symbol"],
                t=int(item["timestamp"]),
                u=0,  # REST endpoint не возвращает update id
                b=float(item.get("bid1", "0.0")),
                B=0.0,  # REST endpoint не возвращает размер лучшего бида
                a=float(item.get("ask1", "0.0")),
                A=0.0,  # REST endpoint не возвращает размер лучшего аска
            )
            for item in items
        }

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
    def futures_klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        data = raw_data["data"]

        times = data["time"]
        opens = data["open"]
        highs = data["high"]
        lows = data["low"]
        closes = data["close"]
        volumes = data["vol"]
        amounts = data["amount"]

        klines: list[KlineDict] = []

        for kline_time, open_, high, low, close, volume, amount in zip(
            times,
            opens,
            highs,
            lows,
            closes,
            volumes,
            amounts,
            strict=False,
        ):
            timestamp = int(float(kline_time))
            if timestamp < 10**12:
                timestamp *= 1000

            klines.append(
                KlineDict(
                    s=symbol,
                    t=timestamp,
                    o=float(open_),
                    h=float(high),
                    l=float(low),
                    c=float(close),
                    v=float(volume),
                    q=float(amount),
                    T=None,
                    x=None,
                )
            )

        return sorted(klines, key=lambda kline_item: kline_item["t"])

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        kline = raw_msg["publicSpotKline"]
        return [
            KlineDict(
                s=raw_msg["symbol"],
                t=int(kline["windowStart"]) * 1000,
                o=float(kline["openingPrice"]),
                h=float(kline["highestPrice"]),
                l=float(kline["lowestPrice"]),
                c=float(kline["closingPrice"]),
                v=float(kline["volume"]),
                T=int(kline["windowEnd"]) * 1000,
                x=None,
                q=float(kline["amount"]),
            )
        ]

    @staticmethod
    def futures_klines_message(raw_msg: Any) -> list[KlineDict]:
        data = raw_msg["data"]
        return [
            KlineDict(
                s=data["symbol"],
                t=data["t"] * 1000,
                o=data["o"],
                h=data["h"],
                l=data["l"],
                c=data["c"],
                v=data["q"],  # Контракты
                q=data["a"],
                T=None,
                x=None,
            )
        ]

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        return [
            TradeDict(
                t=trade["time"],
                s=raw_msg["symbol"],
                S="BUY" if trade["tradeType"] == 1 else "SELL",
                p=float(trade["price"]),
                v=float(trade["quantity"]),
            )
            for trade in sorted(
                raw_msg["publicAggreDeals"]["deals"],
                key=lambda item: item["time"],
            )
        ]

    @staticmethod
    def futures_trades_message(raw_msg: Any) -> list[TradeDict]:
        return [
            TradeDict(
                t=item["t"],
                s=raw_msg["symbol"],
                S="BUY" if item["T"] == 1 else "SELL",
                p=item["p"],
                v=item["v"] * Adapter._get_contract_size(raw_msg["symbol"]),
            )
            for item in sorted(
                raw_msg["data"],
                key=lambda item: item["t"],
            )
        ]

    @staticmethod
    def _get_contract_size(symbol: str) -> float:
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            return 1
