import asyncio
import re

from unicex.kucoin import WebsocketManager
from loguru import logger

logger.remove()
import sys

logger.add(sys.stderr, level="DEBUG")


async def callback(msg):
    print(msg, end="\r")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager(logger=logger)
    ws = manager.orderbook(
        callback=callback, trade_type="SPOT", symbols=["TRX-USDT", "ADA-USDT"], depth="increment"
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
