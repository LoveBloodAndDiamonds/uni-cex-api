import asyncio

from unicex.aster import UserWebsocket, Client
import os
from unicex.enums import Timeframe
from unicex.types import TradeDict
from loguru import logger

logger.remove()
import sys

logger.add(sys.stderr, level="DEBUG")


async def callback(msg) -> None:
    print(type(msg), msg)
    print()


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=os.getenv("ASTER_API_KEY"), api_secret=os.getenv("ASTER_API_SECRET"), logger=logger
    )
    ws = UserWebsocket(callback=callback, client=client, logger=logger)
    await ws.start()
    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
