import asyncio

from unicex import BybitUniClient


async def main() -> None:
    """Main entry point for the application."""
    client = await BybitUniClient.create()

    async with client as conn:
        t = await conn.futures_tickers()
        print("len spot tickers: ", len(t))


if __name__ == "__main__":
    asyncio.run(main())
