import asyncio

from unicex.bitget import WebsocketManager


async def callback(msg: dict):
    print(msg)


symbols = ["BTCUSDT", "ETHUSDT"]


async def main() -> None:
    """Main entry point for the application."""
    mgr = WebsocketManager()

    # ws = mgr.trade(callback=callback, symbols=symbols)
    ws = mgr.candlestick(callback=callback, symbols=symbols, interval="1m")
    ws = mgr.ticker(callback=callback, symbols=symbols)
    ws = mgr.auction(callback=callback, symbols=symbols)

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
