import asyncio

from unicex.bitget import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_get_all_tickers("USDT-FUTURES")

        from pprint import pp

        for item in r["data"]:
            symbol = item["symbol"]
            del_time = item["deliveryTime"]
            del_status = item["deliveryStatus"]
            print(symbol, del_time, del_status)

        # for item in r["result"]["list"]:
        #     symbol = item["symbol"]
        #     deliviry_time = item["deliveryTime"]

        #     if symbol.endswith("USDT"):
        #         if deliviry_time != "0":
        #             print(symbol, deliviry_time)


if __name__ == "__main__":
    asyncio.run(main())
