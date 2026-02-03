import asyncio

from unicex.binance import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.tickers()
        print(len(r))


if __name__ == "__main__":
    asyncio.run(main())
