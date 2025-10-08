import asyncio

from unicex.mexc import WebsocketManager


async def callback(msg):
    try:
        print(type(msg), msg)
    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    # ws = manager.trade(callback=callback, symbols=["BTCUSDT", "ETHUSDT"])
    ws = manager.klines(callback=callback, symbols=["BTCUSDT", "ETHUSDT"], interval="Min1")

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
