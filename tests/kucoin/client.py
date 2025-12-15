import asyncio

from unicex.kucoin import Client


async def main() -> None:
    """Main entry point for the application."""
    c = await Client.create()

    r = await c.symbol("FUTURES", symbol="CUDISUSDTM")

    from pprint import pp

    pp(r)

    await c.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
