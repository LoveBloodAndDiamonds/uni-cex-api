from unicex.enums import Timeframe
from unicex.kucoin import UniClient, start_exchange_info, ExchangeInfo
from unicex.utils import symbol_to_exchange_format


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    await start_exchange_info()

    # await asyncio.sleep(3)

    from pprint import pp

    # pp(ExchangeInfo._futures_tickers_info["BMTUSDTM"])

    # return

    client = await UniClient.create()

    async with client as conn:
        # symbol = symbol_to_exchange_format()
        # r = await conn.open_interest()
        # r = await conn.futures_tickers()
        # r = await conn.last_price()
        # r = await conn.futures_last_price()
        # r = await conn.futures_ticker_24hr()
        # r = await conn.futures_klines(symbol="ETHUSDT", interval=Timeframe.MIN_1, limit=3)
        # r = await conn.tickers()
        r = await conn.funding_rate("XBTUSDTM")
        from pprint import pp

        pp(r)


if __name__ == "__main__":
    asyncio.run(main())
