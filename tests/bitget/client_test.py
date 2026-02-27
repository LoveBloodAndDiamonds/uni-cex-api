import asyncio

from unicex.bitget import Client

# +


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_get_all_tickers("USDT-FUTURES")

        from pprint import pp

        for el in r["data"]:
            if el["symbol"] == "1MCHEEMS" + "USDT":
                pp(el)


if __name__ == "__main__":
    asyncio.run(main())
