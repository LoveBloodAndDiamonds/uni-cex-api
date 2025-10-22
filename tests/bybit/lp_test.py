import asyncio

from unicex import BybitUniClient


async def main() -> None:
    client = await BybitUniClient.create()

    last_prices = await client.futures_last_price()

    print(f"Current last price: {last_prices['DOGEUSDT']}")

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
