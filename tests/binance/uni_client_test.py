import asyncio

from unicex import OrderSide, OrderType  # type: ignore
from unicex.binance import UniClient

from loguru import logger  # type: ignore

import os


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )

    async with c:
        r = await c.futures_order_create(
            symbol="TRXUSDT",
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            quantity="50",
            price="0.28",
            client_order_id="1232",
        )
        from pprint import pp

        pp(r)

        r = await c.futures_position_info("TRXUSDT")

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
