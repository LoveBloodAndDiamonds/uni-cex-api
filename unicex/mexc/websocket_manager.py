__all__ = ["WebsocketManager"]

import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

import orjson
from google.protobuf.json_format import MessageToDict

from unicex._base import Websocket

from ._spot_ws_proto import PushDataV3ApiWrapper
from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Mexc."""

    _SPOT_URL: str = "wss://wbs-api.mexc.com/ws"
    """Базовый URL для вебсокета на спот."""

    _FUTURES_URL: str = "wss://contract.mexc.com/edge"
    """Базовый URL для вебсокета на фьючерсы."""

    class _MexcProtobufDecoder:
        """Класс для декодирования сообщений в формате Protobuf со спотового рынка Mexc."""

        def decode(self, message: Any) -> dict:
            if isinstance(message, bytes):
                wrapper = PushDataV3ApiWrapper()  # noqa
                wrapper.ParseFromString(message)
                return MessageToDict(wrapper, preserving_proto_field_name=True)  # type: ignore
            elif isinstance(message, str):
                return orjson.loads(message)
            else:
                raise ValueError(f"Invalid message type: {type(message)}")

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Mexc.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _generate_subscription_message(
        self,
        channel_template: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        **template_kwargs: Any,
    ) -> list[str]:
        """Сформировать сообщение для подписки на вебсокет."""
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        if symbol:
            params = [channel_template.format(symbol=symbol, **template_kwargs)]
        elif symbols:
            params = [
                channel_template.format(symbol=symbol, **template_kwargs) for symbol in symbols
            ]

        return [json.dumps({"method": "SUBSCRIPTION", "params": params})]

    def _generate_futures_subscription_message(
        self,
        topic: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        require_symbol: bool = True,
        **additional_params_kwargs: Any,
    ) -> list[str]:
        """Сформировать сообщение для подписки на фьючерсный вебсокет."""
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if require_symbol and not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        if symbol:
            symbols = [symbol]
        if symbols:
            return [
                json.dumps({"method": topic, "param": {"symbol": s, **additional_params_kwargs}})
                for s in symbols
            ]  # type: ignore
        return [json.dumps({"method": topic, "param": {**additional_params_kwargs}})]

    def _create_websocket(
        self, callback: CallbackType, subscription_messages: list[str]
    ) -> Websocket:
        """Шорткат для создания вебсокета."""
        return Websocket(
            callback=callback,
            url=self._SPOT_URL,
            subscription_messages=subscription_messages,
            decoder=self._MexcProtobufDecoder,
            ping_message='{"method": "PING"}',
            **self._ws_kwargs,
        )

    def _create_futures_websocket(
        self, callback: CallbackType, subscription_messages: list[str]
    ) -> Websocket:
        """Шорткат для создания фьючерсного вебсокета."""
        return Websocket(
            callback=callback,
            url=self._FUTURES_URL,
            subscription_messages=subscription_messages,
            ping_message='{"method": "ping"}',
            **self._ws_kwargs,
        )

    def trade(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        update_interval: Literal["100ms", "10ms"] = "100ms",
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#trade-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            update_interval (`Literal["100ms", "10ms"]`): Интервал обновления.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.aggre.deals.v3.api.pb@{update_interval}@{symbol}",
            symbol=symbol,
            symbols=symbols,
            update_interval=update_interval,
        )
        return self._create_websocket(callback, subscription_messages)

    def klines(
        self,
        callback: CallbackType,
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения K-line (candlestick) данных.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#k-line-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            interval (`Literal[...]`): Интервал K-line.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.kline.v3.api.pb@{symbol}@{interval}",
            symbol=symbol,
            symbols=symbols,
            interval=interval,
        )
        return self._create_websocket(callback, subscription_messages)

    def diff_depth(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        update_speed: Literal["100ms", "10ms"] = "100ms",
    ) -> Websocket:
        """Создает вебсокет для получения инкрементальных изменений в книге заявок.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#diff-depth-stream

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            update_speed (`Literal["100ms", "10ms"]`): Скорость обновления данных.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.aggre.depth.v3.api.pb@{update_speed}@{symbol}",
            symbol=symbol,
            symbols=symbols,
            update_speed=update_speed,
        )
        return self._create_websocket(callback, subscription_messages)

    def partial_depth(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        levels: Literal["5", "10", "20"] = "5",
    ) -> Websocket:
        """Создает вебсокет для получения ограниченной глубины книги заявок.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#partial-book-depth-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            levels (`Literal["5", "10", "20"]`): Количество уровней глубины.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.limit.depth.v3.api.pb@{symbol}@{levels}",
            symbol=symbol,
            symbols=symbols,
            levels=levels,
        )
        return self._create_websocket(callback, subscription_messages)

    def book_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        update_speed: Literal["100ms", "10ms"] = "100ms",
    ) -> Websocket:
        """Создает вебсокет для получения лучших цен покупки и продажи в реальном времени.

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#individual-symbol-book-ticker-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            update_speed (`Literal["100ms", "10ms"]`): Скорость обновления данных.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.aggre.bookTicker.v3.api.pb@{update_speed}@{symbol}",
            symbol=symbol,
            symbols=symbols,
            update_speed=update_speed,
        )
        return self._create_websocket(callback, subscription_messages)

    def book_ticker_batch(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучших цен покупки и продажи (батч версия).

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#individual-symbol-book-ticker-streams-batch-aggregation

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_subscription_message(
            channel_template="spot@public.bookTicker.batch.v3.api.pb@{symbol}",
            symbol=symbol,
            symbols=symbols,
        )
        return self._create_websocket(callback, subscription_messages)

    def futures_tickers(
        self,
        callback: CallbackType,
    ) -> Websocket:
        """Создает вебсокет для получения тикеров всех фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.tickers", require_symbol=False
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_ticker(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения тикера конкретных фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.ticker", symbol=symbol, symbols=symbols
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_depth(
        self,
        callback: CallbackType,
        limit: Literal[5, 10, 20] | None = None,
        is_full: bool = False,
        compress: bool = False,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения глубины рынка фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            limit (`Literal[5, 10, 20] | None`): Количество уровней в стакане заявок.
            is_full (`bool`): Получать полную глубину рынка.
            compress (`bool`): Использовать сжатие данных.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        additional_params = {}
        if limit:
            additional_params["limit"] = limit
        if compress:
            additional_params["compress"] = compress
        topic = "sub.depth"
        if is_full:
            topic += ".full"
        subscription_messages = self._generate_futures_subscription_message(
            topic=topic, symbol=symbol, symbols=symbols, **additional_params
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_kline(
        self,
        callback: CallbackType,
        interval: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечных данных фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            interval (`str`): Временной интервал для свечей.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.deal", symbol=symbol, symbols=symbols, interval=interval
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def funding_rate(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения ставки финансирования фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.funding.rate", symbol=symbol, symbols=symbols
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_index_price(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения индексной цены фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.index.price", symbol=symbol, symbols=symbols
        )
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_fair_price(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения справедливой цены фьючерсных контрактов.

        https://mexcdevelop.github.io/apidocs/contract_v1_en/#public-channels

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Символ фьючерсного контракта.
            symbols (`Sequence[str] | None`): Последовательность символов фьючерсных контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_messages = self._generate_futures_subscription_message(
            topic="sub.fair.price", symbol=symbol, symbols=symbols
        )
        return self._create_futures_websocket(callback, subscription_messages)
