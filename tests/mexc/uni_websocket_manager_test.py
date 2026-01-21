import asyncio

from unicex.mexc import UniWebsocketManager
from unicex.types import TradeDict


async def callback(lq: list[TradeDict]) -> None:
    print(type(lq))
    print(lq)
    print()


async def main() -> None:
    """Main entry point for the application."""
    manager = UniWebsocketManager()
    ws = manager.trades(
        callback=callback, symbols=["BTCUSDT", "ETHUSDT", "TRXUSDT", "ADAUSDT", "DOGEUSDT"]
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
