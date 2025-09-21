from unicex.exchanges.binance.websocket_manager import BinanceWebsocketManager
from unicex.exchanges.binance.client import BinanceClient

from os import getenv


def main() -> None:
    """Main entry point for the application."""

    # import json

    # a = {"method": "SUBSCRIBE", "params": ["btcusdt@aggTrade"], "id": 1757169879029}
    # print(json.dumps(a))
    # exit()
    #

    client = BinanceClient(
        api_key=getenv("BINANCE_API_KEY"), api_secret=getenv("BINANCE_API_SECRET")
    )

    bwm = BinanceWebsocketManager(client=client)
    ws = bwm.user_data_stream(callback=lambda m: print(m))
    ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()
