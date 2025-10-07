import asyncio

from unicex.mexc import load_exchange_info, ExchangeInfo, UniClient
from pprint import pp


async def main() -> None:
    """Main entry point for the application."""
    await load_exchange_info()

    # pp(ExchangeInfo._futures_tickers_info)

    client = await UniClient.create()

    result = await client.futures_ticker_24hr()

    # spot {'p': 0.54, 'v': 10157.76177903, 'q': 1267201908.88}
    # fut:{'p': -0.47000000000000003, 'v': 38058.7512, 'q': 4751342042.00293}
    #

    # pp(result)

    pp(result["BAGWORK_USDT"])

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
