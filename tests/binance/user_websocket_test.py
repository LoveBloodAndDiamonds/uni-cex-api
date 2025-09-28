import asyncio

from unicex.binance import WebsocketManager, Client
from os import getenv


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    try:
        client = await Client.create(
            api_key=getenv("BINANCE_API_KEY"), api_secret=getenv("BINANCE_API_SECRET")
        )

        mgr = WebsocketManager(client=client)
        user_ws = mgr.futures_user_data_stream(callback=callback)

        await user_ws.start()

        await asyncio.sleep(10000)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
