import asyncio

from unicex.base.websocket import BaseAioWebsocket


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""
    url = "wss://fstream.binance.com/ws/twtusdt@kline_1m"

    ws = BaseAioWebsocket(url=url, callback=callback)

    import asyncio

    await ws.start()

    await asyncio.sleep(100_000)


if __name__ == "__main__":
    asyncio.run(main())
