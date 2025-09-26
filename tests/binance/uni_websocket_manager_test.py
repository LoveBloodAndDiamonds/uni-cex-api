from unicex.enums import Timeframe
from unicex.binance import UniWebsocketManager
from unicex.types import KlineDict


# def callback(klines: list[KlineDict]):
#     for k in klines:
#         print(k)


def callback(msg):
    print(msg)


def main() -> None:
    """Main entry point for the application."""
    sm = UniWebsocketManager()
    socket = sm.futures_trades(callback=callback, symbol="BTCUSDT")
    socket.start()

    import time

    time.sleep(100)


if __name__ == "__main__":
    main()
