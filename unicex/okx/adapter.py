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
from unicex.utils import catch_adapter_errors, decorate_all_methods

from .exchange_info import ExchangeInfo


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Okx API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        return [
            item["instId"]
            for item in raw_data["data"]
            if item["instId"].endswith("-USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        return [
            item["instId"]
            for item in raw_data["data"]
            if item["instId"].endswith("-USDT-SWAP") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        # Обратите внимание, изменение цены в случае с OKX возвращается относительно открытия 1 day свечи.
        result = {}
        for item in raw_data["data"]:
            try:
                result[item["instId"]] = TickerDailyItem(
                    p=round(
                        (float(item["last"]) - float(item["open24h"]))
                        / float(item["open24h"])
                        * 100,
                        2,
                    ),
                    v=float(item["vol24h"]),
                    q=float(item["volCcy24h"]),
                )
            except (ValueError, TypeError, KeyError):
                continue
        return result

    @staticmethod
    def futures_ticker_24hr(raw_data: dict) -> TickerDailyDict:
        # Обратите внимание, изменение цены в случае с OKX возвращается относительно открытия 1 day свечи.
        result = {}
        for item in raw_data["data"]:
            try:
                last = float(item["last"])
                open_24h = float(item["open24h"])
                vol_ccy_24h = float(item["volCcy24h"])
                result[item["instId"]] = TickerDailyItem(
                    p=round((last - open_24h) / open_24h * 100, 2),
                    v=vol_ccy_24h,
                    q=vol_ccy_24h * last,
                )
            except (ValueError, TypeError, KeyError, ZeroDivisionError):
                continue
        return result

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        result = {}
        for item in raw_data["data"]:
            try:
                result[item["instId"]] = float(item["last"])
            except (ValueError, TypeError, KeyError):
                continue
        return result

    @staticmethod
    def klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[6]),
                q=float(kline[7]),
                T=None,
                x=bool(int(kline[8])),
            )
            for kline in sorted(
                raw_data["data"],
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        data = raw_data["data"][0]
        return {data["instId"]: float(data["fundingRate"]) * 100}

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        return {
            item["instId"]: OpenInterestItem(
                t=int(item["ts"]),
                v=float(item["oiCcy"]),
                u="coins",
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
        return {
            item["instId"]: BestBidAskItem(
                s=item["instId"],
                t=int(item["ts"]),
                u=0,  # REST endpoint не возвращает update id
                b=float(item["bidPx"]),
                B=float(item["bidSz"]) * Adapter._get_contract_size(item["instId"]),
                a=float(item["askPx"]),
                A=float(item["askSz"]) * Adapter._get_contract_size(item["instId"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def futures_depth(raw_data: dict, symbol: str) -> BookDepthDict:
        data = raw_data["data"][0]
        contract_size = Adapter._get_contract_size(symbol)
        return BookDepthDict(
            s=symbol,
            t=int(data["ts"]),
            u=int(data["seqId"]),
            b=[(float(item[0]), float(item[1]) * contract_size) for item in data["bids"]],
            a=[(float(item[0]), float(item[1]) * contract_size) for item in data["asks"]],
        )

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        return [
            KlineDict(
                s=raw_msg["arg"]["instId"],
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[6]),
                q=float(kline[7]),
                T=None,
                x=bool(int(kline[8])),
            )
            for kline in sorted(raw_msg["data"], key=lambda item: int(item[0]))
        ]

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        return [
            TradeDict(
                t=int(trade["ts"]),
                s=trade["instId"],
                S=trade["side"].upper(),
                p=float(trade["px"]),
                v=float(trade["sz"]) * Adapter._get_contract_size(trade["instId"]),
            )
            for trade in sorted(raw_msg["data"], key=lambda item: int(item["ts"]))
        ]

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: Any) -> list[BestBidAskItem]:
        data = raw_msg["data"][0]
        inst_id = raw_msg["arg"]["instId"]
        contract_size = Adapter._get_contract_size(inst_id)
        bids = data.get("bids", [])
        asks = data.get("asks", [])

        best_bid = bids[0] if bids else None
        best_ask = asks[0] if asks else None

        bid_price = float(best_bid[0]) if best_bid else 0.0
        bid_size = float(best_bid[1]) if best_bid else 0.0
        ask_price = float(best_ask[0]) if best_ask else 0.0
        ask_size = float(best_ask[1]) if best_ask else 0.0

        return [
            BestBidAskItem(
                s=str(raw_msg["arg"]["instId"]),
                t=int(data["ts"]),
                u=int(data["seqId"]),
                b=bid_price,
                B=bid_size * contract_size,
                a=ask_price,
                A=ask_size * contract_size,
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message(raw_msg: Any) -> list[BookDepthDict]:
        data = raw_msg["data"][0]
        inst_id = raw_msg["arg"]["instId"]
        contract_size = Adapter._get_contract_size(inst_id)
        bids = data.get("bids", [])
        asks = data.get("asks", [])

        return [
            BookDepthDict(
                s=inst_id,
                t=int(data["ts"]),
                u=int(data["seqId"]),
                b=[(float(item[0]), float(item[1]) * contract_size) for item in bids],
                a=[(float(item[0]), float(item[1]) * contract_size) for item in asks],
            )
        ]

    @staticmethod
    def _get_contract_size(symbol: str) -> float:
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            return 1
