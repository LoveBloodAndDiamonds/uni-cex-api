import asyncio

from unicex.bingx.websocket_manager import WebsocketManager


async def callback(msg):
    print(msg)


async def main() -> None:
    """Main entry point for the application."""

    manager = WebsocketManager()

    symbols = ["BTC-USDT", "ETH-USDT"]

    kwargs = dict(callback=callback, market_type="FUTURES", symbols=symbols)

    # ws = manager.trade(**kwargs)  # type: ignore
    # ws = manager.all_liquidation(**kwargs)
    # ws = manager.orderbook(**kwargs)
    ws = manager.klines(**kwargs, interval="1")
    # ws = manager.public_trade(**kwargs)
    # ws = manager.ticker(**kwargs)  # type: ignore
    # ws = manager.liquidation(**kwargs)

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
