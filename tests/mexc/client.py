from webbrowser import get
from unicex.mexc import Client


import asyncio

from os import getenv


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=getenv("MEXC_API_KEY"), api_secret=getenv("MEXC_API_SECRET")
    )

    # r = await client.create_order(
    #     symbol="MXUSDT", side="BUY", type="MARKET", price=2.58, quote_order_quantity=3
    # )
    #
    r = await client.exchange_info(symbols=["MXUSDT", "BTCUSDT"])

    from pprint import pp

    pp(r)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
