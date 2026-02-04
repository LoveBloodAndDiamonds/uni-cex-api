import asyncio

from unicex.aster import UniClient
from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create()

    async with client as conn:
        r = await conn.open_interest("BTCUSDT")
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
