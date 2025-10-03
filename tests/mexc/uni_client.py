import asyncio

from unicex.mexc import load_exchange_info, ExchangeInfo, UniClient
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""
    await load_exchange_info()

    pp(ExchangeInfo._futures_tickers_info)

    client = await UniClient.create()

    result = await client.open_interest()

    pp(result["BTC_USDT"])

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
