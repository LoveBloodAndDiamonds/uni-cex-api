import asyncio

from unicex.kucoin import Client


async def main() -> None:
    """Main entry point for the application."""
    c = await Client.create()

    # r = await c.ticker("FUTURES", symbol="ETHUSDTM")
    import time

    r = await c.funding_rate_history(
        symbol="ETHUSDTM",
        start_at=int(time.time() * 1000 - 100 * 100000),
        end_at=int(time.time() * 1000),
    )

    from pprint import pp

    pp(r)

    await c.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
