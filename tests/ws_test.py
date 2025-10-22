import asyncio

from unicex import BinanceWebsocketManager

from loguru import logger

import sys

# logger.add(sys.stderr, level="TRACE")


async def callback(msg):
    pass


async def main() -> None:
    """Main entry point for the application."""
    logger.trace("START")
    bsm = BinanceWebsocketManager(logger=logger)

    ws = bsm.trade(callback=callback, symbol="BTCUSDT")

    import asyncio

    t = asyncio.create_task(ws.start())

    await asyncio.sleep(5)

    logger.debug("Stopping")
    await ws.stop()
    logger.debug("Stopped")

    await t

    logger.debug("Finished")


if __name__ == "__main__":
    asyncio.run(main())
