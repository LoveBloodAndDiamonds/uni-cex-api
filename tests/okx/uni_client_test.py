import asyncio

from unicex.okx import UniClient
from unicex.enums import *

from loguru import logger
from os import getenv


logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=getenv("OKX_API_KEY"),
        api_secret=getenv("OKX_API_SECRET"),
        api_passphrase=getenv("OKX_API_PASSPHRASE"),
    )

    async with c:
        t = "BTC-USDT-SWAP"

        r = await c.futures_set_leverage(t, leverage=13, margin_type=MarginType.ISOLATED)
        from pprint import pp

        pp(r)
        # r = # await c.futures_set_margin_type(t, MarginType.CROSSED)


if __name__ == "__main__":
    asyncio.run(main())
