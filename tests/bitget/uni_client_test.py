import asyncio

from unicex.bitget import UniClient
from pprint import pp

from unicex.enums import Timeframe


async def main() -> None:
    """Main entry point for the application."""

    client = await UniClient.create()

    r = await client.open_interest()

    pp(r)

    print(len(r))

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
