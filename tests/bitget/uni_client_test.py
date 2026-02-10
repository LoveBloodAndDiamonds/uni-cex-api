import asyncio

from unicex.bybit import UniClient


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create()

    async with c:
        t = await c.ticker_24hr()

    top_50_symbols = [
        symbol for symbol, _ in sorted(t.items(), key=lambda item: item[1]["q"], reverse=True)[:50]
    ]

    print(top_50_symbols)


if __name__ == "__main__":
    asyncio.run(main())
