import asyncio

from unicex.bybit import UniWebsocketManager, UniClient
from unicex.types import LiquidationDict


async def callback(lq: list[LiquidationDict]) -> None:
    """Выводит ликвидации в консоль."""
    print(lq)


async def main() -> None:
    """Запусти пример подписки на ликвидации Binance."""
    c = await UniClient.create()
    async with c:
        t = await c.futures_tickers()
    manager = UniWebsocketManager()
    ws = manager.liquidations(callback=callback, symbols=t)
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
