import asyncio

from unicex.okx import load_exchange_info, ExchangeInfo, UniClient
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""
    await load_exchange_info()

    pp(ExchangeInfo._futures_tickers_info["BTC-USDT-SWAP"])

    client = await UniClient.create()

    result = await client.futures_tickers()

    # pp(result["BTC-USDT"])
    pp(result)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
