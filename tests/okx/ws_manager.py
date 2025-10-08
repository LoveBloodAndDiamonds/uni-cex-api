import asyncio
from operator import call

from unicex.okx import WebsocketManager


async def callback(msg):
    try:
        print(type(msg), msg)
    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    c = {"callback": callback}
    ws = manager.instruments(**c, inst_type="SWAP")
    ws = manager.open_interest(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.funding_rate(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.price_limit(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.option_summary(**c, inst_family="BTC-USD")
    ws = manager.estimated_price(**c, inst_type="FUTURES", inst_family="BTC-USD")  # type: ignore
    ws = manager.mark_price(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.index_tickers(**c, inst_id="BTC-USDT")
    ws = manager.mark_price_candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    ws = manager.index_candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    ws = manager.liquidation_orders(**c, inst_type="SWAP")
    ws = manager.adl_warning(**c, inst_type="SWAP")  # type: ignore
    ws = manager.tickers(**c, inst_id="BTC-USDT")
    ws = manager.candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    ws = manager.trades(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.all_trades(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.order_book(**c, channel="books", inst_id="BTC-USDT-SWAP")

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
