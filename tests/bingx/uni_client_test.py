import asyncio

from unicex.bingx import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.ticker_24hr()
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
