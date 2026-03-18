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
            # Exchange.BINANCE,
            # Exchange.BYBIT,
            # Exchange.BITGET,
            # Exchange.GATE,
            Exchange.ASTER,
        ]:
            continue

        try:
            funding_time = await client.funding_next_time()
            btc_time = funding_time.get("DEGOUSDT", None)
            if btc_time is None:
                btc_time = funding_time.get("XTZ_USDT", 0)
            print(f"{e}: funding_interval={btc_time}, {datetime.fromtimestamp(btc_time / 1000)}")

            print(len(funding_time))
        except NotImplementedError:
            print(f"{e}: funding_interval is not implemented")

        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
