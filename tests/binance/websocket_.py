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
    ws = bwm.futures_user_data_stream(callback=lambda m: print(m))
    ws.start()
    # ws = bwm.mini_ticker(callback=lambda m: print(m), symbol="ETHUSDT")
    # ws = bwm.futures_continuous_kline(
    #     callback=lambda m: print(m), pair="BTCUSDT", contract_type="perpetual", interval="1m"
    # )
    # ws = bwm.futures_composite_index(callback=lambda m: print(m), symbol="ETHUSDT")
    # ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()
