import asyncio

from pprint import pp
import sys
from unicex import get_uni_client

from unicex.enums import Exchange, Timeframe
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")

exchanges = [Exchange.BYBIT, Exchange.BINANCE, Exchange.BITGET]
"""Exchanges to test."""


async def main() -> None:
    """Main entry point for the tests."""

    for e in exchanges:
        try:
            client = await get_uni_client(e).create(logger=logger)

            tickers = await client.tickers()
            print(f"[{e}] [tickers] {str(tickers)[:70]=}\n{len(tickers)=}\n")

            tickers_batched = await client.tickers_batched()
            print(
                f"[{e}] [tickers_batched] {str(tickers_batched)[:70]=}\n{len(tickers_batched)=}\n"
            )

            futures_tickers = await client.futures_tickers()
            print(
                f"[{e}] [futures_tickers] {str(futures_tickers)[:70]=}\n{len(futures_tickers)=}\n"
            )

            futures_tickers_batched = await client.futures_tickers_batched()
            print(
                f"[{e}] [futures_tickers_batched] {str(futures_tickers_batched)[:70]=}\n{len(futures_tickers_batched)=}\n"
            )

            last_price = await client.last_price()
            print(f"[{e}] [last_price] {str(last_price)[:70]=}\n{len(last_price)=}\n")

            futures_last_price = await client.futures_last_price()
            print(
                f"[{e}] [futures_last_price] {str(futures_last_price)[:70]=}\n{len(futures_last_price)=}\n"
            )

            ticker_24hr = await client.ticker_24hr()
            print(f"[{e}] [ticker_24hr] {str(ticker_24hr)[:70]=}\n{len(ticker_24hr)=}\n")

            futures_ticker_24hr = await client.futures_ticker_24hr()
            print(
                f"[{e}] [futures_ticker_24hr] {str(futures_ticker_24hr)[:70]=}\n{len(futures_ticker_24hr)=}\n"
            )

            klines = await client.klines(symbol="BTCUSDT", interval=Timeframe.DAY_1, limit=10)
            print(f"[{e}] [klines] {str(klines)[:70]=}\n{len(klines)=}\n")

            futures_klines = await client.futures_klines(
                symbol="BTCUSDT", interval=Timeframe.DAY_1, limit=10
            )
            print(f"[{e}] [futures_klines] {str(futures_klines)[:70]=}\n{len(futures_klines)=}\n")

            if e not in [Exchange.BINANCE]:
                open_interest = await client.open_interest()
                print(f"[{e}] [open_interest] {str(open_interest)[:70]=}\n{len(open_interest)=}\n")

            single_open_interest = await client.open_interest(symbol="BTCUSDT")
            print(
                f"[{e}] [single_open_interest] {str(single_open_interest)[:70]=}\n{len(single_open_interest)=}\n"
            )

            print("-------------\n")

        except Exception as exc:
            logger.error(f"[{e}] Error: {exc}")
            sys.exit(1)
        finally:
            try:
                await client.close_connection()
            except:
                pass
    logger.success(f"[{e}] Success")


if __name__ == "__main__":
    asyncio.run(main())
