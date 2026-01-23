import asyncio

from unicex.aster import UniWebsocketManager
from unicex.enums import Timeframe
from unicex.types import TradeDict


async def callback(msg) -> None:
    print(type(msg), msg)
    print()


async def main() -> None:
    """Main entry point for the application."""
    manager = UniWebsocketManager()
    ws = manager.futures_trades(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    # ws = manager.futures_klines(
    #     callback=callback, timeframe=Timeframe.MIN_1, symbols=["BTCUSDT", "ETHUSDT"]
    # )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
