import asyncio
from datetime import datetime

from unicex.bitget import Client
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        # r = await client.request(
        #     "GET", endpoint="/api/v2/margin/currencies", params={}, data={}, signed=False
        # )

        # pp(r)
        # print(len(r["data"]))
        #

        r = await client.get_symbol_info()

        pp(r)
        print(len(r["data"]))

        # for item in r["data"]:
        # symbol = item["symbol"]
        # print(symbol, areaSymbol)
        # from pprint import pp

        # pp(item)


if __name__ == "__main__":
    asyncio.run(main())
