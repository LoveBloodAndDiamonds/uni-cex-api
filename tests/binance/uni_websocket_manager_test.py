import asyncio

from unicex.binance import UniWebsocketManager, UniClient
from unicex.types import PartialBookDepthDict
from time import time


async def callback(event: PartialBookDepthDict) -> None:
    """Выводит ликвидации в консоль."""
    print(time(), len(event["b"]))


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    c = await UniClient.create()
    async with c:
        t = await c.futures_tickers()
    t = ["BTCUSDT"]
    manager = UniWebsocketManager()
    ws = manager.futures_partial_book_depth(
        callback=callback,
        symbols=t,
        limit=5,
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
