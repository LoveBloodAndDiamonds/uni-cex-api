import asyncio

from unicex.kucoin import Client


async def main() -> None:
    """Main entry point for the application."""
    c = await Client.create()

    # r = await c.ticker("FUTURES", symbol="ETHUSDTM")
    import time

    r = await c.funding_rate("XRP" + "USDTM")

    print(type(r["data"]["nextFundingRate"]))
    print(str(r["data"]["nextFundingRate"] * 100))

    from pprint import pp

    pp(r)

    await c.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
