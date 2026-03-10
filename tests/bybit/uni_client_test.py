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

    # async with c:
    # tickers = await c.futures_tickers()

    # for t in tickers:
    #     try:
    #         # r = await c.client.set_leverage("linear", t, "5", "5")
    #         r = await c.client.set_margin_mode("ISOLATED_MARGIN")
    #         print(f"{t}: {r}")
    #     except Exception as e:
    #         print(f"{t}: {e}")

    async with c:
        r = await c.futures_order_create(
            symbol="TRXUSDT",
            side=OrderSide.BUY,
            type=OrderType.MARKET,
            quantity="100",
            reduce_only=True,
        )
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
