__all__ = ["WebsocketManager"]


import json
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Okx."""

    _BASE_URL = "wss://ws.okx.com:8443/ws"
    """Базовый URL вебсокетов на Okx."""

    _PUBLIC_URL = _BASE_URL + "/v5/public"
    """Публичный URL вебсокетов на Okx."""

    _BUSINESS_URL = _BASE_URL + "/v5/business"
    """Бизнес-URL вебсокетов на Okx. (для топиков trades-all и candle)"""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для OKX.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = {"ping_message": "ping", **ws_kwargs}

    def instruments(
        self,
        callback: CallbackType,
        inst_type: Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"],
    ) -> Websocket:
        """Создает вебсокет для получения изменений в состоянии инструментов.

        https://www.okx.com/docs-v5/en/#public-data-websocket-instruments-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_type (`Literal["SPOT", "MARGIN", "SWAP", "FUTURES", "OPTION"]`): Тип инструмента.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "instruments",
                        "instType": inst_type,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def open_interest(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных об открытом интересе.

        https://www.okx.com/docs-v5/en/#public-data-websocket-open-interest-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "LTC-USD-SWAP").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "open-interest",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def funding_rate(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных о ставке финансирования.

        https://www.okx.com/docs-v5/en/#public-data-websocket-funding-rate-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "BTC-USD-SWAP").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "funding-rate",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def price_limit(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения максимальной цены покупки и минимальной цены продажи инструментов.

        https://www.okx.com/docs-v5/en/#public-data-websocket-price-limit-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "LTC-USD-190628").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "price-limit",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def option_summary(
        self,
        callback: CallbackType,
        inst_family: str,
    ) -> Websocket:
        """Создает вебсокет для получения детальной информации о ценах всех OPTION контрактов.

        https://www.okx.com/docs-v5/en/#public-data-websocket-option-summary-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_family (`str`): Семейство инструментов (например, "BTC-USD").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "opt-summary",
                        "instFamily": inst_family,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def estimated_price(
        self,
        callback: CallbackType,
        inst_type: Literal["OPTION", "FUTURES"],
        inst_family: str | None = None,
        inst_id: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения расчетной цены поставки/исполнения/расчета для FUTURES и OPTION контрактов.

        https://www.okx.com/docs-v5/en/#public-data-websocket-estimated-delivery-exercise-settlement-price-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_type (`Literal["OPTION", "FUTURES"]`): Тип инструмента.
            inst_family (`str | None`): Семейство инструментов (например, "BTC-USD"). Обязателен либо inst_family, либо inst_id.
            inst_id (`str | None`): ID инструмента. Обязателен либо inst_family, либо inst_id.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if not inst_family and not inst_id:
            raise ValueError("Either inst_family or inst_id must be provided")
        if inst_family and inst_id:
            raise ValueError("Only one of inst_family or inst_id should be provided")

        args: dict[str, str] = {
            "channel": "estimated-price",
            "instType": inst_type,
        }

        if inst_family:
            args["instFamily"] = inst_family
        if inst_id:
            args["instId"] = inst_id

        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [args],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def mark_price(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения маркировочной цены.

        https://www.okx.com/docs-v5/en/#public-data-websocket-mark-price-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "LTC-USD-190628").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "mark-price",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def index_tickers(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных индексных тикеров.

        https://www.okx.com/docs-v5/en/#public-data-websocket-index-tickers-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): Индекс с USD, USDT, BTC, USDC в качестве котируемой валюты (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "index-tickers",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def mark_price_candlesticks(
        self,
        callback: CallbackType,
        interval: Literal[
            "3M",
            "1M",
            "1W",
            "1D",
            "2D",
            "3D",
            "5D",
            "12H",
            "6H",
            "4H",
            "2H",
            "1H",
            "30m",
            "15m",
            "5m",
            "3m",
            "1m",
            "1Yutc",
            "3Mutc",
            "1Mutc",
            "1Wutc",
            "1Dutc",
            "2Dutc",
            "3Dutc",
            "5Dutc",
            "12Hutc",
            "6Hutc",
        ],
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных свечей маркировочной цены.

        https://www.okx.com/docs-v5/en/#public-data-websocket-mark-price-candlesticks-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`Literal`): Интервал свечей.
            inst_id (`str`): ID инструмента (например, "BTC-USD-190628").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        channel = f"mark-price-candle{interval}"
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": channel,
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._BUSINESS_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def index_candlesticks(
        self,
        callback: CallbackType,
        interval: Literal[
            "3M",
            "1M",
            "1W",
            "1D",
            "2D",
            "3D",
            "5D",
            "12H",
            "6H",
            "4H",
            "2H",
            "1H",
            "30m",
            "15m",
            "5m",
            "3m",
            "1m",
            "3Mutc",
            "1Mutc",
            "1Wutc",
            "1Dutc",
            "2Dutc",
            "3Dutc",
            "5Dutc",
            "12Hutc",
            "6Hutc",
        ],
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных свечей индекса.

        https://www.okx.com/docs-v5/en/#public-data-websocket-index-candlesticks-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`Literal`): Интервал свечей.
            inst_id (`str`): Индекс (например, "BTC-USD").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        channel = f"index-candle{interval}"
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": channel,
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._BUSINESS_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def liquidation_orders(
        self,
        callback: CallbackType,
        inst_type: Literal["SWAP", "FUTURES", "MARGIN", "OPTION"],
    ) -> Websocket:
        """Создает вебсокет для получения недавних ордеров ликвидации.

        https://www.okx.com/docs-v5/en/#public-data-websocket-liquidation-orders-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_type (`Literal["SWAP", "FUTURES", "MARGIN", "OPTION"]`): Тип инструмента.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "liquidation-orders",
                        "instType": inst_type,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def adl_warning(
        self,
        callback: CallbackType,
        inst_type: Literal["SWAP", "FUTURES", "OPTION"],
        inst_family: str | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения предупреждений об авто-делевередже.

        https://www.okx.com/docs-v5/en/#public-data-websocket-adl-warning-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_type (`Literal["SWAP", "FUTURES", "OPTION"]`): Тип инструмента.
            inst_family (`str | None`): Семейство инструментов (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        args: dict[str, str] = {
            "channel": "adl-warning",
            "instType": inst_type,
        }

        if inst_family:
            args["instFamily"] = inst_family

        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [args],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def tickers(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения последней цены сделки, цены bid, цены ask и 24-часового объема торгов.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-tickers-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "tickers",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def candlesticks(
        self,
        callback: CallbackType,
        interval: Literal[
            "3M",
            "1M",
            "1W",
            "1D",
            "2D",
            "3D",
            "5D",
            "12H",
            "6H",
            "4H",
            "2H",
            "1H",
            "30m",
            "15m",
            "5m",
            "3m",
            "1m",
            "1s",
            "3Mutc",
            "1Mutc",
            "1Wutc",
            "1Dutc",
            "2Dutc",
            "3Dutc",
            "5Dutc",
            "12Hutc",
            "6Hutc",
        ],
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных свечей инструмента.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-candlesticks-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`Literal`): Интервал свечей.
            inst_id (`str`): ID инструмента (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        channel = f"candle{interval}"
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": channel,
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._BUSINESS_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def trades(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных о последних сделках.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-trades-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "trades",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def all_trades(
        self,
        callback: CallbackType,
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных о всех сделках (по одной сделке на обновление).

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-all-trades-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            inst_id (`str`): ID инструмента (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": "trades-all",
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._BUSINESS_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def order_book(
        self,
        callback: CallbackType,
        channel: Literal["books", "books5", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"],
        inst_id: str,
    ) -> Websocket:
        """Создает вебсокет для получения данных ордербука.

        https://www.okx.com/docs-v5/en/#order-book-trading-market-data-ws-order-book-channel

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            channel (`Literal["books", "books5", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"]`): Тип канала ордербука.
            inst_id (`str`): ID инструмента (например, "BTC-USDT").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = json.dumps(
            {
                "op": "subscribe",
                "args": [
                    {
                        "channel": channel,
                        "instId": inst_id,
                    }
                ],
            }
        )

        return Websocket(
            callback=callback,
            url=self._PUBLIC_URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )
