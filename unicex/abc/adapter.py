from abc import ABC, abstractmethod
from typing import Any

from unicex.types import KlineDict, TickerDailyDict


class IAdapter(ABC):
    """Интерфейс для создания адаптеров, которые преобразовывают ответы с бирж в унифицированный формат."""

    @staticmethod
    @abstractmethod
    def tickers(raw_data: Any, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @staticmethod
    @abstractmethod
    def futures_tickers(raw_data: Any, only_usdt: bool) -> list[str]:
        """Преобразует сырой ответ, в котором содержатся данные о тикерах в список тикеров.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            list[str]: Список тикеров.
        """

    @staticmethod
    @abstractmethod
    def ticker_24h(raw_data: Any, only_usdt: bool) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """

    @staticmethod
    @abstractmethod
    def futures_ticker_24h(raw_data: Any, only_usdt: bool) -> dict[str, TickerDailyDict]:
        """Преобразует сырой ответ, в котором содержатся данные о тикере за последние 24 часа в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Флаг, указывающий, нужно ли включать только тикеры в паре к USDT.

        Возвращает:
            dict[str, TickerDailyDict]: Словарь, где ключ - тикер, а значение - статистика за последние 24 часа.
        """

    @staticmethod
    @abstractmethod
    def last_price(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """

    @staticmethod
    @abstractmethod
    def futures_last_price(raw_data: Any) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о последних ценах тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - последняя цена.
        """

    @staticmethod
    @abstractmethod
    def klines(raw_data: Any) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """

    @staticmethod
    @abstractmethod
    def futures_klines(raw_data: Any) -> list[KlineDict]:
        """Преобразует сырой ответ, в котором содержатся данные о котировках тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.

        Возвращает:
            list[KlineDict]: Список словарей, где каждый словарь содержит данные о свече.
        """

    @staticmethod
    @abstractmethod
    def funding_rate(raw_data: Any, only_usdt: bool = True) -> dict[str, float]:
        """Преобразует сырой ответ, в котором содержатся данные о ставках финансирования тикеров в унифицированный формат.

        Параметры:
            raw_data (Any): Сырой ответ с биржи.
            only_usdt (bool): Если True, то возвращаются только ставки для USDT-тикеров.

        Возвращает:
            dict[str, float]: Словарь, где ключ - тикер, а значение - ставка финансирования.
        """
