import asyncio

from unicex.hyperliquid import UniWebsocketManager
from unicex import Timeframe


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    m = UniWebsocketManager()

    s = m.trades(callback=callback, symbol="@107")

    await s.start()


if __name__ == "__main__":
    asyncio.run(main())
