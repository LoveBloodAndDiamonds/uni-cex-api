import asyncio
from venv import logger

from unicex import OrderSide, OrderType
from unicex.bybit import UniClient

from loguru import logger

import os


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
    )

    async with c:
        r = await c.futures_order_create(
            symbol="TRXUSDT",
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity=10,
        )

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
