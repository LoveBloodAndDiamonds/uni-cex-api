import asyncio

from unicex import OrderSide, OrderType  # type: ignore
from unicex.enums import MarginType
from unicex.gate import UniClient, ExchangeInfo

from loguru import logger  # type: ignore

import os

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()

    await asyncio.sleep(5)

    c = await UniClient.create(
        api_key=os.getenv("GATE_API_KEY"),
        api_secret=os.getenv("GATE_API_SECRET"),
    )

    async with c:
        t = "BTC_USDT"

        # await c.futures_set_leverage(t, leverage=10)
        await c.futures_set_margin_type(t, MarginType.ISOLATED)

    # async with c:
    #     r = await c.futures_order_create(
    #         symbol="TRX_USDT",
    #         side=OrderSide.BUY,
    #         type=OrderType.MARKET,
    #         quantity="100",
    #         reduce_only=True,
    #     )
    #     from pprint import pp

    #     pp(r)


if __name__ == "__main__":
    asyncio.run(main())
