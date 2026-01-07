import asyncio

from unicex import Exchange, get_uni_client, MarketType, start_exchanges_info, KucoinExchangeInfo
from unicex.extra import generate_ex_link, generate_cg_link
from unicex.utils import symbol_to_exchange_format
from loguru import logger

# logger.remove()

# todo MEXC ошибка
# todo KUCOIN ошибка


async def main() -> None:
    """Main entry point for the application."""
    # asyncio.create_task(MexcExchangeInfo.start())
    await start_exchanges_info()

    await asyncio.sleep(2)

    # ticker_info = MexcExchangeInfo.get_futures_ticker_info("BTC_USDT")
    # print(ticker_info)

    # return

    for ex in Exchange:
        client_factory = get_uni_client(ex)
        client = await client_factory.create(logger=logger)
        async with client:
            try:
                if ex not in {Exchange.KUCOIN}:
                    continue
                symbol = symbol_to_exchange_format("BTCUSDT", ex, MarketType.FUTURES)
                response = await client.open_interest(symbol=symbol)
                ex_link = generate_ex_link(ex, MarketType.FUTURES, symbol=symbol)
                cg_link = generate_cg_link(ex, MarketType.FUTURES, symbol=symbol)
                # ticker_info = MexcExchangeInfo.get_futures_ticker_info(symbol)
                print(ex, response["v"], response["u"], ex_link, cg_link)
            except Exception as e:
                logger.exception(e)
                print(ex, e)


if __name__ == "__main__":
    asyncio.run(main())
