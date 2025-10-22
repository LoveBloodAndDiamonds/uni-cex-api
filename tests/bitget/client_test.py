import asyncio

from os import getenv
from unicex.bitget import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=getenv("BITGET_API_KEY"),
        api_secret=getenv("BITGET_API_SECRET"),
        api_passphrase=getenv("BITGET_API_PASSPHRASE"),
    )

    r = await client.get_current_orders()

    print(r)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
