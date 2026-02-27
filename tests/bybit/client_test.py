import asyncio

from unicex.bybit import Client

# +


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.tickers("linear")

        from pprint import pp

        for el in r["result"]["list"]:
            if el["symbol"] == "OXT" + "USDT":
                pp(el)


if __name__ == "__main__":
    asyncio.run(main())
