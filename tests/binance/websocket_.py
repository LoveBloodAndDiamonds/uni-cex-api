from unicex.exchanges.binance.websocket_manager import BinanceWebsocketManager


def main() -> None:
    """Main entry point for the application."""

    # import json

    # a = {"method": "SUBSCRIBE", "params": ["btcusdt@aggTrade"], "id": 1757169879029}
    # print(json.dumps(a))
    # exit()

    bwm = BinanceWebsocketManager()
    # ws = bwm.mini_ticker(callback=lambda m: print(m), symbol="ETHUSDT")
    # ws = bwm.futures_continuous_kline(
    #     callback=lambda m: print(m), pair="BTCUSDT", contract_type="perpetual", interval="1m"
    # )
    ws = bwm.futures_composite_index(callback=lambda m: print(m), symbol="ETHUSDT")
    ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()
