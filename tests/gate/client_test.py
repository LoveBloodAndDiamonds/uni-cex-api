import asyncio

from unicex.gate import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_contracts("usdt")

        for i in r:
            symbol = i["name"]
            delisting_time = i.get("delisting_time")  # Если не делистниг то поля нет

            if delisting_time:
                import time

                t = time.time()
                print(symbol, delisting_time, delisting_time > t)


"""
BTC_USDT launch_time=1574035200 status='trading' is_pre_market=False

BDXN_USDT launch_time=1748945060 status='trading' is_pre_market=False
PENGUIN_USDT launch_time=1769256600 status='trading' is_pre_market=False
"""
# from pprint import pp

# pp(r)

# for item in r["data"]:
#     symbol = item["symbol"]
#     del_time = item["deliveryTime"]
#     del_status = item["deliveryStatus"]
#     print(symbol, del_time, del_status)


if __name__ == "__main__":
    asyncio.run(main())
