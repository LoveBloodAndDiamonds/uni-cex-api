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
    OrderIdDict,
    PositionInfoDict,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods

from .exchange_info import ExchangeInfo


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Gateio API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        return [
            item["currency_pair"]
            for item in raw_data
            if item["currency_pair"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        return [
            item["contract"]
            for item in raw_data
            if item["contract"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        result = {}
        for item in raw_data:
            try:
                result[item["currency_pair"]] = float(item["last"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        result = {}
        for item in raw_data:
            try:
                result[item["contract"]] = float(item["last"])
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        result = {}
        for item in raw_data:
            try:
                result[item["currency_pair"]] = TickerDailyItem(
                    p=float(item["change_percentage"]),
                    v=float(item["base_volume"]),
                    q=float(item["quote_volume"]),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        result = {}
        for item in raw_data:
            try:
                result[item["contract"]] = TickerDailyItem(
                    p=float(item["change_percentage"]),
                    v=float(item["volume_24h_base"]),
                    q=float(item["volume_24h_quote"]),
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]) * 1000,  # переводим секунды → миллисекунды
                o=float(kline[5]),
                h=float(kline[3]),
                l=float(kline[4]),
                c=float(kline[2]),
                v=float(kline[6]),
                q=float(kline[1]),
                T=None,
                x=kline[7] == "true",
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def futures_klines(raw_data: list[dict], symbol: str) -> list[KlineDict]:
        return [
            KlineDict(
                s=symbol,
                t=int(kline["t"]) * 1000,  # переводим секунды → миллисекунды
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["sum"]),  # "sum" = объем в $ (quote volume)
                T=None,
                x=None,
            )
            for kline in sorted(raw_data, key=lambda x: int(x["t"]))
        ]

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        result = {}
        for item in raw_data:
            try:
                if item.get("funding_rate") is not None:
                    result[item["contract"]] = float(item["funding_rate"]) * 100
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_interval(raw_data: list[dict]) -> dict[str, int]:
        result = {}
        for item in raw_data:
            try:
                if item.get("funding_interval") is not None:
                    result[item["name"]] = int(item["funding_interval"]) // 3600
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_next_time(raw_data: list[dict]) -> dict[str, int]:
        result = {}
        for item in raw_data:
            try:
                if item.get("funding_next_apply") is not None:
                    # funding_next_apply возвращается в секундах, переводим в миллисекунды
                    result[item["name"]] = int(item["funding_next_apply"]) * 1000
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def funding_info(tickers_data: list[dict], contracts_data: list[dict]) -> FundingInfoDict:
        # Строим словари из contracts: interval (сек → ч) и next_time (сек → мс)
        intervals = {
            item["name"]: int(item["funding_interval"]) // 3600
            for item in contracts_data
            if item.get("funding_interval") is not None
        }
        next_times = {
            item["name"]: int(item["funding_next_apply"]) * 1000
            for item in contracts_data
            if item.get("funding_next_apply") is not None
        }
        result: FundingInfoDict = {}
        for item in tickers_data:
            try:
                if item.get("funding_rate") is not None:
                    symbol = item["contract"]
                    result[symbol] = FundingInfoItem(
                        v=float(item["funding_rate"]) * 100,
                        i=intervals.get(symbol, 0),
                        T=next_times.get(symbol, 0),
                    )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def open_interest(raw_data: list[dict]) -> OpenInterestDict:
        result = {}
        for item in raw_data:
            try:
                result[item["contract"]] = OpenInterestItem(
                    t=int(time.time() * 1000),
                    v=float(item["total_size"]) * float(item["quanto_multiplier"]),
                    u="coins",
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_best_bid_ask(raw_data: list[dict]) -> BestBidAskDict:
        result = {}
        for item in raw_data:
            try:
                contract = item["contract"]
                contract_size = Adapter._get_contract_size(contract)
                result[contract] = BestBidAskItem(
                    s=contract,
                    t=int(time.time() * 1000),
                    u=0,
                    b=float(item["highest_bid"]),
                    B=float(item["highest_size"]) * contract_size,
                    a=float(item["lowest_ask"]),
                    A=float(item["lowest_size"]) * contract_size,
                )
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return result

    @staticmethod
    def futures_depth(raw_data: dict, symbol: str) -> BookDepthDict:
        contract_size = Adapter._get_contract_size(symbol)
        bids = []
        asks = []
        for item in raw_data["bids"]:
            try:
                bids.append((float(item["p"]), float(item["s"]) * contract_size))
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        for item in raw_data["asks"]:
            try:
                asks.append((float(item["p"]), float(item["s"]) * contract_size))
            except Exception as e:
                logger.error(f"Item {item} iteration {type(e)} error: {e}")
        return BookDepthDict(
            s=symbol,
            t=int(float(raw_data["update"]) * 1000),
            u=int(raw_data.get("id", 0)),
            b=bids,
            a=asks,
        )

    @staticmethod
    def futures_delistings(contracts: list) -> dict[str, int]:
        result = {}
        for item in contracts:
            symbol = item["name"]
            delisting_time = item.get("delisting_time")

            if not delisting_time:
                continue

            # delisting_time приходит в секундах, конвертируем в мс
            result[symbol] = int(delisting_time * 1000)

        return result

    @staticmethod
    def futures_order_create(raw_data: dict) -> OrderIdDict:
        return OrderIdDict(
            t=raw_data["create_time"] * 1000,
            id=raw_data["id"],
            cloid=raw_data["text"],
        )

    @staticmethod
    def futures_position_info(raw_data: dict) -> PositionInfoDict:
        if not raw_data:
            return PositionInfoDict(
                t=0,
                symbol="",
                side="",
                quantity=0,
                entry_price=0,
                mark_price=0,
                liquidation_price=0,
                unrealized_pnl=0,
                realized_pnl=0,
                leverage=0,
                notional=0,
            )
        contracts = float(raw_data["size"])
        contract_size = Adapter._get_contract_size(raw_data["contract"])
        quantity = abs(contracts) * contract_size

        return PositionInfoDict(
            t=raw_data["update_time"] * 1000,
            symbol=raw_data["contract"],
            side="BUY" if contracts > 0 else "SELL" if contracts < 0 else "",
            quantity=quantity,
            entry_price=float(raw_data["entry_price"]),
            mark_price=float(raw_data["mark_price"]),
            liquidation_price=float(raw_data["liq_price"]),
            unrealized_pnl=float(raw_data["unrealised_pnl"]),
            realized_pnl=float(raw_data["realised_pnl"]),
            leverage=float(raw_data["lever"]),
            notional=abs(float(raw_data["value"])),
        )

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        data = raw_msg["result"]
        return [
            KlineDict(
                s=data["n"].split("_", 1)[1],  # XRP_USDT
                t=int(data["t"]) * 1000,
                o=float(data["o"]),
                h=float(data["h"]),
                l=float(data["l"]),
                c=float(data["c"]),
                v=float(data["a"]),
                q=float(data["v"]),
                T=None,
                x=not data["w"],  # w=False → свеча закрыта
            )
        ]

    @staticmethod
    def futures_klines_message(raw_msg: Any) -> list[KlineDict]:
        return [
            KlineDict(
                s=item["n"].split("_", 1)[1],  # XRP_USDT
                t=int(item["t"]) * 1000,
                o=float(item["o"]),
                h=float(item["h"]),
                l=float(item["l"]),
                c=float(item["c"]),
                v=float(item["a"]),
                q=float(item["v"]),
                T=None,
                x=not item["w"],  # w=False → свеча закрыта
            )
            for item in sorted(
                raw_msg["result"],
                key=lambda x: int(x["t"]),
            )
        ]

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        trade = raw_msg["result"]
        return [
            TradeDict(
                t=trade["create_time_ms"],
                s=trade["currency_pair"],
                S=trade["side"].upper(),
                p=float(trade["price"]),
                v=float(trade["amount"]),
            )
        ]

    @staticmethod
    def futures_trades_message(raw_msg: Any) -> list[TradeDict]:
        return [
            TradeDict(
                t=item["create_time_ms"],
                s=item["contract"],
                S="BUY" if float(item["size"]) > 0 else "SELL",
                p=float(item["price"]),
                v=abs(float(item["size"])) * Adapter._get_contract_size(item["contract"]),
            )
            for item in sorted(
                raw_msg["result"],
                key=lambda x: x["create_time_ms"],
            )
        ]

    @staticmethod
    def futures_best_bid_ask_message(raw_msg: Any) -> list[BestBidAskItem]:
        result = raw_msg["result"]
        symbol = result["s"]
        contract_size = Adapter._get_contract_size(symbol)
        bid_price = float(result["b"]) if result["b"] != "" else 0.0
        ask_price = float(result["a"]) if result["a"] != "" else 0.0
        return [
            BestBidAskItem(
                s=symbol,
                t=int(result["t"]),
                u=int(result["u"]),
                b=bid_price,
                B=float(result["B"]) * contract_size,
                a=ask_price,
                A=float(result["A"]) * contract_size,
            )
        ]

    @staticmethod
    def futures_partial_book_depth_message(raw_msg: Any) -> list[BookDepthDict]:
        result = raw_msg["result"]
        symbol = result["contract"]
        contract_size = Adapter._get_contract_size(symbol)
        bids = result.get("bids", [])
        asks = result.get("asks", [])
        update_id = result.get("id", result.get("u"))
        if update_id is None:
            raise ValueError("Field `id` is missing in futures.order_book message")
        return [
            BookDepthDict(
                s=symbol,
                t=int(result["t"]),
                u=int(update_id),
                b=[(float(item["p"]), float(item["s"]) * contract_size) for item in bids],
                a=[(float(item["p"]), float(item["s"]) * contract_size) for item in asks],
            )
        ]

    @staticmethod
    def _get_contract_size(symbol: str) -> float:
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            raise
