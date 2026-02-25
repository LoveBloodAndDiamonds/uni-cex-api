import asyncio

from unicex.hyperliquid import WebsocketManager
from unicex import Timeframe


async def callback(msg):
    levels = msg["data"]["levels"]
    asks = levels[0]
    bids = levels[1]

    print(levels)
    # print(len(asks))
    # print(len(bids))
    print()


async def main() -> None:
    """Main entry point for the application."""
    m = WebsocketManager()

    # s = m.bbo(callback=callback, coin="ETH")
    s = m.l2_book(callback=callback, coin="ETH")

    await s.start()


if __name__ == "__main__":
    asyncio.run(main())
