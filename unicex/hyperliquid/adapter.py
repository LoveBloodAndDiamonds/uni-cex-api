__all__ = ["Adapter"]

import time

from unicex.types import (
    BestBidAskDict,
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    PartialBookDepthDict,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods

from .exchange_info import ExchangeInfo


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Hyperliquid API."""

    @staticmethod
    def _resolve_spot_symbol(symbol: str, resolve_symbols: bool) -> str:
        """Преобразует внутренний спотовый идентификатор в тикер."""
        if not resolve_symbols:
            return symbol
        try:
            return ExchangeInfo.resolve_spot_symbol(symbol)
        except ValueError:
            # Если ExchangeInfo еще не загружен, возвращаем исходное значение.
            return symbol

    @staticmethod
    def tickers(raw_data: dict, resolve_symbols: bool = True) -> list[str]:
        """Преобразует данные Hyperliquid в список спотовых тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, преобразует "@123" в обычный тикер.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            Adapter._resolve_spot_symbol(item["name"], resolve_symbols)
            for item in raw_data["universe"]
        ]

    @staticmethod
    def futures_tickers(raw_data: dict) -> list[str]:
        """Преобразует данные Hyperliquid в список фьючерсных тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[str]: Список тикеров (например, "BTC, ETH").
        """
        return Adapter.tickers(raw_data, resolve_symbols=False)

    @staticmethod
    def last_price(raw_data: dict, resolve_symbols: bool = True) -> dict[str, float]:
        """Преобразует данные о последних ценах (spot) в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, преобразует "@123" в обычный тикер.

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        return {
            Adapter._resolve_spot_symbol(token, resolve_symbols): float(price)
            for token, price in raw_data.items()
            if token.startswith("@")
        }

    @staticmethod
    def futures_last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует данные о последних ценах (futures) в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и последних цен.
        """
        return {
            token: float(price) for token, price in raw_data.items() if not token.startswith("@")
        }

    @staticmethod
    def ticker_24hr(raw_data: list, resolve_symbols: bool = True) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (spot) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, преобразует "@123" в обычный тикер.

        Возвращает:
            TickerDailyDict: Словарь тикеров и их статистики.
        """
        metrics = raw_data[1]
        result: TickerDailyDict = {}

        for item in metrics:
            try:
                coin = Adapter._resolve_spot_symbol(item["coin"], resolve_symbols)

                prev_day_px = float(item.get("prevDayPx") or "0")
                mid_px = float(item.get("midPx") or "0")
                mark_px = float(item.get("markPx") or "0")
                day_ntl_vlm = float(item.get("dayNtlVlm") or "0")

                p = round(((mark_px - prev_day_px) / prev_day_px * 100), 2) if prev_day_px else 0.0
                v = (day_ntl_vlm / mid_px) if mid_px else 0.0
                q = day_ntl_vlm

                if coin in result:
                    # В случае конфликта оставляем запись с большим дневным объемом.
                    prev_ticker_daily = result[coin]
                    curr_ticker_daily = TickerDailyItem(p=p, v=v, q=q)
                    if prev_ticker_daily["q"] > curr_ticker_daily["q"]:
                        result[coin] = prev_ticker_daily
                    else:
                        result[coin] = curr_ticker_daily
                else:
                    result[coin] = TickerDailyItem(p=p, v=v, q=q)

            except (KeyError, TypeError, ValueError):
                continue

        return result

    @staticmethod
    def futures_ticker_24hr(raw_data: list) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (futures) в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь тикеров и их статистики.
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]

        result: TickerDailyDict = {}

        for i, item in enumerate(metrics):
            try:
                prev_day_px = float(item.get("prevDayPx", 0) or "0")
                oracle_px = float(item.get("oraclePx", 0) or "0")
                mark_px = float(item.get("markPx", 0) or "0")
                day_ntl_vlm = float(item.get("dayNtlVlm", 0) or "0")

                p = ((mark_px - prev_day_px) / prev_day_px * 100) if prev_day_px else 0.0
                v = (day_ntl_vlm / oracle_px) if oracle_px else 0.0
                q = day_ntl_vlm

                result[universe[i]["name"]] = TickerDailyItem(p=p, v=v, q=q)
            except (KeyError, TypeError, ValueError):
                continue

        return result

    @staticmethod
    def klines(raw_data: list[dict], resolve_symbols: bool = True) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            resolve_symbols (bool): Если True, преобразует "@123" в обычный тикер.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s=Adapter._resolve_spot_symbol(str(kline["s"]), resolve_symbols),
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),
                q=float(kline["v"]) * float(kline["c"]),
                T=kline["T"],
                x=None,
            )
            for kline in sorted(
                raw_data,
                key=lambda x: int(x["t"]),
            )
        ]

    @staticmethod
    def futures_klines(raw_data: list[dict]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return Adapter.klines(raw_data, resolve_symbols=False)

    @staticmethod
    def funding_rate(raw_data: list) -> dict[str, float]:
        """Преобразует данные о ставках финансирования в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь тикеров и ставок финансирования (в %).
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {
            universe[i]["name"]: float(item["funding"]) * 100
            for i, item in enumerate(metrics)
            if item.get("funding") is not None
        }

    @staticmethod
    def open_interest(raw_data: list) -> OpenInterestDict:
        """Преобразует данные об открытом интересе в унифицированный формат.

        Параметры:
            raw_data (list): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь тикеров и значений открытого интереса.
        """
        universe = raw_data[0]["universe"]
        metrics = raw_data[1]
        return {
            universe[i]["name"]: OpenInterestItem(
                t=int(time.time() * 1000),
                v=float(item["openInterest"]),
                u="coins",
            )
            for i, item in enumerate(metrics)
        }

    @staticmethod
    def klines_message(raw_msg: dict, resolve_symbols: bool = True) -> list[KlineDict]:
        """Преобразует сырое websocket-сообщение со свечой в унифицированный формат."""
        candle = raw_msg["data"]
        volume = float(candle["v"])
        close_price = float(candle["c"])

        return [
            KlineDict(
                s=Adapter._resolve_spot_symbol(str(candle["s"]), resolve_symbols),
                t=int(candle["t"]),
                o=float(candle["o"]),
                h=float(candle["h"]),
                l=float(candle["l"]),
                c=close_price,
                v=volume,
                q=volume * close_price,
                T=int(candle["T"]),
                x=None,
            )
        ]

    @staticmethod
    def trades_message(raw_msg: dict, resolve_symbols: bool = True) -> list[TradeDict]:
        """Преобразует сырое websocket-сообщение со сделками в унифицированный формат."""
        result: list[TradeDict] = []
        for trade in sorted(raw_msg["data"], key=lambda item: int(item["time"])):
            side = "BUY" if trade["side"] == "B" else "SELL"
            result.append(
                TradeDict(
                    t=int(trade["time"]),
                    s=Adapter._resolve_spot_symbol(str(trade["coin"]), resolve_symbols),
                    S=side,
                    p=float(trade["px"]),
                    v=float(trade["sz"]),
                )
            )

        return result

    @staticmethod
    def best_bid_ask_message(raw_msg: dict, resolve_symbols: bool = True) -> list[BestBidAskDict]:
        """Преобразует сырое websocket-сообщение с лучшим бидом/аском в унифицированный формат."""
        data = raw_msg["data"]
        best_bid = data["bbo"][0]
        best_ask = data["bbo"][1]

        bid_price = float(best_bid["px"]) if best_bid else 0.0
        bid_size = float(best_bid["sz"]) if best_bid else 0.0
        ask_price = float(best_ask["px"]) if best_ask else 0.0
        ask_size = float(best_ask["sz"]) if best_ask else 0.0

        return [
            BestBidAskDict(
                t=int(data["time"]),
                u=int(data["time"]),
                b=bid_price,
                B=bid_size,
                a=ask_price,
                A=ask_size,
            )
        ]

    @staticmethod
    def partial_book_depth_message(
        raw_msg: dict,
        limit: int,
        resolve_symbols: bool = True,
    ) -> list[PartialBookDepthDict]:
        """Преобразует сырое websocket-сообщение со стаканом в унифицированный формат."""
        data = raw_msg["data"]
        bids = data["levels"][0][:limit]
        asks = data["levels"][1][:limit]

        return [
            PartialBookDepthDict(
                t=int(data["time"]),
                u=int(data["time"]),
                b=[(float(level["px"]), float(level["sz"])) for level in bids],
                a=[(float(level["px"]), float(level["sz"])) for level in asks],
            )
        ]
