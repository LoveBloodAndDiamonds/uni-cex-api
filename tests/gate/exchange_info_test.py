import asyncio

from unicex.gate import ExchangeInfo


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()

    from pprint import pp

    await asyncio.sleep(5)

    pp(ExchangeInfo._futures_tickers_info["SIREN_USDT"])


if __name__ == "__main__":
    asyncio.run(main())
