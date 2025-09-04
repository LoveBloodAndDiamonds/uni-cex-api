__all__ = ["BinanceAdapter"]

from unicex.abstract import IAdapter
from unicex.types import KlineDict, TickerDailyDict


class BinanceAdapter(IAdapter):
    """Адаптер для унификации данных с Binance API."""

    @staticmethod
    def tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        if only_usdt:
            return [item["symbol"] for item in raw_data if item["symbol"].endswith("USDT")]
        return [item["symbol"] for item in raw_data]

    @staticmethod
    def futures_tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return BinanceAdapter.tickers(raw_data, only_usdt)

    @staticmethod
    def ticker_24h(raw_data: list[dict], only_usdt: bool = True) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDaily]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        if only_usdt:
            result = {}
            for item in raw_data:
                symbol = item["symbol"]
                if symbol.endswith("USDT"):
                    result[symbol] = TickerDailyDict(
                        p=float(item["priceChangePercent"]),
                        q=float(item["quoteVolume"]),  # Объем торгов в долларах
                        v=float(item["volume"]),  # Объем торгов в монетах
                    )
        else:
            result = {
                item["symbol"]: TickerDailyDict(
                    p=float(item["priceChangePercent"]),
                    q=float(item["quoteVolume"]),  # Объем торгов в долларах
                    v=float(item["volume"]),  # Объем торгов в монетах
                )
                for item in raw_data
            }
        return result

    @staticmethod
    def futures_ticker_24h(
        raw_data: list[dict], only_usdt: bool = True
    ) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDaily]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return BinanceAdapter.ticker_24h(raw_data)

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["price"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return BinanceAdapter.last_price(raw_data)

    @staticmethod
    def klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                t=item[0],  # Start time
                o=float(item[1]),  # Open price
                h=float(item[2]),  # High price
                l=float(item[3]),  # Low price
                c=float(item[4]),  # Close price
                v=float(item[5]),  # Volume
                q=float(item[7]),  # Quote volume
                T=item[6],  # Close time
                x=None,  # Is closed (not provided by Binance)
            )
            for item in raw_data
        ]

    @staticmethod
    def futures_klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return BinanceAdapter.klines(raw_data)
