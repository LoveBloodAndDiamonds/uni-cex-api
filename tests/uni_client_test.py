import asyncio
import sys
import time
from pprint import pp

from unicex import get_uni_client, start_exchanges_info
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
test_all_timeframes = False

# Какие биржи тестировать
exchanges = [
    Exchange.HYPERLIQUID,
    Exchange.MEXC,
    Exchange.BYBIT,
    Exchange.BINANCE,
    Exchange.BITGET,
    Exchange.OKX,
    Exchange.GATE,
    Exchange.KUCOIN,
    Exchange.BINGX,
    Exchange.ASTER,
]

# Сколько символов показывать в превью вывода
repr_len = 100

# Настройки логирования
logger.remove()
logger.add(sys.stderr, level="INFO")

# ---------------- LOGIC ---------------- #


def should_run(name: str) -> bool:
    return test_all or tests_config.get(name, False)


async def safe_call(exc, func, *args, **kwargs):
    """Безопасный вызов метода клиента, возвращает (ok, result_or_error)."""
    try:
        res = await func(*args, **kwargs)
        if repr_len:
            print(f"{exc} {func.__name__} {str(res)[:repr_len]}")
        return True, res
    except Exception as exc:
        return False, str(exc)


async def test_exchange(exchange: Exchange) -> dict:
    """Тестирует все методы для конкретной биржи, возвращает результаты."""
    results = {}
    start = time.perf_counter()

    try:
        client: IUniClient = await get_uni_client(exchange).create(logger=logger)
    except Exception as e:
        return {"_fatal_": str(e)}

    try:
        f_symbol = symbol_to_exchange_format("ETHUSDT", exchange, MarketType.FUTURES)
        s_symbol = symbol_to_exchange_format("BTCUSDT", exchange, MarketType.SPOT)

        if should_run("tickers"):
            results["tickers"] = await safe_call(exchange, client.tickers)
        if should_run("tickers_batched"):
            results["tickers_batched"] = await safe_call(exchange, client.tickers_batched)
        if should_run("futures_tickers"):
            results["futures_tickers"] = await safe_call(exchange, client.futures_tickers)
        if should_run("futures_tickers_batched"):
            results["futures_tickers_batched"] = await safe_call(
                exchange, client.futures_tickers_batched
            )
        if should_run("last_price"):
            results["last_price"] = await safe_call(exchange, client.last_price)
        if should_run("futures_last_price"):
            results["futures_last_price"] = await safe_call(exchange, client.futures_last_price)
        if should_run("ticker_24hr"):
            results["ticker_24hr"] = await safe_call(exchange, client.ticker_24hr)
        if should_run("futures_ticker_24hr"):
            results["futures_ticker_24hr"] = await safe_call(exchange, client.futures_ticker_24hr)

        intervals = Timeframe if test_all_timeframes else [Timeframe.DAY_1]
        for interval in intervals:
            if should_run("klines"):
                results[f"klines_{interval.name}"] = await safe_call(
                    exchange, client.klines, symbol=s_symbol, interval=interval, limit=10
                )
            if should_run("futures_klines"):
                results[f"futures_klines_{interval.name}"] = await safe_call(
                    exchange, client.futures_klines, symbol=f_symbol, interval=interval, limit=10
                )

        if should_run("open_interest") and exchange not in [Exchange.BINANCE, Exchange.BINGX]:
            results["open_interest"] = await safe_call(exchange, client.open_interest)
        if should_run("single_open_interest"):
            results["single_open_interest"] = await safe_call(
                exchange, client.open_interest, symbol=f_symbol
            )
        if should_run("funding_rate") and exchange not in [Exchange.OKX, Exchange.KUCOIN]:
            results["funding_rate"] = await safe_call(exchange, client.funding_rate)
        if should_run("single_funding_rate"):
            results["single_funding_rate"] = await safe_call(
                exchange, client.funding_rate, symbol=f_symbol
            )

    finally:
        try:
            await client.close_connection()
        except Exception:
            pass

    duration = round(time.perf_counter() - start, 2)
    results["_time_"] = duration

    return results


async def main():
    """Запускает тесты параллельно и выводит сводку."""
    all_results = await asyncio.gather(
        *[test_exchange(e) for e in exchanges], return_exceptions=False
    )

    print("\n\n==================== TEST SUMMARY ====================\n")

    for exchange, results in zip(exchanges, all_results):
        name = f"[{exchange}]"
        if "_fatal_" in results:
            print(f"\033[91m{name} ❌ FAILED TO START: {results['_fatal_']}\033[0m")
            continue

        time_s = results.pop("_time_")
        ok_count = sum(1 for ok, _ in results.values() if ok)
        total = len(results)
        color = "\033[92m" if ok_count == total else "\033[91m"
        status = "✅ OK" if ok_count == total else "❌ ERRORS"
        print(f"{color}{name} {status} ({ok_count}/{total} passed) [{time_s:.2f}s]\033[0m")

        # выводим упавшие тесты
        failed = {k: v for k, (ok, v) in results.items() if not ok}
        if failed:
            for k, err in failed.items():
                print(f"   - {k}: {err}")

        print()

    print("=====================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
