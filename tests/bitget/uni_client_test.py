import asyncio

from unicex.bybit import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        t = await c.futures_tickers()
        print(len(t))


if __name__ == "__main__":
    asyncio.run(main())
