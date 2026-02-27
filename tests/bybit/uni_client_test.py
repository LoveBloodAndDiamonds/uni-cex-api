import asyncio

from unicex.bybit import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.futures_best_bid_ask()

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
