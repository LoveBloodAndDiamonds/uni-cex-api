import asyncio

from unicex import Exchange, get_uni_client


async def main() -> None:
    """Main entry point for the application."""

    for e in Exchange:
        client = await get_uni_client(e).create()

        if e in [Exchange.BINANCE, Exchange.BYBIT]:
            continue

        try:
            interval = await client.funding_interval()
            print(f"{e}: funding_interval={interval}")
        except NotImplementedError:
            print(f"{e}: funding_interval is not implemented")

        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
