from unicex.exchanges.binance import AsyncBinanceClient

from pprint import pp as print  # noqa # type: ignore


import asyncio


async def main() -> None:
    """Main entry point for the application."""

    client = await AsyncBinanceClient.create()

    # result = await client.exchange_info()

    async with client as cl:
        r = await cl.futures_exchange_info()
        print(r)

    # print(result)

    # await client.close()


if __name__ == "__main__":
    asyncio.run(main())
