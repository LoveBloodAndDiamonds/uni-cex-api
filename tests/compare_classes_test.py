def main() -> None:
    """Простой чек: вывести публичные методы WS‑менеджера Binance (асинхронного)."""

    import inspect
    from unicex.binance import WebsocketManager

    methods = [
        m
        for m in dir(WebsocketManager)
        if not m.startswith("_") and inspect.isfunction(getattr(WebsocketManager, m))
    ]

    from pprint import pp

    pp(sorted(methods))


if __name__ == "__main__":
    main()
