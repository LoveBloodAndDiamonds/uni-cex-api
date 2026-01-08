import asyncio

from unicex.binance import UniWebsocketManager
from unicex.enums import Timeframe, Exchange
from unicex.utils import symbol_to_exchange_format
from unicex.mapper import get_uni_websocket_manager


async def callback(msg):
    print(msg)


EXCHANGE = Exchange.GATE
SYMBOL = ""
SYMBOLS = ["XRPUSDT", "ETHUSDT"]
# SYMBOLS = []


async def main() -> None:
    """Main entry point for the application."""
    symbol = symbol_to_exchange_format(SYMBOL, exchange=EXCHANGE) if SYMBOL else None
    symbols = [symbol_to_exchange_format(s, exchange=EXCHANGE) for s in SYMBOLS]
    manager = get_uni_websocket_manager(EXCHANGE)()
    # ws = manager.klines(
    #     callback=callback,
    #     timeframe=Timeframe.MIN_1,
    #     symbol=symbol,
    #     symbols=symbols,  # type: ignore
    # )  # type: ignore
    # ws = manager.futures_klines(
    #     callback=callback,
    #     timeframe=Timeframe.MIN_1,
    #     symbol=symbol,
    #     symbols=symbols,  # type: ignore
    # )  # type: ignore
    # ws = manager.trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore
    ws = manager.futures_trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore
    # ws = manager.aggtrades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore
    # ws = manager.futures_aggtrades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())


"""
futures:
{'time': 1767890715, 'time_ms': 1767890715198, 'channel': 'futures.trades', 'event': 'update', 'result': [{'id': 668036915, 'size': 63, 'create_time': 1767890715, 'create_time_ms': 1767890715198, 'price': '3108.95', 'contract': 'ETH_USDT'}]}

spot:
{'time': 1767890734, 'time_ms': 1767890734695, 'channel': 'spot.trades', 'event': 'update', 'result': {'id': 195515538, 'id_market': 195515538, 'create_time': 1767890734, 'create_time_ms': '1767890734695.323000', 'side': 'buy', 'currency_pair': 'ETH_USDT', 'amount': '2.1806', 'price': '3112.24', 'range': '195515538-195515538'}}
"""
