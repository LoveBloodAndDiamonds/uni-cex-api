import asyncio

from unicex.bitget.exchange_info import ExchangeInfo


async def main() -> None:
    """Загружает и выводит информацию о нескольких тикерах Binance."""
    await ExchangeInfo.load_exchange_info()

    print("Spot tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        info = ExchangeInfo.get_ticker_info(symbol)
        print(f"{symbol}: {info}")

    print("\nFutures tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        info = ExchangeInfo.get_futures_ticker_info(symbol)
        print(f"{symbol}: {info}")


if __name__ == "__main__":
    asyncio.run(main())
