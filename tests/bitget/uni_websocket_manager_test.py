import asyncio

from unicex.bybit import UniWebsocketManager, UniClient


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        tickers = await c.futures_tickers()

    manager = UniWebsocketManager()
    ws = manager.liquidations(callback=callback, symbols=tickers)

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
