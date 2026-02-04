import asyncio

from unicex.bybit import UniWebsocketManager


async def callback(msg) -> None:
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    m = UniWebsocketManager()
    s = m.aggtrades(symbol="BTCUSDT", callback=callback)
    await s.start()


if __name__ == "__main__":
    asyncio.run(main())
