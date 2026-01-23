import asyncio

from unicex.aster import UniClient
from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create(
        # api_key=os.getenv("ASTER_API_KEY"), api_secret=os.getenv("ASTER_API_SECRET")
    )

    async with client as conn:
        res = await conn.funding_rate("ACUUSDT")
        pp(res)


if __name__ == "__main__":
    asyncio.run(main())
