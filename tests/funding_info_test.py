import asyncio
from datetime import datetime

from unicex import Exchange, get_uni_client

from loguru import logger

logger.remove()


async def main() -> None:
    """Main entry point for the application."""

    for e in Exchange:
        client = await get_uni_client(e).create()

        if e not in [
            Exchange.BINANCE,
            # Exchange.BYBIT,
            # Exchange.BITGET,
            # Exchange.GATE,
            Exchange.ASTER,
        ]:
            await client.close_connection()
            continue

        try:
            funding_info = await client.funding_info()
            btc_info = funding_info.get("XRPUSDT", None)
            if btc_info is None:
                btc_info = funding_info.get("XRP_USDT", 0)
            print(f"{e}: {btc_info}")

            print(len(funding_info))
        except NotImplementedError:
            print(f"{e}: funding_info is not implemented")

        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
