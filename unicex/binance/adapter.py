__all__ = ["Adapter"]


from unicex.types import (
    AggTradeDict,
    KlineDict,
    OpenInterestItem,
    TickerDailyDict,
    TickerDailyItem,
    TradeDict,
)
from unicex.utils import catch_adapter_errors


class Adapter:
    """Адаптер для унификации данных с Binance API."""

    @staticmethod
    @catch_adapter_errors
    def tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return [
            item["symbol"] for item in raw_data if not only_usdt or item["symbol"].endswith("USDT")
        ]

    @staticmethod
    @catch_adapter_errors
    def futures_tickers(raw_data: list[dict], only_usdt: bool = True) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        return Adapter.tickers(raw_data, only_usdt)

    @staticmethod
    @catch_adapter_errors
    def ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return {
            item["symbol"]: TickerDailyItem(
                p=float(item["priceChangePercent"]),
                q=float(item["quoteVolume"]),  # объём в долларах
                v=float(item["volume"]),  # объём в монетах
            )
            for item in raw_data
        }

    @staticmethod
    @catch_adapter_errors
    def futures_ticker_24hr(raw_data: list[dict]) -> TickerDailyDict:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            TickerDailyDict: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return Adapter.ticker_24hr(raw_data)

    @staticmethod
    @catch_adapter_errors
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return {item["symbol"]: float(item["price"]) for item in raw_data}

    @staticmethod
    @catch_adapter_errors
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return Adapter.last_price(raw_data)

    @staticmethod
    @catch_adapter_errors
    def klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return [
            KlineDict(
                s="",
                t=item[0],
                o=float(item[1]),
                h=float(item[2]),
                l=float(item[3]),
                c=float(item[4]),
                v=float(item[5]),
                q=float(item[7]),
                T=item[6],
                x=None,
            )
            for item in raw_data
        ]

    @staticmethod
    @catch_adapter_errors
    def futures_klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return Adapter.klines(raw_data)

    @staticmethod
    @catch_adapter_errors
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования тикеров в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        return {item["symbol"]: float(item["lastFundingRate"]) * 100 for item in raw_data}

    @staticmethod
    @catch_adapter_errors
    def klines_message(raw_msg: dict) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        # Обрабатываем обертку в случае с multiplex stream
        kline = raw_msg.get("data", raw_msg)["k"]
        return [
            KlineDict(
                s=kline["s"],
                t=kline["t"],
                o=float(kline["o"]),
                h=float(kline["h"]),
                l=float(kline["l"]),
                c=float(kline["c"]),
                v=float(kline["v"]),  # Используем quote volume (в USDT)
                q=float(kline["q"]),  # Используем quote volume (в USDT)
                T=kline["T"],
                x=kline["x"],
            )
        ]

    @staticmethod
    @catch_adapter_errors
    def futures_klines_message(raw_msg: dict) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return Adapter.klines_message(raw_msg)

    @staticmethod
    @catch_adapter_errors
    def aggtrades_message(raw_msg: dict) -> list[AggTradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        msg = raw_msg.get("data", raw_msg)
        return [
            AggTradeDict(
                t=int(msg["T"]),
                s=str(msg["s"]),
                S="SELL" if bool(msg["m"]) else "BUY",
                p=float(msg["p"]),
                v=float(msg["q"]),
            )
        ]

    @staticmethod
    @catch_adapter_errors
    def futures_aggtrades_message(raw_msg: dict) -> list[AggTradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        return Adapter.aggtrades_message(raw_msg)

    @staticmethod
    @catch_adapter_errors
    def trades_message(raw_msg: dict) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        msg = raw_msg.get("data", raw_msg)
        return [
            TradeDict(
                t=int(msg["T"]),
                s=str(msg["s"]),
                S="SELL" if bool(msg["m"]) else "BUY",
                p=float(msg["p"]),
                v=float(msg["q"]),
            )
        ]

    @staticmethod
    @catch_adapter_errors
    def futures_trades_message(raw_msg: dict) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        return Adapter.trades_message(raw_msg)

    @staticmethod
    @catch_adapter_errors
    def open_interest(raw_data: dict) -> OpenInterestItem:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        объеме открытых позиций в унифицированный вид.

        Параметры:
            raw_data (Any): Сырое сообщение с вебсокета.

        Возвращает:
            OpenInterestItem: Словарь со временем и объемом открытого интереса в монетах.
        """
        return OpenInterestItem(t=raw_data["time"], v=float(raw_data["openInterest"]))
