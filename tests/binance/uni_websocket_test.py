from unicex.enums import Timeframe
from unicex.exchanges.binance import UniBinanceWebsocketManager, BinanceWebsocketManager
from unicex.types import KlineDict


# def callback(klines: list[KlineDict]):
#     for k in klines:
#         print(k)


def callback(msg):
    print(msg)


def main() -> None:
    """Main entry point for the application."""
    sm = BinanceWebsocketManager()
    socket = sm.futures_klines(symbol="BTCUSDT", callback=callback, interval="1m")
    socket.start()

    import time

    time.sleep(100)


if __name__ == "__main__":
    main()
