from unicex.binance import WebsocketManager, Client

from os import getenv


def main() -> None:
    """Main entry point for the application."""

    # import json

    # a = {"method": "SUBSCRIBE", "params": ["btcusdt@aggTrade"], "id": 1757169879029}
    # print(json.dumps(a))
    # exit()
    #

    client = Client(api_key=getenv("BINANCE_API_KEY"), api_secret=getenv("BINANCE_API_SECRET"))

    lk = client.futures_listen_key()
    print(lk)

    return

    bwm = WebsocketManager(client=client)
    ws = bwm.user_data_stream(callback=lambda m: print(m))
    ws.start()
    import time

    time.sleep(100000)


if __name__ == "__main__":
    main()

# import asyncio

# from unicex.binance.asyncio import WebsocketManager, Client
# from os import getenv


# async def callback(msg):
#     print(msg)


# async def main() -> None:
#     """Main entry point for the application."""
#     try:
#         client = await Client.create(
#             api_key=getenv("BINANCE_API_KEY"), api_secret=getenv("BINANCE_API_SECRET")
#         )

#         print(getenv("BINANCE_API_KEY"))
#         print(getenv("BINANCE_API_SECRET"))

#         lk = await client.futures_listen_key()
#         print(lk)

#         return

#         mgr = WebsocketManager(client=client)
#         user_ws = mgr.user_data_stream(callback=callback)

#         await user_ws.start()

#         await asyncio.sleep(10000)
#     finally:
#         await client.close()


# if __name__ == "__main__":
#     asyncio.run(main())
