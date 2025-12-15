from unicex.kucoin import UniClient, start_exchange_info


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    await start_exchange_info()

    await asyncio.sleep(3)

    client = await UniClient.create()

    async with client as conn:
        r = await conn.open_interest()
        # r = await conn.futures_tickers()
        # r = await conn.last_price()
        # r = await conn.futures_last_price()
        # r = await conn.futures_ticker_24hr()
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
