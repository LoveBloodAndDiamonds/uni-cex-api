import asyncio

from unicex import load_exchanges_info, start_exchanges_info, OkxExchangeInfo, MexcExchangeInfo


async def main() -> None:
    """Main entry point for the application."""
    import time

    start = time.time()
    await start_exchanges_info(1)
    print(f"Loaded exchanges info in {time.time() - start:.2f} seconds")

    while True:
        await asyncio.sleep(1)
        print(str(OkxExchangeInfo._tickers_info)[:100], "\n\n")
        print(str(OkxExchangeInfo._futures_tickers_info)[:100], "\n\n")
        print(str(MexcExchangeInfo._futures_tickers_info)[:100], "\n\n")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
