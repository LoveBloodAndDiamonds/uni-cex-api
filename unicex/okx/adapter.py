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
    LongShortRatioItem,
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
    def _base_volume_index(inst_id: str) -> int:
        """Индекс объёма в базовой валюте в свече OKX.

        Свеча: `[ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]`.
        Спот (`BTC-USDT`): `vol` — в базовой валюте. SWAP/FUTURES (`BTC-USDT-SWAP`):
        `vol` — в контрактах, `volCcy` — в базовой валюте. `volCcyQuote` — всегда в котируемой.
        """
        return 5 if inst_id.count("-") == 1 else 6

    @staticmethod
    def klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        v_idx = Adapter._base_volume_index(symbol)
        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[v_idx]),
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
    def _swap_funding_items(raw_data: dict) -> list[dict]:
        """Элементы `public/funding-rate` только по бессрочным SWAP (без X-Perps `FUTURES`)."""
        return [item for item in raw_data["data"] if item.get("instType", "SWAP") == "SWAP"]

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        result = {}
        for item in Adapter._swap_funding_items(raw_data):
            try:
                result[item["instId"]] = float(item["fundingRate"]) * 100
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_interval(raw_data: dict) -> dict[str, int]:
        result = {}
        for item in Adapter._swap_funding_items(raw_data):
            try:
                if item.get("fundingTime") and item.get("prevFundingTime"):
                    result[item["instId"]] = (
                        int(item["fundingTime"]) - int(item["prevFundingTime"])
                    ) // (1000 * 60 * 60)
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_next_time(raw_data: dict) -> dict[str, int]:
        # fundingTime — ближайшее списание по текущей ставке, nextFundingTime — следующее за ним
        result = {}
        for item in Adapter._swap_funding_items(raw_data):
            try:
                if item.get("fundingTime"):
                    result[item["instId"]] = int(item["fundingTime"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_info(raw_data: dict) -> FundingInfoDict:
        result = {}
        for item in Adapter._swap_funding_items(raw_data):
            try:
                funding_time = int(item["fundingTime"]) if item.get("fundingTime") else 0
                prev_time = int(item["prevFundingTime"]) if item.get("prevFundingTime") else 0
                interval = (funding_time - prev_time) // (1000 * 60 * 60) if prev_time else 0
                result[item["instId"]] = FundingInfoItem(
                    v=float(item["fundingRate"]) * 100,
                    i=interval,
                    T=funding_time,
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_delistings(raw_data: dict) -> dict[str, int]:
        # Для SWAP expTime заполняется только при плановом выводе инструмента
        now = int(time.time() * 1000)
        result = {}
        for item in raw_data["data"]:
            try:
                if item.get("expTime") and int(item["expTime"]) > now:
                    result[item["instId"]] = int(item["expTime"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

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
    def long_short_ratio(raw_data: dict) -> list[LongShortRatioItem]:
        result: list[LongShortRatioItem] = []
        for item in raw_data["data"]:
            try:
                ts, raw_ratio = item[0], item[1]
                ratio = float(raw_ratio)
                # OKX отдает только ratio = long / short, доли восстанавливаются из него
                result.append(
                    LongShortRatioItem(
                        t=int(ts),
                        long=ratio / (1 + ratio),
                        short=1 / (1 + ratio),
                        ratio=ratio,
                    )
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        result.sort(key=lambda x: x["t"])
        return result

    @staticmethod
    def futures_best_bid_ask(raw_data: dict) -> BestBidAskDict:
        result = {}
        for item in raw_data["data"]:
            # У неликвидных инструментов bidPx/bidSz/askPx/askSz бывают пустыми строками
            if not (item.get("bidPx") and item.get("bidSz") and item.get("askPx")):
                continue
            if not item.get("askSz"):
                continue
            try:
                contract_size = Adapter._get_contract_size(item["instId"])
                result[item["instId"]] = BestBidAskItem(
                    s=item["instId"],
                    t=int(item["ts"]),
                    u=0,  # REST endpoint не возвращает update id
                    b=float(item["bidPx"]),
                    B=float(item["bidSz"]) * contract_size,
                    a=float(item["askPx"]),
                    A=float(item["askSz"]) * contract_size,
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

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
        v_idx = Adapter._base_volume_index(raw_msg["arg"]["instId"])
        return [
            KlineDict(
                s=raw_msg["arg"]["instId"],
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[v_idx]),
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
