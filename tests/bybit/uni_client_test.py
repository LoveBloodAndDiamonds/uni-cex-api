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
        tickers = await c.futures_tickers()

        for t in tickers:
            try:
                # r = await c.client.set_leverage("linear", t, "5", "5")
                r = await c.client.set_margin_mode("ISOLATED_MARGIN")
                print(f"{t}: {r}")
            except Exception as e:
                print(f"{t}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
