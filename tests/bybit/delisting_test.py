import asyncio

from unicex.bybit import UniClient
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create()
    async with client:
        t = await client.futures_delistings()
        pp(t)


if __name__ == "__main__":
    asyncio.run(main())
