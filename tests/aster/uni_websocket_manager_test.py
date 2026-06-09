import asyncio
from time import time

from unicex.aster import UniClient, UniWebsocketManager  # type: ignore # noqa
from unicex.types import BestBidAskDict, PartialBookDepthDict  # type: ignore # noqa

# async def callback(event: PartialBookDepthDict) -> None:
#     """Выводит ликвидации в консоль."""
#     print(int(time()), len(event["b"]), event)
#     # exit(1)


# async def main() -> None:
#     """Запусти пример подписки на ликвидации Binance."""
#     t = ["BTCUSDT"]
#     manager = UniWebsocketManager()
#     ws = manager.futures_partial_book_depth(
#         callback=callback,
#         symbols=t,
#         limit=5,
#     )
#     await ws.start()


async def callback(event: BestBidAskDict) -> None:
    """Выводит ликвидации в консоль."""
    print(int(time()), event)


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    t = ["BTCUSDT"]
    manager = UniWebsocketManager()
    ws = manager.futures_best_bid_ask(
        callback=callback,
        symbols=t,
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
