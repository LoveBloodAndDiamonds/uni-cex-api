from typing import Any

from unicex._abc import IAdapter
from unicex.exceptions import AdapterError
from unicex.types import AggTradeDict, KlineDict, TickerDailyDict, TradeDict


class Adapter(IAdapter):
    """Преобразовываeт ответы с бирж в унифицированный формат."""

    @staticmethod
    def tickers(raw_data: Any, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        try:
            data = raw_data.get("data", [])
            return [
                item["symbol"] for item in data if not only_usdt or item["symbol"].endswith("USDT")
            ]
        except Exception as e:
            raise AdapterError(f"({type(e)}): {e}. Can not convert {raw_data} to tickers.") from e

    @staticmethod
    def futures_tickers(raw_data: Any, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """
        raise NotImplementedError()

    @staticmethod
    def ticker_24h(raw_data: Any) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        try:
            return {
                item["symbol"]: TickerDailyDict(
                    p=round(float(item["change24h"]) * 100, 2),  # конвертируем в проценты
                    v=float(item["baseVolume"]),  # объём в COIN
                    q=float(item["usdtVolume"]),  # объём в USDT
                )
                for item in raw_data.get("data", [])
            }
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_data} to ticker 24h."
            ) from e

    @staticmethod
    def futures_ticker_24h(raw_data: Any) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """
        raise NotImplementedError()

    @staticmethod
    def last_price(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_last_price(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров
        в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """
        raise NotImplementedError()

    @staticmethod
    def klines(raw_data: Any) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в
        унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_klines(raw_data: Any) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в
        унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        raise NotImplementedError()

    @staticmethod
    def funding_rate(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования
        тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
        raise NotImplementedError()

    @staticmethod
    def klines_message(raw_msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_klines_message(raw_msg: Any) -> list[KlineDict]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        свече/свечах в унифицированный вид.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """
        raise NotImplementedError()

    @staticmethod
    def aggtrades_message(raw_msg: Any) -> list[AggTradeDict]:
        """Преобразует сырое сообщение вебсокета с агрегированными сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[AggTradeDict]: Список сделок в унифицированном формате.
        """
        raise NotImplementedError()

    @staticmethod
    def futures_aggtrades_message(raw_msg: Any) -> list[AggTradeDict]:
        """Преобразует сырое сообщение вебсокета с агрегированными сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[AggTradeDict]: Список сделок в унифицированном формате.
        """
        raise NotImplementedError()

    @staticmethod
    def trades_message(raw_msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение вебсокета со сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[TradeDict]: Список сделок в унифицированном формате.
        """
        try:
            symbol = raw_msg["arg"]["instId"]

            return [
                AggTradeDict(
                    t=int(trade["ts"]),
                    s=symbol,
                    S=trade["side"].upper(),
                    p=float(trade["price"]),
                    v=float(trade["size"]),
                )
                for trade in raw_msg["data"]
            ]
        except Exception as e:
            raise AdapterError(
                f"({type(e)}): {e}. Can not convert {raw_msg} to unified aggtrades."
            ) from e

    @staticmethod
    def futures_trades_message(raw_msg: Any) -> list[TradeDict]:
        """Преобразует сырое сообщение вебсокета со сделками в унифицированный формат.

        Параметры:
            raw_msg (Any): Сырое сообщение с вебсокета.

        Возвращает:
            list[TradeDict]: Список сделок в унифицированном формате.
        """
        raise NotImplementedError()

    @staticmethod
    def open_interest(raw_data: Any) -> float | dict[str, float]:
        """Преобразует сырое сообщение с вебсокета, в котором содержится информация о
        объеме открытых позиций в унифицированный вид.

        Параметры:
            raw_data (Any): Сырое сообщение с вебсокета.

        Возвращает:
            float | dict[str, float]: Объем открытых позиций в монетах или словарь,
            где ключи - название тикера, а значения - объемы открытых позиций в монетах.
        """
        raise NotImplementedError()
