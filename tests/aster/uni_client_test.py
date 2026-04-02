import asyncio

from unicex.aster import UniClient

from unicex import *

import os

from loguru import logger

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.environ.get("ASTER_API_KEY"),
        api_secret=os.environ.get("ASTER_API_SECRET"),
    )

    # async with c:
    #     t = "BTCUSDT"

    #     # await c.futures_set_leverage(t, leverage=10)
    #     await c.futures_set_margin_type(t, MarginType.ISOLATED)

    async with c:
        r = await c.futures_order_create(
            symbol="TRXUSDT",
            side=OrderSide.SELL,
            type=OrderType.MARKET,
            quantity="50",
            reduce_only=False,
        )
        # r = await c.futures_position_info("TRXUSDT")
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
