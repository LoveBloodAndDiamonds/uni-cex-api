import asyncio

from unicex.gate import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(timeout=20)

    async with c:
        r = await c.futures_last_price()

        from pprint import pp

        pp(len(r))


if __name__ == "__main__":
    asyncio.run(main())
