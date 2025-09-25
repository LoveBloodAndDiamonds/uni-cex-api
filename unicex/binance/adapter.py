__all__ = ["Adapter"]


from unicex._abc import IAdapter
from unicex.exceptions import AdapterError
from unicex.types import AggTradeDict, KlineDict, TickerDailyDict, TradeDict


class Adapter(IAdapter):
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
        try:
            return [
                item["symbol"]
                for item in raw_data
                if not only_usdt or item["symbol"].endswith("USDT")
            ]
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to unified tickers."
            ) from e

    @staticmethod
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
    def ticker_24h(raw_data: list[dict]) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        try:
            return {
                item["symbol"]: TickerDailyDict(
                    p=float(item["priceChangePercent"]),
                    q=float(item["quoteVolume"]),  # объём в долларах
                    v=float(item["volume"]),  # объём в монетах
                )
                for item in raw_data
            }
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to unified ticker 24h."
            ) from e

    @staticmethod
    def futures_ticker_24h(raw_data: list[dict]) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        return Adapter.ticker_24h(raw_data)

    @staticmethod
    def last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        try:
            return {item["symbol"]: float(item["price"]) for item in raw_data}
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to unified last price."
            ) from e

    @staticmethod
    def futures_last_price(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        return Adapter.last_price(raw_data)

    @staticmethod
    def klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        try:
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
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to unified kline."
            ) from e

    @staticmethod
    def futures_klines(raw_data: list[list]) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (list[list]): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        return Adapter.klines(raw_data)

    @staticmethod
    def funding_rate(raw_data: list[dict]) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования тикеров в унифицированный формат.

        Параметры:
            raw_data (list[dict]): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        try:
            return {item["symbol"]: float(item["lastFundingRate"]) * 100 for item in raw_data}
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to unified funding rate."
            ) from e

    @staticmethod
    def klines_message(raw_msg: dict) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        try:
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
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_msg} to unified kline."
            ) from e

    @staticmethod
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
    def aggtrades_message(raw_msg: dict) -> list[AggTradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        аггрегированных сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        try:
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
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_msg} to unified aggtrade."
            ) from e

    @staticmethod
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
    def trades_message(raw_msg: dict) -> list[TradeDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        сделке/сделках в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о сделке.
        """
        try:
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
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_msg} to unified trade."
            ) from e

    @staticmethod
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
    def open_interest(raw_data: dict) -> float:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        объеме открытых позиций в унифицированный вид.

        Параметры:
            raw_data (Any): Сырое сообщение с вебсокета.

        Возвращает:
            float: Объем открытых позиций в монетах.
        """
        try:
            return float(raw_data["openInterest"])
        except Exception as e:
            raise AdapterError(
                f"{type(e)}: {e}. Can not convert {raw_data} to unified open interest."
            ) from e
