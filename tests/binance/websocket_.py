from unicex.abstract import BaseSyncWebsocket


def main() -> None:
    """Main entry point for the application."""
    ws = BaseSyncWebsocket(
        url="wss://stream.binance.com:9443/ws/btcusdt@aggTrade", callback=lambda m: print(m)
    )
    ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()
