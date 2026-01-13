import asyncio

from unicex.bybit import UniWebsocketManager
from unicex.types import LiquidationDict


async def callback(lq: LiquidationDict) -> None:
    print(lq)


async def main() -> None:
    """Main entry point for the application."""
    manager = UniWebsocketManager()
    ws = manager.liquidations(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
