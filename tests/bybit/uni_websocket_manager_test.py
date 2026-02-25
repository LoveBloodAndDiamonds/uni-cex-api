import asyncio

from unicex.bybit import ExchangeInfo, UniWebsocketManager
from unicex.types import PartialBookDepthDict


async def callback(event: PartialBookDepthDict) -> None:
    """Выводит top-20 из полного локального стакана."""
    print(event["a"][:5])


async def main() -> None:
    """Запускает пример подписки на Bybit partial book depth."""
    await ExchangeInfo.start()

    # await asyncio.sleep(10)

    manager = UniWebsocketManager()
    ws = manager.futures_partial_book_depth(
        callback=callback,
        limit=50,
        symbols=["CYBERUSDT"],
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())


"""
gate +
okx +
bybit говно, присылает diff
binance +
bitget +
hyperliquid +
aster +
"""
