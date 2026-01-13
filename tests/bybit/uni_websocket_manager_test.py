import asyncio

from unicex.bybit import UniWebsocketManager
from unicex.types import LiquidationDict


async def callback(lq: list[LiquidationDict]) -> None:
    print(type(lq))
    print(lq)
    print()


async def main() -> None:
    """Main entry point for the application."""
    manager = UniWebsocketManager()
    ws = manager.liquidations(
        callback=callback, symbols=["BTCUSDT", "ETHUSDT", "TRXUSDT", "ADAUSDT", "DOGEUSDT"]
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
