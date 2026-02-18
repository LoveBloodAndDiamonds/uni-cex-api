import asyncio

from unicex.binance import WebsocketManager, UniClient
from unicex.types import TradeDict


async def callback(lq: list[TradeDict]) -> None:
    print(type(lq))
    print(lq)
    print()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        tickers = await c.futures_tickers()

    manager = WebsocketManager()
    ws = manager.liquidation_order(callback=callback, symbols=tickers)
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
