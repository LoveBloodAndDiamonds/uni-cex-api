from unicex.hyperliquid import UniClient


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await UniClient.create()

    from pprint import pp

    resp = await client.last_price()

    pp(resp)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
