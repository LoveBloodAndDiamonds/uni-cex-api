import asyncio

from unicex.gate import UniWebsocketManager, UniClient, ExchangeInfo
from unicex.types import BestBidAskDict
from time import time


async def callback(event: BestBidAskDict) -> None:
    """Выводит ликвидации в консоль."""
    print(time(), event)


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    await ExchangeInfo.start()

    await asyncio.sleep(10)

    t = ["RVN_USDT"]
    manager = UniWebsocketManager()
    ws = manager.futures_best_bid_ask(
        callback=callback,
        symbols=t,
    )
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
