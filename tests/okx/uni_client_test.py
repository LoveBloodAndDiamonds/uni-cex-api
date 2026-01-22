import asyncio

from unicex.okx import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()
    async with c:
        # ticker = await c.futures_tickers()
        # print(ticker)
        fr = await c.funding_rate("ETH-USDT-SWAP")
        print(fr)

        from pprint import pp

        fr_raw = await c.client.get_funding_rate("ETH-USDT-SWAP")
        pp(fr_raw)


if __name__ == "__main__":
    asyncio.run(main())
