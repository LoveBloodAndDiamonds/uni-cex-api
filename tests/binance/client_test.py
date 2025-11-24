import asyncio

from unicex.binance import Client
import os


async def main() -> None:
    """Main entry point for the application."""

    client = await Client.create(
        api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_API_SECRET")
    )

    async with client as conn:
        # r = await conn.oco_order_create(
        #     symbol="BTCUSDT",
        #     side="SELL",
        #     quantity="0.00016",
        #     above_type="TAKE_PROFIT",
        #     above_stop_price="93000",
        #     below_type="STOP_LOSS",
        #     below_stop_price="90000",
        # )

        r = await conn.my_trades(symbol="BTCUSDT")

        from pprint import pp

        # pp(r)
        #
        for item in r:
            pp(item)
            # pp(item["orderId"])


if __name__ == "__main__":
    asyncio.run(main())
