import asyncio
from decimal import Clamped

from unicex.binance import WebsocketManager, Client


async def callback(msg):
    print(msg["data"]["U"])


async def main() -> None:
    """Main entry point for the application."""
    c = await Client.create()
    m = WebsocketManager(c)
    s = m.depth_stream(callback=callback, symbols=["BTCUSDT"], update_speed="100ms")
    await s.start()

    await c.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
