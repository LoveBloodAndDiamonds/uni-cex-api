import asyncio

from unicex.bybit import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.instruments_info("linear", limit=1000)

        from pprint import pp

        for item in r["result"]["list"]:
            symbol = item["symbol"]
            # print(symbol)

            # if symbol == "VFYUSDT":
            # print(item)

            deliviry_time = item["deliveryTime"]

            if symbol.endswith("USDT"):
                if deliviry_time != "0":
                    print(symbol, deliviry_time)

        # now = time.time() * 1000
        # for item in r["symbols"]:
        #     symbol = item["symbol"]
        #     delivery_ts = item["deliveryDate"]
        #     if symbol.endswith("USDT"):
        #         ticker = symbol.replace("USDT", "")
        #         if delivery_ts != standart_delivery_date and delivery_ts > now:
        #             print(
        #                 ticker,
        #                 item["deliveryDate"],
        #                 datetime.fromtimestamp(item["deliveryDate"] / 1000),
        #             )

        # for el in r[]:


if __name__ == "__main__":
    asyncio.run(main())
