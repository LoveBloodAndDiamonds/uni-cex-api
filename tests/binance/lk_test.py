from unicex.binance import Client
from unicex.binance.asyncio import Client as AsyncClient

import asyncio

from os import getenv


async def main() -> None:
    """Main entry point for the application."""
    api_key = getenv("BINANCE_API_KEY")
    secret_key = getenv("BINANCE_API_SECRET")

    client = Client(api_key, secret_key)
    async_client = await AsyncClient.create(api_key, secret_key)

    spot_lk = client.listen_key()
    print(f"{spot_lk=}")
    futures_lk = client.futures_listen_key()
    print(f"{futures_lk=}")

    spot_lk_async = await async_client.listen_key()
    print(f"{spot_lk_async=}")
    futures_lk_async = await async_client.futures_listen_key()
    print(f"{futures_lk_async=}")

    await async_client.close()
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
