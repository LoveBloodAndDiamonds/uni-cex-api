import asyncio

from unicex.gate import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_tickers(settle="usdt", contract="ZEC_USDT")
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
