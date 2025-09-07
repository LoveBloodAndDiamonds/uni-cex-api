from unicex.exchanges.binance.client import BinanceClient
from unicex.enums import Timeframe

from pprint import pp as print  # noqa # type: ignore
from tests.keys import binance_api, binance_secret


def main() -> None:
    """Main entry point for the application."""
    client = BinanceClient(
        api_key=binance_api,
        api_secret=binance_secret,
    )

    with client as cl:
        # r = cl.ticker_24h(symbols=["BTCUSDT", "ETHUSDT"])

        # r = cl.futures_ticker_24h("BTCUSDT")

        # r = cl.all_orders("BTCUSDT")

        # r = cl.order_create(symbol="TRXUSDT", side="SELL", type="MARKET", quantity=19)

        r = cl.futures_listen_key()

        print(r)


if __name__ == "__main__":
    main()
