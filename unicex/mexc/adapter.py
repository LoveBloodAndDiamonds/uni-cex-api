__all__ = ["Adapter"]

from unicex.types import (
    KlineDict,
    OpenInterestDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
)
from unicex.utils import catch_adapter_errors, decorate_all_methods


@decorate_all_methods(catch_adapter_errors)
class Adapter:
    """Адаптер для унификации данных с Mexc API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах, в список тикеров.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [item["symbol"] for item in raw_data if only_usdt or item["symbol"].endswith("USDT")]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о фьючерсных тикерах, в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"]
            for item in raw_data["data"]
            if only_usdt or item["symbol"].endswith("USDT")
        ]

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о спотовых ценах, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о фьючерсных ценах, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["lastPrice"]) for item in raw_data["data"]}

    @staticmethod
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о статистике за 24 часа, в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
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
        """Преобразует сырой ответ, в котором содержатся данные о фьючерсной статистике за 24 часа, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return {
            item["symbol"]: TickerDailyItem(
                p=float(item["riseFallRate"]) * 100,
                v=float(item["volume24"]),
                q=float(item["amount24"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        """Преобразует сырой ответ, в котором содержатся данные об открытом интересе, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            OpenInterestDict: Словарь, где ключ - тикер, а значение - агрегированные данные открытого интереса.
        """
        return {
            item["symbol"]: OpenInterestItem(t=item["timestamp"], v=float(item["holdVol"]))
            for item in raw_data["data"]
        }

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        return {
            item["symbol"]: float(item["fundingRate"]) * 100
            for item in raw_data["data"]
            if "fundingRate" in item  # В некоторых элементах item нет ключа 'fundingRate'
        }

    @staticmethod
    def klines(raw_data: list[list], symbol: str) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о свечах, в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s=symbol,
                t=kline[0],
                o=kline[1],
                h=kline[2],
                l=kline[3],
                c=kline[4],
                v=kline[5],
                q=kline[7],
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
        """Преобразует сырой ответ, в котором содержатся данные о фьючерсных свечах, в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            symbol (str): Символ тикера.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
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
