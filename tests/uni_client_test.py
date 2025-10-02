import asyncio
import sys
import time
from pprint import pp

from unicex import get_uni_client
from unicex._abc.uni_client import IUniClient
from unicex.enums import Exchange, MarketType, Timeframe
from loguru import logger

from unicex.utils import symbol_to_exchange_format

# ---------------- CONFIG ---------------- #

# Глобальный флаг: если True — тестируются все методы
test_all = False

# Индивидуальные флаги: если test_all=False, берём отсюда
tests_config = {
    "tickers": True,
    "tickers_batched": True,
    "futures_tickers": True,
    "futures_tickers_batched": True,
    "last_price": True,
    "futures_last_price": True,
    "ticker_24hr": True,
    "futures_ticker_24hr": True,
    "klines": True,
    "futures_klines": True,
    "open_interest": True,
    "single_open_interest": True,
    "funding_rate": True,
    "single_funding_rate": True,
}

# Тестировать ли все таймфреймы?
test_all_timeframes = True

# Какие биржи тестировать
exchanges = [
    Exchange.MEXC,
    Exchange.BYBIT,
    Exchange.BINANCE,
    Exchange.BITGET,
    Exchange.OKX,
    Exchange.GATEIO,
]
# exchanges = [Exchange.GATEIO]

# Сколько символов показывать в превью вывода
repr_len = 100

# ---------------------------------------- #

logger.remove()
logger.add(sys.stderr, level="INFO")


def should_run(test_name: str) -> bool:
    """Определяет, запускать ли тест."""
    return test_all or tests_config.get(test_name, False)


def pretty_print(exchange: Exchange, test_name: str, result):
    """Красивый вывод результата теста."""
    cyan = "\033[96m"
    reset = "\033[0m"
    print(f"{cyan}[{exchange}] [{test_name}]{reset}")
    print(f"  preview: {str(result)[:repr_len]}")
    try:
        print(f"  length : {len(result)}\n")
    except Exception:
        pass


async def test_exchange(e: Exchange, client: IUniClient) -> None:
    """Тестирование одной биржи."""
    f_symbol = symbol_to_exchange_format(
        symbol="BTCUSDT", exchange=e, market_type=MarketType.FUTURES
    )
    s_symbol = symbol_to_exchange_format(symbol="BTCUSDT", exchange=e, market_type=MarketType.SPOT)

    if should_run("tickers"):
        tickers = await client.tickers()
        pretty_print(e, "tickers", tickers)

    if should_run("tickers_batched"):
        tickers_batched = await client.tickers_batched()
        pretty_print(e, "tickers_batched", tickers_batched)

    if should_run("futures_tickers"):
        futures_tickers = await client.futures_tickers()
        pretty_print(e, "futures_tickers", futures_tickers)

    if should_run("futures_tickers_batched"):
        futures_tickers_batched = await client.futures_tickers_batched()
        pretty_print(e, "futures_tickers_batched", futures_tickers_batched)

    if should_run("last_price"):
        last_price = await client.last_price()
        pretty_print(e, "last_price", last_price)

    if should_run("futures_last_price"):
        futures_last_price = await client.futures_last_price()
        pretty_print(e, "futures_last_price", futures_last_price)

    if should_run("ticker_24hr"):
        ticker_24hr = await client.ticker_24hr()
        pretty_print(e, "ticker_24hr", ticker_24hr)

    if should_run("futures_ticker_24hr"):
        futures_ticker_24hr = await client.futures_ticker_24hr()
        pretty_print(e, "futures_ticker_24hr", futures_ticker_24hr)

    intervals = Timeframe if test_all_timeframes else [Timeframe.DAY_1]
    for interval in intervals:
        if should_run("klines"):
            klines = await client.klines(symbol=s_symbol, interval=interval, limit=10)
            pretty_print(e, f"{interval} klines", klines)

        if should_run("futures_klines"):
            futures_klines = await client.futures_klines(
                symbol=f_symbol, interval=interval, limit=10
            )
            pretty_print(e, f"{interval} futures_klines", futures_klines)

    if should_run("open_interest") and e not in [Exchange.BINANCE]:
        open_interest = await client.open_interest()
        pretty_print(e, "open_interest", open_interest)

    if should_run("single_open_interest"):
        single_open_interest = await client.open_interest(symbol=f_symbol)
        pretty_print(e, "single_open_interest", single_open_interest)

    if should_run("funding_rate") and e not in [Exchange.OKX]:
        funding_rate = await client.funding_rate()
        pretty_print(e, "funding_rate", funding_rate)

    if should_run("single_funding_rate"):
        single_funding_rate = await client.funding_rate(symbol=f_symbol)
        pretty_print(e, "single_funding_rate", single_funding_rate)


async def main() -> None:
    """Main entry point for the tests."""

    for exchange in exchanges:
        try:
            client = await get_uni_client(exchange).create(logger=logger)
            await test_exchange(exchange, client)
            print("-------------\n")
        except Exception as exc:
            logger.exception(f"[{exc}] Error: {exc}")
            sys.exit(1)
        finally:
            try:
                await client.close_connection()
            except:
                pass
        logger.success(f"[{exchange}] Success")

    logger.success("All exchanges tested successfully!")


if __name__ == "__main__":
    asyncio.run(main())
