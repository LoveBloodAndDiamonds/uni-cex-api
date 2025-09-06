__all__ = [
    "BaseSyncWebsocket",
    "BaseAsyncWebsocket",
]

import json
import threading

from websocket import WebSocketApp


class BaseSyncWebsocket:
    """Базовый класс синхронного вебсокета."""

    def __init__(
        self, url: str, ws_kwargs: dict | None = None, run_kwargs: dict | None = None
    ) -> None:
        """Инициализация вебсокета.

        Параметры:
            url (str): URL вебсокета.
            ws_kwargs (dict | None): Параметры WebSocketApp.
            run_kwargs (dict | None): Параметры run_forever.
        """
        self._ws_kw = ws_kwargs or {}
        self._run_kw = run_kwargs or {}
        self._ws = WebSocketApp(url=url, **self._ws_kw)

        self._wst: threading.Thread | None = None

    def start(self) -> None:
        """Запустить вебсокет в потоке."""
        self._wst = threading.Thread(target=self._ws.run_forever, kwargs=self._run_kw)
        self._wst.daemon = True
        self._wst.start()

    def stop(self) -> None:
        """Останавливает вебсокет и поток."""
        if self._ws:
            self._ws.close()  # отправляем "close frame"
        if self._wst and self._wst.is_alive():
            self._wst.join(timeout=5)  # ждём завершения потока
            self._wst = None

    def send(self, message: dict) -> None:
        """Отправляет сообщение в вебсокет."""
        self._ws.send_text(json.dumps(message))


class BaseAsyncWebsocket:
    """Базовый класс асинхронного вебсокета."""

    pass
