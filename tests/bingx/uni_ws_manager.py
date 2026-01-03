import asyncio

from unicex.bingx.uni_websocket_manager import UniWebsocketManager
from unicex.enums import Timeframe


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""

    manager = UniWebsocketManager()

    symbols = ["BTC-USDT"]

    # ws = manager.klines(callback=callback, timeframe=Timeframe.MIN_1, symbols=symbols)
    # ws = manager.futures_klines(callback=callback, timeframe=Timeframe.MIN_1, symbols=symbols)
    # ws = manager.trades(callback=callback, symbols=symbols)
    ws = manager.futures_trades(callback=callback, symbols=symbols)

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
