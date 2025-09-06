from unicex.exchanges.binance.websocket_manager import BinanceWebsocketManager


def main() -> None:
    """Main entry point for the application."""

    # import json

    # a = {"method": "SUBSCRIBE", "params": ["btcusdt@aggTrade"], "id": 1757169879029}
    # print(json.dumps(a))
    # exit()

    bwm = BinanceWebsocketManager()
    ws = bwm.agg_trade(callback=lambda m: print(m), symbol="BTCUSDT")
    ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()
