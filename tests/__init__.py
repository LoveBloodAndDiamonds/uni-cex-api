# from unicex._base.asyncio import BaseWebsocket, BaseClient
# from unicex._base import BaseWebsocket, BaseClient

# from unicex.bitget.asyncio import Websocket, Client

# from unicex.bitget import Websocket, Client

# from unicex._abc.asyncio import IUniWebsocketManager
# from unicex.binance.asyncio import UniWebsocketManager


# import asyncio

# from unicex.enums import Timeframe


# async def callback(msg):
#     print(msg)


# async def main() -> None:
#     """Main entry point for the application."""
#     uwm: IUniWebsocketManager = IUniWebsocketManager()
#     socket = uwm.klines(callback=callback, symbols=["BTCUSDT"], timeframe=Timeframe.MIN_5)
#     await socket.start()


# if __name__ == "__main__":
#     asyncio.run(main())
