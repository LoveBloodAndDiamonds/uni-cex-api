from unicex.enums import Timeframe
from unicex.hyperliquid import Client, ExchangeInfo, UniClient


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()
    # await asyncio.sleep(3)

    # print(ExchangeInfo.resolve_spot_symbol("@38"))  # @52

    # return

    client = await UniClient.create()

    # r = await client.perp_meta_and_asset_contexts()
    r = await client.klines(symbol="@142", interval=Timeframe.MIN_5, limit=1)

    from pprint import pp

    pp(r)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
