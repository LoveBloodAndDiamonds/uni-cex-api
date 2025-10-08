__all__ = ["WebsocketManager"]

import json
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Literal

import orjson

from unicex._base import Websocket

from ._spot_ws_proto import PushDataV3ApiWrapper
from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Mexc."""

    _BASE_SPOT_URL: str = "wss://wbs-api.mexc.com/ws"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://contract.mexc.com/edge"
    """Базовый URL для вебсокета на фьючерсы."""

    class _MexcProtobufDecoder:
        """Класс для декодирования сообщений в формате Protobuf со спотового рынка Mexc."""

        def decode(self, message: Any) -> dict:
            if isinstance(message, bytes):
                wrapper = PushDataV3ApiWrapper()  # noqa
                wrapper.ParseFromString(message)
                print(wrapper)
                return wrapper  # type: ignore
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
        market_type: str,
        channel: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
    ) -> list[str]:
        """Сформировать сообщение для подписки на вебсокет."""
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        subscription_messages = []

        if symbol:
            params = [f"{market_type}@{channel}@{symbol}"]
            subscription_messages.append(json.dumps({"method": "SUBSCRIPTION", "params": params}))
        elif symbols:
            for symbol in symbols:
                params = [f"{market_type}@{channel}@{symbol}"]
                subscription_messages.append(
                    json.dumps({"method": "SUBSCRIPTION", "params": params})
                )

        return subscription_messages

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
            market_type="spot",
            channel=f"public.aggre.deals.v3.api.pb@{update_interval}",
            symbol=symbol,
            symbols=symbols,
        )
        return Websocket(
            callback=callback,
            url=self._BASE_SPOT_URL,
            subscription_messages=subscription_messages,
            decoder=self._MexcProtobufDecoder,
            ping_message='{"method": "PING"}',
            **self._ws_kwargs,
        )

    def klines(
        self,
        callback: CallbackType,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        interval: str = "Min1",
    ) -> Websocket:
        """Создает вебсокет для получения свечных данных (K-line).

        https://mexcdevelop.github.io/apidocs/spot_v3_en/#k-line-streams

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbol (`str | None`): Один символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.
            interval (`str`): Интервал свечей. Доступные: Min1, Min5, Min15, Min30, Min60, Hour4, Hour8, Day1, Week1, Month1.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")

        subscription_messages = []

        if symbol:
            params = [f"spot@public.kline.v3.api.pb@{symbol}@{interval}"]
            subscription_messages.append(json.dumps({"method": "SUBSCRIPTION", "params": params}))
        elif symbols:
            for sym in symbols:
                params = [f"spot@public.kline.v3.api.pb@{sym}@{interval}"]
                subscription_messages.append(
                    json.dumps({"method": "SUBSCRIPTION", "params": params})
                )

        return Websocket(
            callback=callback,
            url=self._BASE_SPOT_URL,
            subscription_messages=subscription_messages,
            decoder=self._MexcProtobufDecoder,
            **self._ws_kwargs,
        )
