import asyncio

from unicex.mexc import WebsocketManager
from unicex.types import TradeDict


async def callback(msg: dict) -> None:
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()
    ws = manager.trade(callback=callback, symbols=["BTCUSDT"])
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
