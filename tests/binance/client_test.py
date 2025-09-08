from os import getenv

from unicex.exchanges.binance.client import BinanceClient
from unicex.enums import Timeframe

from pprint import pp as print  # noqa # type: ignore


def main() -> None:
    """Main entry point for the application."""
    client = BinanceClient(
        api_key=getenv("BINANCE_API_KEY"),
        api_secret=getenv("BINANCE_API_SECRET"),
    )

    with client as cl:
        # r = cl.ticker_24h(symbols=["BTCUSDT", "ETHUSDT"])

        # r = cl.futures_ticker_24h("BTCUSDT")

        # r = cl.all_orders("BTCUSDT")

        # r = cl.order_create(symbol="TRXUSDT", side="SELL", type="MARKET", quantity=19)

        # 2kmVLdWzz5AwUWOqU6sbuuLmlOnKS3THP7g44FSStAl6eAFyU5eUstxSdc4EWTs7

        r = cl.listen_key()

        # r = cl.futures_close_listen_key()

        print(r)


if __name__ == "__main__":
    main()
