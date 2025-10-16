import asyncio

from unicex.gateio.exchange_info import ExchangeInfo


async def main() -> None:
    """Загружает и выводит информацию о нескольких тикерах Binance."""
    await ExchangeInfo.load_exchange_info()

    await asyncio.sleep(1)

    print("Spot tickers:")
    print(f"Len spot: {len(ExchangeInfo._tickers_info)}")
    for symbol in ["BTC_USDT", "ETH_USDT", "BNB_USDT"]:
        info = ExchangeInfo.get_ticker_info(symbol)
        print(f"{symbol}: {info}")

    print("\nFutures tickers:")
    print(f"Len futures: {len(ExchangeInfo._futures_tickers_info)}")
    for symbol in ["BTC_USDT", "XRP_USDT", "ETH_USDT"]:
        info = ExchangeInfo.get_futures_ticker_info(symbol)
        print(f"{symbol}: {info}")


if __name__ == "__main__":
    asyncio.run(main())
