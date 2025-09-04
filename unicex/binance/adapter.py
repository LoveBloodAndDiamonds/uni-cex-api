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
    def ticker_24h(raw_data: list[dict]) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, Ticker24hStats]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.

        Пример возвращаемого значения:
            ```python
            {
                "BTCUSDT": {
                    "p": 0.01,
                    "v": 1000000,
                    "c": 1000,
                },
                "ETHUSDT": {
                    "p": 0.02,
                    "v": 500000,
                    "c": 5000,
                },
            }
        ```
        """
        return {
            item["symbol"]: TickerDailyDict(
                p=float(item["priceChangePercent"]),
                q=float(item["quoteVolume"]),
                v=float(item["volume"]),
            )
            for item in raw_data
        }

    @staticmethod
    def futures_ticker_24h(raw_data: list[dict]) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, Ticker24hStats]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.

        Пример возвращаемого значения:
            ```python
            {
                "BTCUSDT": {
                    "p": 0.01,
                    "v": 1000,
                    "q": 100000,
                },
                "ETHUSDT": {
                    "p": 0.02,
                    "v": 5000,
                    "q": 500000,
                },
            }
        ```
        """
        return BinanceAdapter.ticker_24h(raw_data)

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
        """
        return {item["symbol"]: float(item["price"]) for item in raw_data}

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.
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
                t=item[0],
                o=float(item[1]),
                h=float(item[2]),
                l=float(item[3]),
                c=float(item[4]),
                v=float(item[7]),
                T=item[6],
                x=None,
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
