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
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods

from .exchange_info import ExchangeInfo


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Kucoin API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        return [
            item["symbol"]
            for item in raw_data["data"]["list"]
            if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        return [
            item["symbol"]
            for item in raw_data["data"]["list"]
            if item["symbol"].endswith("USDTM") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        def safe_float(value: object, default: float = 0.0) -> float:
            try:
                if value is None:
                    return default
                return float(value)  # type: ignore
            except (TypeError, ValueError):
                return default

        result: dict[str, TickerDailyItem] = {}

        for item in raw_data["data"]["list"]:
            symbol = item.get("symbol")
            if not symbol:
                continue

            last_price = safe_float(item.get("lastPrice"))
            open_price = safe_float(item.get("open"))
            base_volume = safe_float(item.get("baseVolume"))
            quote_volume = safe_float(item.get("quoteVolume"))

            if open_price > 0:
                p = round((last_price / open_price - 1) * 100, 2)
            else:
                p = 0.0

            result[symbol] = TickerDailyItem(
                p=p,
                v=base_volume,
                q=quote_volume,
            )

        return result

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        return {
            item["symbol"]: float(item["lastPrice"])
            for item in raw_data["data"]["list"]
            if item["lastPrice"]
        }

    @staticmethod
    def open_interest(
        raw_data: dict[str, Any], contract_sizes: dict[str, float] | None = None
    ) -> OpenInterestDict:
        result = {}
        for item in raw_data["data"]:
            try:
                result[item["symbol"]] = OpenInterestItem(
                    t=Adapter._to_ms(item["ts"]),
                    v=float(item["openInterest"])
                    * Adapter._contract_size(item["symbol"], contract_sizes),
                    u="coins",
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def _funding_items(raw_data: dict) -> list[dict]:
        # UTA V2 отдаёт список (V1 отдавал объект с символом вида ".XBTUSDTMFPI8H")
        data = raw_data["data"]
        return data if isinstance(data, list) else [data]

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        result = {}
        for item in Adapter._funding_items(raw_data):
            try:
                result[item["symbol"]] = round(float(item["nextFundingRate"]) * 100, 6)
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_interval(raw_data: dict) -> dict[str, int]:
        result = {}
        for item in Adapter._funding_items(raw_data):
            try:
                result[item["symbol"]] = int(item["currentGranularity"]) // (1000 * 60 * 60)
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_next_time(raw_data: dict) -> dict[str, int]:
        result = {}
        for item in Adapter._funding_items(raw_data):
            try:
                result[item["symbol"]] = int(item["fundingTime"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_info(raw_data: dict) -> FundingInfoDict:
        result = {}
        for item in Adapter._funding_items(raw_data):
            try:
                result[item["symbol"]] = FundingInfoItem(
                    v=round(float(item["nextFundingRate"]) * 100, 6),
                    i=int(item["currentGranularity"]) // (1000 * 60 * 60),
                    T=int(item["fundingTime"]),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def klines(raw_data: dict, symbol: str, contract_size: float = 1) -> list[KlineDict]:
        # UTA (с 2026-01-17): [t (сек), o, h, l, c, v, q]; у фьючерсов v — в контрактах
        klines: list[KlineDict] = []
        for item in sorted(raw_data["data"]["list"], key=lambda x: int(float(x[0]))):
            try:
                klines.append(
                    KlineDict(
                        s=symbol,
                        t=int(float(item[0])) * 1000,
                        o=float(item[1]),
                        h=float(item[2]),
                        l=float(item[3]),
                        c=float(item[4]),
                        v=float(item[5]) * contract_size,
                        q=float(item[6]),
                        T=None,
                        x=None,
                    )
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return klines

    @staticmethod
    def futures_best_bid_ask(
        raw_data: dict, contract_sizes: dict[str, float] | None = None
    ) -> BestBidAskDict:
        result = {}
        for item in raw_data["data"]["list"]:
            try:
                if not (item.get("bestBidPrice") and item.get("bestAskPrice")):
                    continue
                size = Adapter._contract_size(item["symbol"], contract_sizes)
                result[item["symbol"]] = BestBidAskItem(
                    s=item["symbol"],
                    t=Adapter._to_ms(item.get("ts") or raw_data["data"]["ts"]),
                    u=int(item.get("sequence") or 0),
                    b=float(item["bestBidPrice"]),
                    B=float(item["bestBidSize"] or 0) * size,
                    a=float(item["bestAskPrice"]),
                    A=float(item["bestAskSize"] or 0) * size,
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_depth(raw_data: dict, symbol: str, contract_size: float = 1) -> BookDepthDict:
        data = raw_data["data"]
        return BookDepthDict(
            s=symbol,
            t=Adapter._to_ms(data["ts"]),
            u=int(data["sequence"]),
            b=[(float(p), float(v) * contract_size) for p, v in data["bids"]],
            a=[(float(p), float(v) * contract_size) for p, v in data["asks"]],
        )

    @staticmethod
    def futures_delistings(raw_data: dict) -> dict[str, int]:
        # Для бессрочных контрактов (contractType "0") expiryTime заполняется только при делистинге
        now = int(time.time() * 1000)
        result = {}
        for item in raw_data["data"]["list"]:
            try:
                expiry = item.get("expiryTime")
                if str(item.get("contractType")) == "0" and expiry and int(expiry) > now:
                    result[item["symbol"]] = int(expiry)
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def contract_sizes(raw_data: dict) -> dict[str, float]:
        result = {}
        for item in raw_data["data"]["list"]:
            try:
                result[item["symbol"]] = float(item["unitSize"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def _to_ms(ts: int | str) -> int:
        """Приводит метку времени KuCoin (сек / мс / мкс / нс) к миллисекундам."""
        value = int(float(ts))
        while value > 10**13:
            value //= 1000
        if value < 10**11:
            value *= 1000
        return value

    @staticmethod
    def _contract_size(symbol: str, contract_sizes: dict[str, float] | None = None) -> float:
        if contract_sizes and symbol in contract_sizes:
            return contract_sizes[symbol]
        return Adapter._get_contract_size(symbol)

    @staticmethod
    def _get_contract_size(symbol: str) -> float:
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            return 1
