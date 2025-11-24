from unicex.gate import UniClient


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create()

    async with client as conn:
        k = await conn.klines("BTC_USDT", "1m", limit=10)
        # k = await conn.futures_klines("BTC_USDT", "1m", limit=10)
        from pprint import pp

        pp(k)
        # r = await conn.futures_tickers()
        # print(len(r))


if __name__ == "__main__":
    asyncio.run(main())
