import asyncio

from unicex.mexc import Client, ExchangeInfo
from unicex import Exchange, MarketType


async def main() -> None:
    """Main entry point for the application."""
    asyncio.create_task(ExchangeInfo.start())

    c = await Client.create()

    async with c:
        r = await c.futures_contract_detail()

        for el in r["data"]:
            symbol = el["symbol"]
            is_new = el.get("isNew")  # Обозначает что тикер был недавно добавлен
            is_delisting = el.get("automaticDelivery")  # Обозначает что тикер будет вскоре удален


if __name__ == "__main__":
    asyncio.run(main())
