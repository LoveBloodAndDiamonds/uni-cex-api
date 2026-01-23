import asyncio

from unicex.aster import WebsocketManager


async def callback(msg):
    print(type(msg), msg)
    print()


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    ws = manager.futures_agg_trade(callback=callback, symbols=["ETHUSDT", "BTCUSDT"])
    # ws = manager.futures_symbol_mark_price(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_mark_price(callback=callback)
    # ws = manager.futures_klines(callback=callback, symbol="ETHUSDT", interval="1m")
    # ws = manager.futures_symbol_mini_ticker(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_mini_ticker(callback=callback)
    # ws = manager.futures_symbol_ticker(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_ticker(callback=callback)
    # ws = manager.futures_symbol_book_ticker(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_book_ticker(callback=callback)
    # ws = manager.futures_liquidation_order(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_all_liquidation_orders(callback=callback)
    # ws = manager.futures_partial_book_depth(callback=callback, symbol="ETHUSDT", levels="5")
    # ws = manager.futures_diff_depth(callback=callback, symbol="ETHUSDT")
    # ws = manager.futures_multiplex_socket(
    #     callback=callback, streams="ethusdt@aggTrade/btcusdt@markPrice"
    # )

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
