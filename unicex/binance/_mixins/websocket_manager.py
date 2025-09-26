__all__ = ["WebsocketManagerMixin"]


from collections.abc import Sequence


class WebsocketManagerMixin:
    """Миксин для менеджеров вебсокетов Binance."""

    _BASE_SPOT_URL: str = "wss://stream.binance.com:9443"
    """Базовый URL для вебсокета на спот."""

    _BASE_FUTURES_URL: str = "wss://fstream.binance.com"
    """Базовый URL для вебсокета на фьючерсы."""

    def _generate_stream_url(
        self,
        type: str,
        url: str,
        symbol: str | None = None,
        symbols: Sequence[str] | None = None,
        require_symbol: bool = False,
    ) -> str:
        """Генерирует URL для вебсокета Binance. Параметры symbol и symbols не могут быть использованы вместе.

        Параметры:
            type (`str`): Тип вебсокета.
            url (`str`): Базовый URL для вебсокета.
            symbol (`str | None`): Символ для подписки.
            symbols (`Sequence[str] | None`): Список символов для подписки.
            require_symbol (`bool`): Требуется ли символ для подписки.

        Возвращает:
            str: URL для вебсокета.
        """
        if symbol and symbols:
            raise ValueError("Parameters symbol and symbols cannot be used together")
        if require_symbol and not (symbol or symbols):
            raise ValueError("Either symbol or symbols must be provided")
        if symbol:
            return f"{url}/ws/{symbol.lower()}@{type}"
        if symbols:
            streams = "/".join(f"{s.lower()}@{type}" for s in symbols)
            return f"{url}/stream?streams={streams}"
        return f"{url}/ws/{type}"
