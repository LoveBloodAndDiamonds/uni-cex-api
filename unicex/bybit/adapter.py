from unicex._abc import IAdapter
from unicex.types import KlineDict, TickerDailyDict


class BybitAdapter(IAdapter):
    """Адаптер для унификации данных с Bybit API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        instruments = raw_data.get("result", {}).get("list", [])
        if only_usdt:
            return [item["symbol"] for item in instruments if item["symbol"].endswith("USDT")]
        return [item["symbol"] for item in instruments]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return BybitAdapter.tickers(raw_data, only_usdt)

    @staticmethod
    def ticker_24h(raw_data: dict, only_usdt: bool = True) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        if only_usdt:
            result = {}
            for item in raw_data.get("result", {}).get("list", []):
                symbol = item["symbol"]
                if symbol.endswith("USDT"):
                    result[symbol] = TickerDailyDict(
                        p=round(
                            float(item["price24hPcnt"]) * 100, 2
                        ),  # Bybit возвращает в десятичной форме (0.01 = 1%), конвертируем в проценты
                        q=float(item["turnover24h"]),  # Объем торгов в долларах
                        v=float(item["volume24h"]),  # Объем торгов в монетах
                    )
        else:
            result = {
                item["symbol"]: TickerDailyDict(
                    p=round(
                        float(item["price24hPcnt"]) * 100, 2
                    ),  # Bybit возвращает в десятичной форме (0.01 = 1%), конвертируем в проценты
                    q=float(item["turnover24h"]),  # Объем торгов в долларах
                    v=float(item["volume24h"]),  # Объем торгов в монетах
                )
                for item in raw_data.get("result", {}).get("list", [])
            }
        return result

    @staticmethod
    def futures_ticker_24h(raw_data: dict, only_usdt: bool = True) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return BybitAdapter.ticker_24h(raw_data)

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        tickers = raw_data.get("result", {}).get("list", [])
        return {item["symbol"]: float(item["lastPrice"]) for item in tickers}

    @staticmethod
    def futures_last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return BybitAdapter.last_price(raw_data)

    @staticmethod
    def klines(raw_data: dict) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        klines = raw_data.get("result", {}).get("list", [])
        return [
            KlineDict(
                t=int(item[0]),
                o=float(item[1]),
                h=float(item[2]),
                l=float(item[3]),
                c=float(item[4]),
                v=float(item[5]),
                q=float(item[6]),
                T=None,
                x=None,
            )
            for item in klines
        ]

    @staticmethod
    def futures_klines(raw_data: dict) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return BybitAdapter.klines(raw_data)

    @staticmethod
    def funding_rate(raw_data: dict, only_usdt: bool = True) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования тикеров в унифицированный формат.

        Параметры:
            raw_data (dict): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли фильтровать только тикеры с USDT.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        if only_usdt:
            return {
                item["symbol"]: float(item["fundingRate"]) * 100
                for item in raw_data["result"]["list"]
                if item["symbol"].endswith("USDT")
            }
        else:
            return {
                item["symbol"]: float(item["fundingRate"]) * 100
                for item in raw_data["result"]["list"]
            }
