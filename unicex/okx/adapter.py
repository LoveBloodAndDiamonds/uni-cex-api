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
    """Адаптер для унификации данных с Okx API."""

    @staticmethod
    def tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        """Преобразует сырые данные о тикерах в список унифицированных символов.

        Параметры:
            raw_data (`dict`): Сырой ответ от OKX.
            only_usdt (`bool`): Возвращать только тикеры в паре с USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        return [
            item["instId"]
            for item in raw_data["data"]
            if only_usdt or item["instId"].endswith("-USDT")
        ]

    @staticmethod
    def futures_tickers(raw_data: dict, only_usdt: bool = True) -> list[str]:
        """Преобразует сырые данные о тикерах в список унифицированных символов.

        Параметры:
            raw_data (`dict`): Сырой ответ от OKX.
            only_usdt (`bool`): Возвращать только тикеры в паре с USDT.

        Возвращает:
            `list[str]`: Список тикеров.
        """
        return [
            item["instId"]
            for item in raw_data["data"]
            if only_usdt or item["instId"].endswith("-USDT-SWAP")
        ]

    @staticmethod
    def ticker_24hr(raw_data: dict) -> TickerDailyDict:
        """Преобразует статистику 24ч в унифицированный формат."""
        return {
            item["instId"]: TickerDailyItem(
                p=round(
                    (float(item["last"]) - float(item["open24h"]) / float(item["open24h"])) * 100, 2
                ),
                v=float(item["vol24h"]),
                q=float(item["volCcy24h"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def futures_ticker_24hr(raw_data: dict) -> TickerDailyDict:
        """Преобразует статистику 24ч в унифицированный формат."""
        return {
            item["instId"]: TickerDailyItem(
                p=round(
                    (float(item["last"]) - float(item["open24h"]) / float(item["open24h"])) * 100, 2
                ),
                v=float(item["volCcy24h"]),
                q=float(item["vol24h"]),
            )
            for item in raw_data["data"]
        }

    @staticmethod
    def last_price(raw_data: dict) -> dict[str, float]:
        """Преобразует данные о последней цене в унифицированный формат."""
        return {item["instId"]: float(item["last"]) for item in raw_data["data"]}

    @staticmethod
    def klines(raw_data: dict, symbol: str) -> list[KlineDict]:
        """Преобразует данные о свечах в унифицированный формат."""
        return [
            KlineDict(
                s=symbol,
                t=int(kline[0]),
                o=float(kline[1]),
                h=float(kline[2]),
                l=float(kline[3]),
                c=float(kline[4]),
                v=float(kline[6]),
                q=float(kline[7]),
                T=None,
                x=bool(int(kline[8])),
            )
            for kline in sorted(
                raw_data["data"],
                key=lambda x: int(x[0]),
            )
        ]

    @staticmethod
    def funding_rate(raw_data: dict) -> dict[str, float]:
        """Преобразует данные о ставках финансирования в унифицированный формат."""
        data = raw_data["data"][0]
        return {data["instId"]: float(data["fundingRate"]) * 100}

    @staticmethod
    def open_interest(raw_data: dict) -> OpenInterestDict:
        """Преобразует данные об открытом интересе в унифицированный формат."""
        return {
            item["instId"]: OpenInterestItem(
                t=int(item["ts"]),
                v=float(item["oiCcy"]),
            )
            for item in raw_data["data"]
        }
