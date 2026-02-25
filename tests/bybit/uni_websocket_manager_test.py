import asyncio

from unicex.bybit import UniWebsocketManager, UniClient, ExchangeInfo
from unicex.types import PartialBookDepthDict
from time import time


async def callback(event: PartialBookDepthDict) -> None:
    """Выводит ликвидации в консоль."""
    print(event["a"])


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    await ExchangeInfo.start()

    await asyncio.sleep(10)

    t = ["CYBERUSDT"]
    manager = UniWebsocketManager()
    ws = manager.futures_partial_book_depth(
        callback=callback,
        limit=123,
        symbols=t,
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
