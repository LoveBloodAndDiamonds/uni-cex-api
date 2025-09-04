from unicex.binance.client import BinanceClient
from unicex.enums import Timeframe

from pprint import pp as print  # noqa # type: ignore


def main() -> None:
    """Main entry point for the application."""
    client = BinanceClient()

    with client as cl:
        # r = cl.ticker_24h(symbols=["BTCUSDT", "ETHUSDT"])

        r = cl.futures_ticker_24h("BTCUSDT")

        print(r)


if __name__ == "__main__":
    main()
