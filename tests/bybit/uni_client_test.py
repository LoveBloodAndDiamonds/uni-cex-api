import asyncio

from unicex import OrderSide, OrderType  # type: ignore
from unicex.bybit import UniClient

from loguru import logger  # type: ignore

import os


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
    )

    async with c:
        # r = await c.futures_order_create(
        #     symbol="TRXUSDT",
        #     side=OrderSide.BUY,
        #     type=OrderType.MARKET,
        #     quantity="50",
        #     client_order_id="123",
        # )

        r = await c.futures_position_info("TRXUSDT")

        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
