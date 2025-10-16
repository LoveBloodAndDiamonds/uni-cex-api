import asyncio

from unicex.bybit.exchange_info import ExchangeInfo


async def main() -> None:
    """Загружает и выводит информацию о нескольких тикерах Binance."""
    await ExchangeInfo.load_exchange_info()

    await asyncio.sleep(1)

    print("Spot tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        info = ExchangeInfo.get_ticker_info(symbol)
        print(f"{symbol}: {info}")

    print("\nFutures tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BLESSUSDT"]:
        info = ExchangeInfo.get_futures_ticker_info(symbol)
        print(f"{symbol}: {info}")

    print(len(ExchangeInfo._futures_tickers_info))

    from pprint import pp

    # pp(ExchangeInfo._futures_tickers_info)


if __name__ == "__main__":
    asyncio.run(main())
