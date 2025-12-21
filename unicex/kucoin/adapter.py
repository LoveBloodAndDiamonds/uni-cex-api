__all__ = ["Adapter"]

from typing import Any

from unicex.types import (
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
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"]
            for item in raw_data["data"]["list"]
            if item["symbol"].endswith("USDT") or not only_usdt
        ]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"]
            for item in raw_data["data"]["list"]
            if item["symbol"].endswith("USDTM") or not only_usdt
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """

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
        """Преобразует сырой ответ, в котором содержатся данные о последней цене, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {
            item["symbol"]: float(item["lastPrice"])
            for item in raw_data["data"]["list"]
            if item["lastPrice"]
        }

    @staticmethod
    def open_interest(raw_data: dict[str, Any]) -> OpenInterestDict:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь, где ключ - тикер, а значение - агрегированные данные открытого интереса.
        """
        return {
            item["symbol"]: OpenInterestItem(
                t=item["ts"],
                v=float(item["openInterest"]) * Adapter._get_contract_size(item["symbol"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        """Преобразует историю ставок финансирования в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - актуальная ставка финансирования.
        """
        symbol = raw_data["data"]["symbol"]
        history = raw_data["data"]["list"]
        if not history:
            return {}

        last_point = max(history, key=lambda item: int(item["ts"]))
        return {symbol: float(last_point["fundingRate"]) * 100}

    @staticmethod
    def _get_contract_size(symbol: str) -> float:
        """Возвращает размер контракта для указанного символа тикера."""
        try:
            return ExchangeInfo.get_futures_ticker_info(symbol)["contract_size"] or 1
        except:  # noqa
            return 1

    @staticmethod
    def klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        """Преобразует данные о свечах в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список свечей.
        """
        klines: list[KlineDict] = []
        for item in sorted(raw_data["data"]["list"], key=lambda x: int(float(x[0]))):
            klines.append(  # noqa: PERF401
                KlineDict(
                    s=symbol,
                    t=item[0],
                    o=float(item[1]),
                    h=float(item[3]),
                    l=float(item[4]),
                    c=float(item[2]),
                    v=float(item[5]),
                    q=float(item[6]),
                    T=None,
                    x=None,
                )
            )
        return klines
