from unicex.bybit.client import BybitClient
from unicex.enums import Timeframe

from pprint import pp as print  # noqa # type: ignore
from tests.keys import bybit_api, bybit_secret


def main() -> None:
    """Main entry point for the application."""
    client = BybitClient(
        api_key=bybit_api,
        api_secret=bybit_secret,
    )

    with client as cl:
        # r = cl.order_history(
        #     category="linear",
        #     symbol="BTCUSDT",
        # )
        #
        r = cl.create_order(
            category="linear",
            symbol="TRXUSDT",
            side="Buy",
            orderType="Market",
            qty="20",
        )
        # r = cl.set_leverage("linear", "TRXUSDT", "50", "50")

        print(r)


if __name__ == "__main__":
    main()
