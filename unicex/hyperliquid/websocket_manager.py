__all__ = ["WebsocketManager"]

import base64
import json
import warnings
import zlib
from collections.abc import Awaitable, Callable
from typing import Any

from unicex._base import Websocket

from .client import Client

type CallbackType = Callable[[Any], Awaitable[None]]


class WebsocketManager:
    """Менеджер асинхронных вебсокетов для Hyperliquid."""

    _URL: str = "wss://api.hyperliquid.xyz/ws"
    """Базовый URL для вебсокета."""

    def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
        """Инициализирует менеджер вебсокетов для Hyperliquid.

        Параметры:
            client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
            ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
        """
        self.client = client
        self._ws_kwargs = {
            "ping_message": json.dumps({"method": "ping"}),
            "ping_interval": 30,
            **ws_kwargs,
        }

    def _create_subscription_message(self, subscription_type: str, **params: Any) -> str:
        """Создает сообщение подписки для Hyperliquid.

        Параметры:
            subscription_type (`str`): Тип подписки.
            params (`dict[str, Any]`): Параметры подписки.

        Возвращает:
            `str`: JSON-строка с сообщением подписки.
        """
        subscription = {"type": subscription_type, **params}
        message = {"method": "subscribe", "subscription": subscription}
        return json.dumps(message)

    def all_mids(self, callback: CallbackType, dex: str | None = None) -> Websocket:
        """Создает вебсокет для получения средних цен всех активов.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            dex (`str | None`): Perp dex для получения средних цен. Если не указан, используется первый perp dex.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        params = {}
        if dex is not None:
            params["dex"] = dex

        subscription_message = self._create_subscription_message("allMids", **params)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def notification(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения уведомлений пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("notification", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def _subscribe(
        self, callback: CallbackType, subscription_type: str, **params: Any
    ) -> Websocket:
        """Создает вебсокет с одной подпиской (параметры со значением None не передаются)."""
        params = {k: v for k, v in params.items() if v is not None}
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[self._create_subscription_message(subscription_type, **params)],
            **self._ws_kwargs,
        )

    def web_data3(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения агрегированных данных пользователя (для веб-интерфейса).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "webData3", user=user)

    def web_data2(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения веб-данных пользователя (устарело, используйте `web_data3`).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        warnings.warn(
            "webData2 is no longer documented by Hyperliquid, use web_data3",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._subscribe(callback, "webData2", user=user)

    def twap_states(self, callback: CallbackType, user: str, dex: str | None = None) -> Websocket:
        """Создает вебсокет для получения состояний TWAP-ордеров пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            dex (`str | None`): Perp dex. Если не указан, используется первый perp dex.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "twapStates", user=user, dex=dex)

    def clearinghouse_state(
        self, callback: CallbackType, user: str, dex: str | None = None
    ) -> Websocket:
        """Создает вебсокет для получения состояния перпетуального аккаунта пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            dex (`str | None`): Perp dex. Если не указан, используется первый perp dex.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "clearinghouseState", user=user, dex=dex)

    def open_orders(self, callback: CallbackType, user: str, dex: str | None = None) -> Websocket:
        """Создает вебсокет для получения открытых ордеров пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            dex (`str | None`): Perp dex. Если не указан, используется первый perp dex.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "openOrders", user=user, dex=dex)

    def spot_state(
        self, callback: CallbackType, user: str, is_portfolio_margin: bool | None = None
    ) -> Websocket:
        """Создает вебсокет для получения спотовых балансов пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            is_portfolio_margin (`bool | None`): Аккаунт в режиме портфельной маржи (Опционально).

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(
            callback, "spotState", user=user, isPortfolioMargin=is_portfolio_margin
        )

    def all_dexs_clearinghouse_state(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения состояния аккаунта пользователя по всем perp dex.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "allDexsClearinghouseState", user=user)

    def all_dexs_asset_ctxs(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения контекстов активов (mark, funding, OI) по всем perp dex.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "allDexsAssetCtxs")

    def outcome_meta_updates(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для получения обновлений метаданных outcome-рынков (HIP-4).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        return self._subscribe(callback, "outcomeMetaUpdates")

    def fast_asset_ctxs(self, callback: CallbackType) -> Websocket:
        """Создает вебсокет для быстрых обновлений контекстов активов по всем perp dex.

        Биржа присылает `data` как base64 + raw DEFLATE; в callback приходит уже распакованный
        словарь. Первое сообщение — снапшот, далее только изменившиеся монеты и поля.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """

        async def _decoding_callback(msg: Any) -> None:
            if isinstance(msg, dict) and isinstance(msg.get("data"), str):
                raw = zlib.decompress(base64.b64decode(msg["data"]), wbits=-15)
                msg = {**msg, "data": json.loads(raw)}
            await callback(msg)

        return self._subscribe(_decoding_callback, "fastAssetCtxs")

    def candle(
        self,
        callback: CallbackType,
        interval: str,
        coin: str | None = None,
        coins: list[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения свечей.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            coin (`str`): Символ монеты.
            coins (`list[str]`): Список символов монет для мультиплекс подключения.
            interval (`str`): Интервал свечей ("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d", "3d", "1w", "1M").

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]
        subscription_messages = [
            self._create_subscription_message("candle", coin=coin, interval=interval)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def l2_book(
        self,
        callback: CallbackType,
        coin: str | None = None,
        coins: list[str] | None = None,
        n_sig_figs: int | None = None,
        mantissa: int | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения стакана L2.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            coin (`str | None`): Символ монеты.
            coins (`list[str] | None`): Список символов монет для мультиплекс подключения.
            n_sig_figs (`int | None`): Количество значащих цифр для округления цен.
            mantissa (`int | None`): Мантисса для округления цен.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]

        params = {}
        if n_sig_figs is not None:
            params["nSigFigs"] = n_sig_figs  # type: ignore
        if mantissa is not None:
            params["mantissa"] = mantissa  # type: ignore

        subscription_messages = [
            self._create_subscription_message("l2Book", coin=coin, **params)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def trades(
        self,
        callback: CallbackType,
        coin: str | None = None,
        coins: list[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения сделок.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            coin (`str | None`): Символ монеты.
            coins (`list[str] | None`): Список символов монет для мультиплекс подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]
        subscription_messages = [
            self._create_subscription_message("trades", coin=coin)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def order_updates(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения обновлений ордеров пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("orderUpdates", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def user_events(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения событий пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("userEvents", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def user_fills(
        self, callback: CallbackType, user: str, aggregate_by_time: bool | None = None
    ) -> Websocket:
        """Создает вебсокет для получения исполнений пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            aggregate_by_time (`bool | None`): Агрегировать по времени.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        params = {"user": user}
        if aggregate_by_time is not None:
            params["aggregateByTime"] = aggregate_by_time  # type: ignore

        subscription_message = self._create_subscription_message("userFills", **params)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def user_fundings(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения фандинга пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("userFundings", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def user_non_funding_ledger_updates(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения обновлений леджера пользователя (кроме фандинга).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message(
            "userNonFundingLedgerUpdates", user=user
        )
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def active_asset_ctx(
        self,
        callback: CallbackType,
        coin: str | None = None,
        coins: list[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения контекста активного актива.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            coin (`str | None`): Символ монеты.
            coins (`list[str] | None`): Список символов монет для мультиплекс подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]

        subscription_messages = [
            self._create_subscription_message("activeAssetCtx", coin=coin)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def active_asset_data(
        self,
        callback: CallbackType,
        user: str,
        coin: str | None = None,
        coins: list[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения данных активного актива пользователя (только Perps).

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.
            coin (`str | None`): Символ монеты.
            coins (`list[str] | None`): Список символов монет для мультиплекс подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]

        subscription_messages = [
            self._create_subscription_message("activeAssetData", user=user, coin=coin)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )

    def user_twap_slice_fills(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения TWAP slice fills пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("userTwapSliceFills", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def user_twap_history(self, callback: CallbackType, user: str) -> Websocket:
        """Создает вебсокет для получения TWAP истории пользователя.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            user (`str`): Адрес пользователя.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        subscription_message = self._create_subscription_message("userTwapHistory", user=user)
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=[subscription_message],
            **self._ws_kwargs,
        )

    def bbo(
        self,
        callback: CallbackType,
        coin: str | None = None,
        coins: list[str] | None = None,
    ) -> Websocket:
        """Создает вебсокет для получения лучшего бида/аска.

        Параметры:
            callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
            coin (`str | None`): Символ монеты.
            coins (`list[str] | None`): Список символов монет для мультиплекс подключения.

        Возвращает:
            `Websocket`: Объект для управления вебсокет соединением.
        """
        if coin and coins:
            raise ValueError("Parameters coin and coins cannot be used together")
        if not (coin or coins):
            raise ValueError("Either coin or coins must be provided")
        if coin:
            coins = [coin]

        subscription_messages = [
            self._create_subscription_message("bbo", coin=coin)
            for coin in coins  # type: ignore
        ]
        return Websocket(
            callback=callback,
            url=self._URL,
            subscription_messages=subscription_messages,
            **self._ws_kwargs,
        )
