import asyncio

from unicex.enums import Timeframe
from unicex.hyperliquid import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        r = await c.klines("@142", interval=Timeframe.MIN_1, limit=3)

        from datetime import datetime

        for item in r:
            print(datetime.fromtimestamp(item["t"] / 1000))


if __name__ == "__main__":
    asyncio.run(main())
