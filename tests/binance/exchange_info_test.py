import asyncio

from unicex.binance.exchange_info import ExchangeInfo as BinanceExchangeInfo


async def main() -> None:
    """Загружает и выводит информацию о нескольких тикерах Binance."""
    await BinanceExchangeInfo.load_exchange_info()

    print("Spot tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT"]:
        info = BinanceExchangeInfo.get_ticker_info(symbol)
        print(f"{symbol}: {info}")

    print("\nFutures tickers:")
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        info = BinanceExchangeInfo.get_futures_ticker_info(symbol)
        print(f"{symbol}: {info}")


if __name__ == "__main__":
    asyncio.run(main())
