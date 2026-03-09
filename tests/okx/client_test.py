import asyncio

from unicex.okx import Client
from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()

    async with client as conn:
        r = await conn.get_funding_rate("ANY")
        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
