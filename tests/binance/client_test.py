import asyncio

from unicex.binance import Client


from datetime import datetime


tickers = []


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_exchange_info()
        # r = await client.exchange_info()

        from pprint import pp

        # pp(r["symbols"])

        standart_delivery_date = 4133404800000
        import time

        now = time.time() * 1000
        for item in r["symbols"]:
            symbol = item["symbol"]
            delivery_ts = item["deliveryDate"]
            if symbol.endswith("USDT"):
                ticker = symbol.replace("USDT", "")
                if delivery_ts != standart_delivery_date and delivery_ts > now:
                    print(
                        ticker,
                        item["deliveryDate"],
                        datetime.fromtimestamp(item["deliveryDate"] / 1000),
                    )

        # for el in r[]:


if __name__ == "__main__":
    asyncio.run(main())
