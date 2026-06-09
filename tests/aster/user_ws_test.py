import asyncio
import os

from loguru import logger

from unicex.aster import Client, UserWebsocket

logger.remove()
import sys

logger.add(sys.stderr, level="DEBUG")


async def callback(msg) -> None:
    print(type(msg), msg)
    print()


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        private_key=os.getenv("ASTER_PRIVATE_KEY"), logger=logger
    )
    ws = UserWebsocket(callback=callback, client=client, logger=logger)
    await ws.start()
    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
