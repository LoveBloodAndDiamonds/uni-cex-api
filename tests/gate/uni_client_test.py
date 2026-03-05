import asyncio

from unicex import OrderSide, OrderType  # type: ignore
from unicex.gate import UniClient, ExchangeInfo

from loguru import logger  # type: ignore

import os


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()

    await asyncio.sleep(5)

    c = await UniClient.create(
        api_key=os.getenv("GATE_API_KEY"),
        api_secret=os.getenv("GATE_API_SECRET"),
    )

    async with c:
        r = {}
        r = await c.futures_order_create(
            symbol="TRX_USDT",
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity="150",
            # price="0.28",
            client_order_id="1232",
        )
        from pprint import pp

        pp(r)

        r = await c.futures_position_info("TRX_USDT")

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
