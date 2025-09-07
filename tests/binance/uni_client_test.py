from unicex.exchanges.binance.uni_client import UniBinanceClient
from pprint import pp as print  # noqa type: ignore


def main() -> None:
    """Main entry point for the application."""

    with UniBinanceClient() as client:
        # r = client.futures_klines("BTCUSDT", "1m", limit=1)
        # r = client.futures_ticker_24h()
        r = client.funding_rate()
        print(r)
        print(len(r))


if __name__ == "__main__":
    main()
