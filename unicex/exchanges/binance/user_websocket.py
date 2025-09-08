__all__ = [
    "BinanceUserWebsocket",
    "AsyncBinanceUserWebsocket",
]

import logging
import threading
import time
from collections.abc import Callable

from unicex.base import BaseSyncWebsocket

from .client import AsyncBinanceClient, BinanceClient
from .types import AccountType


class BinanceUserWebsocket:
    """Пользовательский вебсокет Binance с авто‑продлением listenKey.

    Поддержка типов аккаунта: "SPOT" и "FUTURES" (USDT‑маржинальные фьючерсы).
    Тип "MARGIN" пока не реализован.
    """

    # Базовые URL WebSocket
    _BASE_SPOT_WSS: str = "wss://stream.binance.com:9443"
    _BASE_FUTURES_WSS: str = "wss://fstream.binance.com"

    # Интервал продления listenKey (сек.) — безопасный буфер меньше 30 мин
    _RENEW_INTERVAL: int = 25 * 60

    def __init__(self, callback: Callable, client: BinanceClient, type: AccountType) -> None:
        """Инициализирует пользовательский вебсокет.

        Параметры:
            callback (Callable): Обработчик сообщений из стрима.
            client (BinanceClient): Авторизованный клиент Binance.
            type (AccountType): Тип аккаунта ("SPOT" | "FUTURES").
        """
        self._callback = callback
        self._client = client
        self._type = type

        self._logger = logging.getLogger(__name__)
        self._listen_key: str | None = None
        self._ws: BaseSyncWebsocket | None = None
        self._keepalive_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()

    def start(self) -> None:
        """Запускает пользовательский стрим с автопродлением listenKey."""
        with self._lock:
            self._listen_key = self._create_listen_key()
            self._start_ws(self._listen_key)

            # Фоновое продление ключа
            self._stop_event.clear()
            self._keepalive_thread = threading.Thread(
                target=self._keepalive_loop, name="binance-user-ws-keepalive", daemon=True
            )
            self._keepalive_thread.start()

    def stop(self) -> None:
        """Останавливает стрим и закрывает listenKey."""
        with self._lock:
            self._stop_event.set()
            if self._keepalive_thread and self._keepalive_thread.is_alive():
                self._keepalive_thread.join(timeout=5)
            self._keepalive_thread = None

            if self._ws:
                try:
                    self._ws.stop()
                except Exception as e:  # noqa: BLE001
                    self._logger.error(f"Ошибка при остановке WS: {e}")
                finally:
                    self._ws = None

            # Закрываем listenKey на стороне API
            try:
                if self._listen_key:
                    self._close_listen_key(self._listen_key)
            finally:
                self._listen_key = None

    def _ws_url(self, listen_key: str) -> str:
        if self._type == "FUTURES":
            return f"{self._BASE_FUTURES_WSS}/ws/{listen_key}"
        if self._type == "SPOT":
            return f"{self._BASE_SPOT_WSS}/ws/{listen_key}"
        raise NotImplementedError("Поддерживаются только типы аккаунта: SPOT и FUTURES")

    def _start_ws(self, listen_key: str) -> None:
        url = self._ws_url(listen_key)
        self._ws = BaseSyncWebsocket(callback=self._callback, url=url)
        self._ws.start()
        self._logger.info(f"User WS started: {url}")

    def _restart_ws(self, new_listen_key: str) -> None:
        self._logger.info("Перезапуск пользовательского WS из-за изменения listenKey")
        if self._ws:
            try:
                self._ws.stop()
            except Exception as e:  # noqa: BLE001
                self._logger.error(f"Ошибка при остановке WS перед перезапуском: {e}")
        self._start_ws(new_listen_key)

    def _create_listen_key(self) -> str:
        if self._type == "FUTURES":
            resp = self._client.futures_listen_key()
        elif self._type == "SPOT":
            resp = self._client.listen_key()
        else:
            raise NotImplementedError("Тип аккаунта не поддерживается для User Data Stream")

        key = resp.get("listenKey")
        if not isinstance(key, str) or not key:
            raise RuntimeError(f"Не удалось получить listenKey. Ответ: {resp}")
        return key

    def _renew_listen_key(self) -> str | None:
        """Продлевает listenKey. Возвращает новый ключ, если сервер его выдал."""
        if self._type == "FUTURES":
            # FAPI обычно возвращает {} и не меняет ключ
            self._client.futures_renew_listen_key()
            return None
        elif self._type == "SPOT":
            # SPOT keepalive принимает listenKey и обычно возвращает {}
            resp = self._client.renew_listen_key(self._listen_key or "")
            return resp.get("listenKey") if isinstance(resp, dict) else None
        else:
            raise NotImplementedError("Тип аккаунта не поддерживается для keepalive")

    def _close_listen_key(self, listen_key: str) -> None:
        try:
            if self._type == "FUTURES":
                self._client.futures_close_listen_key()
            elif self._type == "SPOT":
                self._client.close_listen_key(listen_key)
            else:
                raise NotImplementedError("Тип аккаунта не поддерживается для закрытия listenKey")
        except Exception as e:  # noqa: BLE001
            self._logger.error(f"Ошибка закрытия listenKey: {e}")

    def _keepalive_loop(self) -> None:
        """Фоновый цикл продления listenKey и восстановления сессии при необходимости."""
        while not self._stop_event.is_set():
            try:
                # Пытаемся продлить текущий ключ
                new_key = self._renew_listen_key()
                # Если сервер вернул новый ключ — перезапускаем WS
                if isinstance(new_key, str) and new_key and new_key != self._listen_key:
                    self._listen_key = new_key
                    with self._lock:
                        self._restart_ws(new_key)
            except Exception as e:  # noqa: BLE001
                # В случае ошибки — пробуем получить новый ключ и перезапуститься
                self._logger.error(f"Ошибка keepalive: {e}. Пробуем пересоздать listenKey…")
                try:
                    new_key = self._create_listen_key()
                    if new_key != self._listen_key:
                        self._listen_key = new_key
                        with self._lock:
                            self._restart_ws(new_key)
                except Exception as ee:  # noqa: BLE001
                    self._logger.error(f"Не удалось пересоздать listenKey: {ee}")

            # Ждём до следующего продления
            for _ in range(self._RENEW_INTERVAL):
                if self._stop_event.is_set():
                    return
                time.sleep(1)


class AsyncBinanceUserWebsocket:
    """Асинхронный пользовательский вебсокет для работы с биржей Binance."""

    def __init__(self, callback: Callable, client: AsyncBinanceClient, type: AccountType) -> None:
        """Инициализирует асинхронный пользовательский вебсокет для работы с биржей Binance.

        Параметры:
            client (BinanceClient): Клиент для работы с биржей Binance.
            type (AccountType): Тип аккаунта (SPOT, MARGIN, FUTURES).
        """
        self._callback = callback
        self._client = client
        self._type = type
