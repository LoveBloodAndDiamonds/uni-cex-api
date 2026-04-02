import asyncio

from unicex.binance import Client


from pprint import pp
import os


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )
    async with client:
        r = await client.request(
            "GET", "https://api.binance.com" + "/sapi/v1/margin/allPairs", {}, True
        )

        total = []
        for item in r:
            # print(item)
            if item["quote"] == "USDT":
                total.append(item)

        pp(len(total))


if __name__ == "__main__":
    asyncio.run(main())
