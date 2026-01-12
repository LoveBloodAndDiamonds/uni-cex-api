from __future__ import annotations

import time
from typing import Any

__all__ = ["Adapter"]

from unicex.types import (
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
    """Адаптер для унификации данных с Gateio API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ о тикерах в список символов.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре c USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["currency_pair"]
            for item in raw_data
            if item["currency_pair"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: list[dict], only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ о фьючерсных тикерах в список символов.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре c USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["contract"]
            for item in raw_data
            if item["contract"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует данные о последних ценах (spot) в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ — тикер, а значение — последняя цена.
        """
        return {item["currency_pair"]: float(item["last"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует данные о последних ценах (futures) в унифицированный формат."""
        return {item["contract"]: float(item["last"]) for item in raw_data}

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (spot) в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ — тикер, а значение — агрегированная статистика.
        """
        return {
            item["currency_pair"]: TickerDailyItem(
                p=float(item["change_percentage"]),
                v=float(item["base_volume"]),
                q=float(item["quote_volume"]),
            )
            for item in raw_data
        }

    @staticmethod
    def futures_ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует 24-часовую статистику (futures) в унифицированный формат."""
        return {
            item["contract"]: TickerDailyItem(
                p=float(item["change_percentage"]),
                v=float(item["volume_24h_base"]),
                q=float(item["volume_24h_quote"]),
            )
            for item in raw_data
        }

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        """Преобразует данные о свечах в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
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
        """Преобразует данные о свечах в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
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
        """Преобразует данные о ставках финансирования в унифицированный формат."""
        return {
            item["contract"]: float(item["funding_rate"]) * 100
            for item in raw_data
            if item.get("funding_rate") is not None
        }

    @staticmethod
    def open_interest(raw_data: list[dict]) -> OpenInterestDict:
        """Преобразует данные об открытом интересе в унифицированный формат."""
        return {
            item["contract"]: OpenInterestItem(
                t=int(time.time() * 1000),
                v=float(item["total_size"]) * float(item["quanto_multiplier"]),
                u="coins",
            )
            for item in raw_data
        }

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        """Преобразует вебсокет-сообщение со свечами в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список свечей в унифицированном формате.
        """
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
        """Преобразует вебсокет-сообщение со свечами в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список свечей в унифицированном формате.
        """
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
        """Преобразует вебсокет-сообщение со сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[TradeDict]: Список сделок в унифицированном формате.
        """
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
        """Преобразует вебсокет-сообщение со сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[TradeDict]: Список сделок в унифицированном формате.
        """
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
    def _get_contract_size(symbol: str) -> float:
        """Возвращает размер контракта для указанного символа тикера."""
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            return 1
