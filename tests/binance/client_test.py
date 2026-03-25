import asyncio

from unicex.binance import Client

# +


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        # r = await client.
        r = []

        from pprint import pp

        for el in r:
            if el["symbol"] == "TAIKO" + "USDT":
                pp(el)


if __name__ == "__main__":
    asyncio.run(main())
