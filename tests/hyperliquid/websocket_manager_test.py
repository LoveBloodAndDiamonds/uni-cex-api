import asyncio

from unicex.hyperliquid import WebsocketManager
from unicex import Timeframe


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    m = WebsocketManager()

    s = m.bbo(callback=callback, coin="ETH")

    await s.start()


if __name__ == "__main__":
    asyncio.run(main())
