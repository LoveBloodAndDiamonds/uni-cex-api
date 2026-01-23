import asyncio

from unicex.aster import Client
from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=os.getenv("ASTER_API_KEY"), api_secret=os.getenv("ASTER_API_SECRET")
    )

    async with client as conn:
        res = await conn.futures_renew_listen_key()
        pp(res)


if __name__ == "__main__":
    asyncio.run(main())
