import asyncio

from unicex.hyperliquid import UniClient, ExchangeInfo


async def main() -> None:
    """Main entry point for the application."""
    asyncio.create_task(ExchangeInfo.start())

    await asyncio.sleep(3)

    c = await UniClient.create()

    async with c:
        t = await c.ticker_24hr(resolve_symbols=True)

        from pprint import pp

        pp(t)


if __name__ == "__main__":
    asyncio.run(main())
