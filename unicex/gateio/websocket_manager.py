__all__ = ["WebsocketManager"]


import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, Literal

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Gateio."""

    _SPOT_URL = "wss://api.gateio.ws/ws/v4/"
    """Адрес вебсокета для спотового рынка."""

    _FUTURES_URL = "wss://fx-ws.gateio.ws/v4/ws/usdt"
    """Адрес вебсокета для фьючерсного рынка."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Mexc.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = ws_kwargs

    def _build_subscription_message(
        self,
        channel: str,
        payload: list,
        event: Literal["subscribe", "unsubscribe"] = "subscribe",
    ) -> str:
        """Формирует JSON сообщение для подписки."""
        return json.dumps(
            {
                "time": int(time.time()),
                "id": int(time.time() * 1e6),
                "channel": channel,
                "event": event,
                "payload": payload,
            }
        )

    def _create_keepalive_message_callable(
        self,
        type: Literal["ping", "pong"],
        market: Literal["spot", "futures"] = "spot",
    ) -> Callable[[], str]:
        """Функция для генерации ping или pong сообщения в рантайме."""
        return lambda: json.dumps(
            {
                "time": int(time.time()),
                "channel": f"{market}.{type}",
            }
        )

    def _create_websocket(
        self,
        callback: CallbackType,
        subscription_messages: list[str],
    ) -> Websocket:
        """Шорткат для создания вебсокета."""
        return Websocket(
            callback=callback,
            url=self._SPOT_URL,
            subscription_messages=subscription_messages,
            ping_message=self._create_keepalive_message_callable("ping", "spot"),
            pong_message=self._create_keepalive_message_callable("pong", "spot"),
            **self._ws_kwargs,
        )

    def _create_futures_websocket(
        self,
        callback: CallbackType,
        subscription_messages: list[str],
    ) -> Websocket:
        """Шорткат для создания фьючерсного вебсокета."""
        return Websocket(
            callback=callback,
            url=self._FUTURES_URL,
            subscription_messages=subscription_messages,
            ping_message=self._create_keepalive_message_callable("ping", "futures"),
            pong_message=self._create_keepalive_message_callable("pong", "futures"),
            **self._ws_kwargs,
        )

    def tickers(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет с общений информацией о тикерах.

        https://www.gate.com/docs/developers/apiv4/ws/en/#tickers-channel.


        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._create_websocket(
            callback, [self._build_subscription_message("spot.tickers", symbols)]
        )

    def trades(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения публичных трейдов.

        https://www.gate.com/docs/developers/apiv4/ws/en/#public-trades-channel

        Канал `spot.trades` отправляет сообщение при каждом новом трейде (только со стороны тейкера).

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список торговых пар (например, ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_websocket(
            callback, [self._build_subscription_message("spot.trades", symbols)]
        )

    def candlesticks(
        self,
        callback: CallbackType,
        interval: str,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения данных свечей (candlesticks).

        https://www.gate.com/docs/developers/apiv4/ws/en/#candlesticks-channel

        Канал `spot.candlesticks` передаёт информацию о свечах каждые 2 секунды.

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            interval (`str`): Интервал свечей (например: "1m", "5m", "1h", "1d").
            symbols (`list[str]`): Список торговых пар (например: ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [[interval, symbol] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("spot.candlesticks", payload) for payload in payloads
        ]
        return self._create_websocket(callback, subscription_messages)

    def book_ticker(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения лучшего бид/аск (best bid / best ask).

        Документация: Best bid or ask price — канал `spot.book_ticker`.
        Канал обновляется с частотой ~10 мс.

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список торговых пар (например ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_websocket(
            callback, [self._build_subscription_message("spot.book_ticker", symbols)]
        )

    def order_book_update(
        self,
        callback: CallbackType,
        symbols: list[str],
        interval: str = "100ms",
    ) -> Websocket:
        """Открывает вебсокет для получения обновлений стакана (изменения уровней ордербука).

        https://www.gate.com/docs/developers/apiv4/ws/en/#changed-order-book-levels

        Канал `spot.order_book_update` передаёт изменения уровней стакана с частотой 20 мс или 100 мс.

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список торговых пар (например: ["BTC_USDT", "ETH_USDT"]).
            interval (`str`): Частота обновлений — "20ms" (глубина 20) или "100ms" (глубина 100). По умолчанию — "100ms".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [[symbol, interval] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("spot.order_book_update", payload)
            for payload in payloads
        ]
        return self._create_websocket(callback, subscription_messages)

    def order_book(
        self,
        callback: CallbackType,
        symbols: list[str],
        level: Literal["5", "10", "20", "50", "100"] = "20",
        interval: Literal["100ms", "1000ms"] = "1000ms",
    ) -> Websocket:
        """Открывает вебсокет для получения снапшота ордербука ограниченного уровня.

        https://www.gate.com/docs/developers/apiv4/ws/en/#limited-level-full-order-book-snapshot

        Канал `spot.order_book` передаёт полный снимок стакана (ограниченной глубины)
        с частотой 100 мс или 1000 мс.

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список торговых пар (например ["BTC_USDT", "ETH_USDT"]).
            level (`Literal["5", "10", "20", "50", "100"]`): Глубина стакана. По умолчанию — "20".
            interval (`Literal["100ms", "1000ms"]`): Частота обновлений. По умолчанию — "1000ms".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [[symbol, level, interval] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("spot.order_book", payload) for payload in payloads
        ]
        return self._create_websocket(callback, subscription_messages)

    def order_book_v2(
        self,
        callback: CallbackType,
        symbols: list[str],
        level: Literal["400", "50"] = "400",
    ) -> Websocket:
        """Открывает вебсокет для получения обновлений ордербука V2 по спотовым контрактам.

        Канал `spot.obu` передаёт изменения ордербука в формате V2.
        Формат подписки для каждого символа: ob.{symbol}.{level}.
        - Level "400": обновления каждые 100 мс
        - Level "50": обновления каждые 20 мс

        Документация: https://www.gate.com/docs/developers/apiv4/ws/en/#order-book-v2-subscription

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список спотовых торговых пар (например ["BTC_USDT", "ETH_USDT"]).
            level (`Literal["400", "50"]`): Глубина ордербука. По умолчанию — "400".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [f"ob.{symbol}.{level}" for symbol in symbols]
        return self._create_websocket(
            callback, [self._build_subscription_message("spot.obu", payloads)]
        )

    def futures_tickers(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения информации по фьючерсным контрактам.

        Канал `futures.tickers` передаёт данные о:
        - последней цене
        - максимальной/минимальной цене за день
        - дневном объёме
        - изменении цены за 24 часа

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#tickers-api

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_futures_websocket(
            callback, [self._build_subscription_message("futures.tickers", symbols)]
        )

    def futures_trades(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения информации о сделках по фьючерсным контрактам.

        Канал `futures.trades` отправляет сообщение при каждом новом трейде.
        Содержит детали сделки: цену, объём, время и тип сделки.

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#trades-api

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_futures_websocket(
            callback, [self._build_subscription_message("futures.trades", symbols)]
        )

    def futures_book_ticker(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения лучшего бид/аск (best bid / best ask) по фьючерсным контрактам.

        Канал `futures.book_ticker` передаёт обновления лучших цен бид и аск для указанных контрактов.

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#best-ask-bid-subscription

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_futures_websocket(
            callback, [self._build_subscription_message("futures.book_ticker", symbols)]
        )

    def futures_order_book_update(
        self,
        callback: CallbackType,
        symbols: list[str],
        frequency: Literal["20ms", "100ms"] = "100ms",
        level: Literal["20", "50", "100"] | None = None,
    ) -> Websocket:
        """Открывает вебсокет для получения обновлений ордербука фьючерсных контрактов.

        Канал `futures.order_book_update` передаёт изменения уровней стакана с заданной частотой.

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#order-book-update-subscription

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).
            frequency (`Literal["20ms", "100ms"]`): Частота обновлений. По умолчанию — "100ms".
            level (`Literal["20", "50", "100"] | None`): Опциональная глубина ордербука. Только для частоты 20ms разрешено "20".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [
            [symbol, frequency] + ([level] if level is not None else []) for symbol in symbols
        ]
        subscription_messages = [
            self._build_subscription_message("futures.order_book_update", payload)
            for payload in payloads
        ]
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_order_book_v2(
        self,
        callback: CallbackType,
        symbols: list[str],
        level: Literal["400", "50"] = "400",
    ) -> Websocket:
        """Открывает вебсокет для получения обновлений ордербука V2 по фьючерсным контрактам.

        Канал `futures.obu` передаёт изменения ордербука в формате V2.
        Формат подписки для каждого символа: ob.{symbol}.{level}.
        - Level "400": обновления каждые 100 мс
        - Level "50": обновления каждые 20 мс

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#order-book-v2-subscription

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).
            level (`Literal["400", "50"]`): Глубина ордербука. По умолчанию — "400".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [f"ob.{symbol}.{level}" for symbol in symbols]
        return self._create_futures_websocket(
            callback, [self._build_subscription_message("futures.obu", payloads)]
        )

    def futures_order_book(
        self,
        callback: CallbackType,
        symbols: list[str],
        limit: Literal["100", "50", "20", "10", "5", "1"] = "20",
        interval: Literal["0"] = "0",
    ) -> Websocket:
        """Открывает вебсокет для получения снапшота ордербука фьючерсных контрактов.

        Канал `futures.order_book` передаёт полный снимок стакана с указанной глубиной и интервалом.

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#legacy-order-book-subscription

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).
            limit (`Literal["100", "50", "20", "10", "5", "1"]`): Глубина ордербука. По умолчанию — "20".
            interval (`Literal["0"]`): Интервал обновления. По документации всегда "0".

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [[symbol, limit, interval] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("futures.order_book", payload) for payload in payloads
        ]
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_candlesticks(
        self,
        callback: CallbackType,
        interval: str,
        symbols: list[str],
        price_type: Literal["index", "mark"] | None = None,
    ) -> Websocket:
        """Открывает вебсокет для получения данных свечей (candlesticks) по фьючерсным контрактам.

        Канал `futures.candlesticks` передаёт информацию о свечах с указанным интервалом.
        Для подписки на специальные типы цен можно указать `price_type`:
        - "mark_" для mark price
        - "index_" для index price

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#candlesticks-api

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            interval (`str`): Интервал свечей, например "10s", "1m", "5m", "1h", "1d".
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).
            price_type (`Literal["index", "mark"] | None`): Тип цены для свечей. По умолчанию — обычные контракты.

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        if price_type:
            prefix = f"{price_type}_"
            symbols = [f"{prefix}{symbol}" for symbol in symbols]

        payloads = [[interval, symbol] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("futures.candlesticks", payload)
            for payload in payloads
        ]
        return self._create_futures_websocket(callback, subscription_messages)

    def futures_public_liquidates(
        self,
        callback: CallbackType,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения информации о ликвидациях по фьючерсным контрактам.

        Канал `futures.public_liquidates` передаёт данные о ликвидационных ордерах.
        Каждый контракт может присылать до одного сообщения о ликвидации в секунду.
        Для подписки на все контракты можно использовать значение ["!all"] в списке `symbols`.

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#public-liquidates-order-api

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]) или ["!all"] для всех контрактов.

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        return self._create_futures_websocket(
            callback, [self._build_subscription_message("futures.public_liquidates", symbols)]
        )

    def futures_contract_stats(
        self,
        callback: CallbackType,
        interval: str,
        symbols: list[str],
    ) -> Websocket:
        """Открывает вебсокет для получения статистики по фьючерсным контрактам.

        Канал `futures.contract_stats` передаёт агрегированную статистику по каждому контракту.
        Интервал определяет период агрегирования данных (например, "1m", "5m", "1h", "1d").

        Документация: https://www.gate.com/docs/developers/futures/ws/en/#contract-stats-api

        Параметры:
            callback (`CallbackType`): Асинхронная функция для обработки входящих сообщений.
            interval (`str`): Интервал статистики, например "1m", "5m", "1h", "1d".
            symbols (`list[str]`): Список фьючерсных контрактов (например ["BTC_USDT", "ETH_USDT"]).

        Возвращает:
            `Websocket`: Объект для управления вебсокет-соединением.
        """
        payloads = [[symbol, interval] for symbol in symbols]
        subscription_messages = [
            self._build_subscription_message("futures.contract_stats", payload)
            for payload in payloads
        ]
        return self._create_futures_websocket(callback, subscription_messages)
