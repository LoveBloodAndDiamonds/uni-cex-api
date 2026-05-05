import asyncio

from unicex.binance import WebsocketManager, UniClient
from unicex.types import TradeDict


async def callback(lq: list[TradeDict]) -> None:
    print(type(lq))
    print(lq)
    print()


async def main() -> None:
    """Main entry point for the application."""
    tickers = ["BTCUSDT", "ETHUSDT"]

    manager = WebsocketManager()
    ws = manager.futures_agg_trade(callback=callback, symbols=tickers)
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
