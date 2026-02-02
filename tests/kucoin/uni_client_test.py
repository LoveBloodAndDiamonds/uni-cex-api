import asyncio

from unicex.kucoin import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.futures_tickers()
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
