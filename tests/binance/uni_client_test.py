import asyncio

from unicex import OrderSide, OrderType, MarginType  # type: ignore
from unicex.binance import UniClient

from loguru import logger  # type: ignore

import os

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )

    async with c:
        t = "BTCUSDT"

        # await c.futures_set_leverage(t, leverage=10)
        await c.futures_set_margin_type(t, MarginType.CROSSED)

    # async with c:
    #     r = await c.futures_order_create(
    #         symbol="TRXUSDT",
    #         side=OrderSide.BUY,
    #         type=OrderType.MARKET,
    #         quantity="100",
    #         reduce_only=True,
    #     )
    #     from pprint import pp

    #     pp(r)


if __name__ == "__main__":
    asyncio.run(main())
