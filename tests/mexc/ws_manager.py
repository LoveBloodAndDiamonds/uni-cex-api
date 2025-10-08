import asyncio
from operator import call

from unicex.mexc import WebsocketManager


async def callback(msg):
    try:
        print(type(msg), msg)
    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    ws = manager.trade(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.klines(callback=callback, symbols=["BTCUSDT", "ETHUSDT"], interval="Min1")
    ws = manager.book_ticker_batch(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.book_ticker(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.diff_depth(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.partial_depth(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.futures_tickers(callback=callback)
    ws = manager.futures_ticker(callback=callback, symbols=["BTC_USDT", "ETH_USDT"])
    ws = manager.futures_depth(callback=callback, symbols=["BTC_USDT", "ETH_USDT"], limit=20)
    ws = manager.futures_kline(
        callback=callback, symbols=["BTC_USDT", "ETH_USDT"], interval="Min60"
    )
    ws = manager.funding_rate(callback=callback, symbols=["BTC_USDT", "ETH_USDT"])
    ws = manager.futures_index_price(callback=callback, symbols=["BTC_USDT", "ETH_USDT"])
    ws = manager.futures_fair_price(callback=callback, symbols=["BTC_USDT", "ETH_USDT"])
    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())


# good
# spot@public.aggre.deals.v3.api.pb@100ms

# bad:
# spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT


# good
# {"method": "SUBSCRIPTION", "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT", "spot@public.aggre.deals.v3.api.pb@100ms@ETHUSDT"]}
# {"method": "SUBSCRIPTION", "params": ["spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT", "spot@public.aggre.deals.v3.api.pb@100ms@ETHUSDT"]}


# {"id":0,"code":0,"msg":"spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT,spot@public.aggre.deals.v3.api.pb@100ms@ETHUSDT"}
# {'id': 0, 'code': 0, 'msg': 'spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT,spot@public.aggre.deals.v3.api.pb@100ms@ETHUSDT'}
