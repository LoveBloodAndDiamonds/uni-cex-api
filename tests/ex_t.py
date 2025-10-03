import asyncio

from unicex import load_exchanges_info, start_exchanges_info, OkxExchangeInfo


async def main() -> None:
    """Main entry point for the application."""
    import time

    start = time.time()
    await start_exchanges_info(1)
    print(f"Loaded exchanges info in {time.time() - start:.2f} seconds")

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
