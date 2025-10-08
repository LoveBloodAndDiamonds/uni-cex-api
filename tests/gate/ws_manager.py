import asyncio
from operator import call

from unicex.gateio import WebsocketManager


async def callback(msg):
    try:
        print(type(msg), msg)
    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    c = {"callback": callback}

    # ws = manager.tickers(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.trades(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.candlesticks(**c, symbols=["BTC_USDT", "ETH_USDT"], interval="10s")
    # ws = manager.book_ticker(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.order_book_update(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.order_book(**c, symbols=["BTC_USDT", "ETH_USDT"], level="5", interval="100ms")
    ws = manager.order_book_v2(**c, symbols=["BTC_USDT", "ETH_USDT"], level="400")

    # ws = manager.futures_tickers(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.futures_trades(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.futures_book_ticker(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.futures_order_book_update(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.futures_candlesticks(**c, symbols=["BTC_USDT", "ETH_USDT"], interval="10s")
    # ws = manager.futures_public_liquidates(**c, symbols=["BTC_USDT", "ETH_USDT"])
    # ws = manager.futures_contract_stats(**c, symbols=["BTC_USDT", "ETH_USDT"], interval="1d")
    # ws = manager.futures_order_book(**c, symbols=["BTC_USDT", "ETH_USDT"], limit="5", interval="0")
    # ws = manager.futures_order_book_v2(**c, symbols=["BTC_USDT", "ETH_USDT"], level="400")

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
