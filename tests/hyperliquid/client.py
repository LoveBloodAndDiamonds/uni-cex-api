from unicex.hyperliquid import Client


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()

    from pprint import pp

    r2 = await client.predicted_fundings()

    pp(r2)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
