import asyncio

from unicex.binance import UniWebsocketManager
from unicex.enums import MarketType, Timeframe, Exchange
from unicex.utils import symbol_to_exchange_format
from unicex.mapper import get_uni_websocket_manager


async def callback(msg):
    print(msg)


EXCHANGE = Exchange.OKX
SYMBOL = "ETHUSDT"
SYMBOLS = ["XRPUSDT", "TRXUSDT"]
SYMBOLS = []


async def main() -> None:
    """Main entry point for the application."""
    symbol = symbol_to_exchange_format(SYMBOL, exchange=EXCHANGE, market_type=MarketType.FUTURES)
    symbols = [symbol_to_exchange_format(s, exchange=EXCHANGE) for s in SYMBOLS]
    manager = get_uni_websocket_manager(EXCHANGE)()
    ws = manager.klines(
        callback=callback,
        timeframe=Timeframe.MIN_1,
        symbol=symbol,
        symbols=symbols,  # type: ignore
    )  # type: ignore
    # ws = manager.trades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore
    # ws = manager.aggtrades(callback=callback, symbol=symbol, symbols=symbols)  # type: ignore

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
