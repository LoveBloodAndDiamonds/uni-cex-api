import asyncio

from unicex.binance import Client
import os


async def main() -> None:
    """Main entry point for the application."""

    client = await Client.create(
        api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_API_SECRET")
    )

    async with client as conn:
        r = await conn.order_create(
            **{
                "symbol": "ETHUSDT",
                "side": "BUY",
                "type": "MARKET",
                "quote_order_qty": 10,
                # "new_client_order_id": "open_VzTDBv6AGsI7XcBnm1wdAeTohpR",
            }
        )

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
