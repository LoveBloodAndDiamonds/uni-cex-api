import asyncio

from unicex.aster import UniClient

import os

from loguru import logger

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.environ.get("ASTER_API_KEY"),
        api_secret=os.environ.get("ASTER_API_SECRET"),
    )

    async with c:
        tickers = await c.futures_tickers()

        for t in tickers:
            try:
                r = await c.client.futures_leverage_change(t, leverage=5)
                r2 = await c.client.futures_margin_type_change(t, "ISOLATED")
                print(f"{t}: {r}, {r2} \n")
            except Exception as e:
                print(f">>> {t}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
