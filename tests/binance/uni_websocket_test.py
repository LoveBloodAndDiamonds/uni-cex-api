from unicex.enums import Timeframe
from unicex.exchanges.binance import UniBinanceWebsocketManager
from unicex.types import KlineDict


def callback(klines: list[KlineDict]):
    for k in klines:
        print(k)


def main() -> None:
    """Main entry point for the application."""
    sm = UniBinanceWebsocketManager()
    socket = sm.futures_aggtrades(symbol="BTCUSDT", callback=callback)
    socket.start()

    import time

    time.sleep(100)


if __name__ == "__main__":
    main()
