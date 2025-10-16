from unicex.gateio import UniClient


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create()

    async with client as conn:
        r = await conn.futures_tickers()
        print(len(r))


if __name__ == "__main__":
    asyncio.run(main())
