import asyncio

from unicex.mexc.exchange_info import ExchangeInfo


async def main() -> None:
    """Загружает и выводит информацию о нескольких тикерах Binance."""
    await ExchangeInfo.load_exchange_info()

    await asyncio.sleep(1)

    print("Spot tickers:")
    print(f"Len spot: {len(ExchangeInfo._tickers_info)}")
    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "PEPEUSDT", "ADAUSDT"]:
        info = ExchangeInfo.get_ticker_info(symbol)
        print(f"{symbol}: {info}")

    rounded = ExchangeInfo.round_price("BTCUSDT", 123456.123456789)
    print(rounded)
    rounded_2 = ExchangeInfo.round_quantity("BTCUSDT", 1.123456789)
    print(rounded_2)

    # print("\nFutures tickers:")
    # print(f"Len futures: {len(ExchangeInfo._futures_tickers_info)}")
    # for symbol in ["BTC_USDT", "XRP_USDT", "ETH_USDT", "SOL_USDT", "SUI_USDT"]:
    #     info = ExchangeInfo.get_futures_ticker_info(symbol)
    #     print(f"{symbol}: {info}")

    # rounded = ExchangeInfo.round_futures_price("BTC_USDT", 123456.123456789)
    # print(rounded)
    # rounded_2 = ExchangeInfo.round_futures_quantity("BTC_USDT", 1.123456789)
    # print(rounded_2)


if __name__ == "__main__":
    asyncio.run(main())
