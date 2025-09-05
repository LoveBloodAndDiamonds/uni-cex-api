from unicex.bybit.uni_client import BybitUniClient
from unicex.enums import Timeframe
from pprint import pp as print  # noqa type: ignore


# TODO TICKERS24H ONLY FOR USDT
def main() -> None:
    """Main entry point for the application."""

    with BybitUniClient() as c:
        # r = client.futures_klines("BTCUSDT", "1", limit=1)
        # r = c._client.futures_ping()
        # r = c.klines("BTCUSDT", Timeframe.MIN_1)
        r = c.funding_rate()

        print(r)
        print(len(r))


if __name__ == "__main__":
    main()
