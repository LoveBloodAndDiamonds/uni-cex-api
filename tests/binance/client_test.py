import asyncio

from unicex.binance import Client


from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )
    async with client:
        r = await client.futures_depth(symbol="BTCUSDT", limit=1000)

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
