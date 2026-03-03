import asyncio

from unicex import get_uni_client, Exchange
from unicex.enums import MarketType
from unicex.utils import symbol_to_exchange_format

from loguru import logger

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    for e in [
        Exchange.ASTER,
        Exchange.BINANCE,
        Exchange.BYBIT,
        Exchange.BITGET,
        Exchange.GATE,
        Exchange.OKX,
    ]:
        client = await get_uni_client(e).create()

        ob = await client.futures_depth(
            symbol_to_exchange_format("ETHUSDT", exchange=e, market_type=MarketType.FUTURES), 5
        )

        print(e)
        print("ask: ", [item[0] for item in ob["a"]])
        print("bid: ", [item[0] for item in ob["b"]])
        print("---")

        await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
