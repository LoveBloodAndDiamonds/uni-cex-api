import asyncio

from unicex.bitget import UniClient
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""

    client = await UniClient.create()

    r = await client.tickers_batched()

    pp(r)

    print(len(r))

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
