import asyncio

from unicex.bybit.websocket_manager import WebsocketManager


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""

    manager = WebsocketManager()

    symbols = ["DOGEUSDT"]

    kwargs = dict(callback=callback, category="spot", symbols=symbols)

    # ws = manager.all_liquidation(**kwargs)
    # ws = manager.orderbook(**kwargs)
    ws = manager.klines(**kwargs, interval="1")  # type: ignore
    # ws = manager.public_trade(**kwargs)
    # ws = manager.ticker(**kwargs)  # type: ignore
    # ws = manager.liquidation(**kwargs)

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
