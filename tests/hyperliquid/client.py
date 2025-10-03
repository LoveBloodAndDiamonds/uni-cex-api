from unicex.hyperliquid import Client


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()

    from pprint import pp

    resp = await client.spot_metadata()

    pp(resp)

    print(len(resp["universe"]))

    r2 = await client.spot_asset_contexts()

    pp(r2)

    print(len(r2[1]))

    r3 = await client.spot

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
