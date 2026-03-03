import asyncio

from unicex.gate import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.futures_depth("BTC_USDT", 300)

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
