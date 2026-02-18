import asyncio

from unicex.hyperliquid import UniWebsocketManager, ExchangeInfo
from unicex import Timeframe

# 1771333346024
# 1771333425340


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    asyncio.create_task(ExchangeInfo.start())

    await asyncio.sleep(3)

    m = UniWebsocketManager()

    s = m.klines(callback=callback, symbol="@107", timeframe=Timeframe.MIN_1)

    await s.start()


if __name__ == "__main__":
    asyncio.run(main())
