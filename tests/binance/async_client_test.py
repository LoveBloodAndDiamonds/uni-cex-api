from unicex.binance.client import AsyncBinanceClient

from pprint import pp as print  # noqa # type: ignore


import asyncio


async def main() -> None:
    """Main entry point for the application."""

    client = await AsyncBinanceClient.create()

    result = await client.exchange_info()

    print(result)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
