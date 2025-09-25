import asyncio

from unicex.bitget.asyncio import UniWebsocketManager
from unicex import TradeDict


async def callback(trade: TradeDict):
    print(trade)


async def main() -> None:
    """Main entry point for the application."""
    uwm = UniWebsocketManager()

    socket = uwm.trades(
        callback=callback,
        symbol="BTCUSDT",
        # symbols=[
        #     "ETHUSDT",
        #     "XRPUSDT",
        # ],
    )

    await socket.start()


if __name__ == "__main__":
    asyncio.run(main())
