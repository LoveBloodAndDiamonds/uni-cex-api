from unicex import get_uni_client


import asyncio

from unicex.enums import Exchange, MarketType
from unicex.utils import symbol_to_exchange_format
from unicex.extra import generate_ex_link
from unicex import start_exchanges_info
from loguru import logger

logger.remove()


async def main() -> None:
    """Main entry point for the application."""

    await start_exchanges_info()

    for e in Exchange:
        if e in [
            Exchange.BITUNIX,
            Exchange.BINANCE,
            Exchange.BITGET,
            Exchange.BYBIT,
            Exchange.GATEIO,
            Exchange.KCEX,
            Exchange.HYPERLIQUID,
            Exchange.MEXC,
            Exchange.OKX,
            Exchange.XT,
        ]:
            continue

        client = await get_uni_client(e).create(logger=logger)

        async with client as conn:
            ticker_daily = await conn.ticker_24hr()
            futures_ticker_daily = await conn.futures_ticker_24hr()
            last_price = await conn.last_price()
            futures_last_price = await conn.futures_last_price()

            from pprint import pp

            print("=" * 80)
            print(e)

            symbol = symbol_to_exchange_format("BTCUSDT", e, MarketType.SPOT)
            print("spot: ", generate_ex_link(e, MarketType.SPOT, symbol))
            print(symbol)
            pp(ticker_daily[symbol])
            pp(last_price[symbol])
            symbol = symbol_to_exchange_format("BTCUSDT", e, MarketType.FUTURES)
            print("futures: ", generate_ex_link(e, MarketType.FUTURES, symbol))
            pp(futures_ticker_daily[symbol])
            pp(futures_last_price[symbol])


if __name__ == "__main__":
    asyncio.run(main())
