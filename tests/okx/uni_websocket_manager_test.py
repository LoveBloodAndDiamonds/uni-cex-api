import asyncio

from unicex.okx import UniWebsocketManager, UniClient  # type: ignore # noqa
from unicex.types import PartialBookDepthDict, BestBidAskDict  # type: ignore # noqa
from time import time


async def callback(event: PartialBookDepthDict) -> None:
    """Выводит ликвидации в консоль."""
    print(int(time()), event)


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    t = ["BTC-USDT-SWAP"]
    manager = UniWebsocketManager()
    ws = manager.futures_partial_book_depth(
        callback=callback,
        symbols=t,
        limit=400,
    )
    await ws.start()


# async def callback(event: BestBidAskDict) -> None:
#     """Выводит ликвидации в консоль."""
#     print(int(time()), event)


# async def main() -> None:
#     """Запусти пример подписки на ликвидации Binance."""
#     t = ["BTC-USDT-SWAP"]
#     manager = UniWebsocketManager()
#     ws = manager.futures_best_bid_ask(
#         callback=callback,
#         symbols=t,
#     )
#     await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
