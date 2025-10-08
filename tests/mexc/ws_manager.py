import asyncio

from unicex.mexc import WebsocketManager


async def callback(msg):
    print(type(msg), msg)


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    ws = manager.trade(callback=callback, symbol="BTCUSDT")

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
