import asyncio
from unicex.aster import ExchangeInfo


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()

    await asyncio.sleep(5)

    from pprint import pp

    print(ExchangeInfo.round_futures_quantity("BTCUSDT", 1.123456789))
    print(ExchangeInfo.round_futures_price("BTCUSDT", 123.123456789))


if __name__ == "__main__":
    asyncio.run(main())
