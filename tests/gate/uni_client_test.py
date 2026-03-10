import asyncio

from unicex import OrderSide, OrderType  # type: ignore
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
        tickers = await c.futures_tickers()

        for t in tickers:
            try:
                r = await c.client.futures_update_leverage("usdt", contract=t, leverage="5")
                r2 = await c.client.futures_switch_cross_mode("usdt", mode="ISOLATED", contract=t)
                print(f"{t}: {r}, {r2} \n")
            except Exception as e:
                print(f">>> {t}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
