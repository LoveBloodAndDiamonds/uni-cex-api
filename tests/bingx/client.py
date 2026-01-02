import asyncio
import time

from unicex.bingx import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()

    async with client:
        timestamp = int(time.time() * 1000)

        def print_result(name: str, result: object) -> None:
            output = str(result)[:100]
            print(f"{name}: {output}\n")

        print_result(
            "futures_contracts",
            await client.futures_contracts(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_order_book",
            await client.futures_order_book(
                symbol="BTC-USDT",
                limit=20,
                timestamp=timestamp,
            ),
        )
        print_result(
            "futures_trades",
            await client.futures_trades(symbol="BTC-USDT", limit=10, timestamp=timestamp),
        )
        print_result(
            "futures_mark_price",
            await client.futures_mark_price(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_funding_rate_history",
            await client.futures_funding_rate_history(
                symbol="BTC-USDT", limit=2, timestamp=timestamp
            ),
        )
        print_result(
            "futures_klines",
            await client.futures_klines(
                symbol="BTC-USDT",
                interval="1h",
                limit=5,
                timestamp=timestamp,
            ),
        )
        print_result(
            "futures_open_interest",
            await client.futures_open_interest(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_ticker_24hr",
            await client.futures_ticker_24hr(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_historical_trades",
            await client.futures_historical_trades(
                symbol="BTC-USDT",
                limit=5,
                timestamp=timestamp,
            ),
        )
        print_result(
            "futures_book_ticker",
            await client.futures_book_ticker(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_mark_price_klines",
            await client.futures_mark_price_klines(
                symbol="BTC-USDT",
                interval="1h",
                limit=5,
                timestamp=timestamp,
            ),
        )
        print_result(
            "futures_ticker_price",
            await client.futures_ticker_price(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "futures_trading_rules",
            await client.futures_trading_rules(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result("symbols", await client.symbols(symbol="BTC-USDT", timestamp=timestamp))
        print_result(
            "trades",
            await client.trades(symbol="BTC-USDT", limit=5, timestamp=timestamp),
        )
        print_result(
            "order_book",
            await client.order_book(symbol="BTC-USDT", limit=20, timestamp=timestamp),
        )
        print_result(
            "klines",
            await client.klines(
                symbol="BTC-USDT",
                interval="1m",
                limit=5,
                timestamp=timestamp,
            ),
        )
        print_result(
            "ticker_24hr",
            await client.ticker_24hr(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "order_book_agg",
            await client.order_book_agg(
                symbol="BTC-USDT",
                depth=20,
                type_="step0",
                timestamp=timestamp,
            ),
        )
        print_result(
            "ticker_price",
            await client.ticker_price(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "book_ticker",
            await client.book_ticker(symbol="BTC-USDT", timestamp=timestamp),
        )
        print_result(
            "historical_klines",
            await client.historical_klines(
                symbol="BTC-USDT",
                interval="1m",
                limit=5,
            ),
        )
        print_result(
            "historical_trades",
            await client.historical_trades(symbol="BTC-USDT", limit=5),
        )


if __name__ == "__main__":
    asyncio.run(main())
