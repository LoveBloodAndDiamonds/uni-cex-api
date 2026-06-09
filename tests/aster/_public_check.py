"""Ad-hoc проверка публичных (не требующих подписи) методов UniClient Aster."""

import asyncio

from loguru import logger

from unicex.aster import UniClient

logger.remove()

SYMBOL = "BTCUSDT"


def _short(value: object, limit: int = 200) -> str:
    """Укорачивает представление значения для компактного вывода."""
    text = repr(value)
    return text if len(text) <= limit else f"{text[:limit]}... (len={len(text)})"


async def _run(name: str, coro) -> None:
    """Выполняет один вызов и печатает результат или ошибку."""
    try:
        result = await coro
        print(f"[OK]   {name}: {_short(result)}")
    except Exception as exc:  # noqa: BLE001 - в тесте ловим всё, чтобы пройти весь список
        print(f"[FAIL] {name}: {type(exc).__name__}: {exc}")


async def main() -> None:
    """Прогоняет все публичные методы UniClient по очереди."""
    c = await UniClient.create()
    async with c:
        # Спотовые методы (ранее кидали NotSupported)
        await _run("tickers (spot)", c.tickers())
        await _run("last_price (spot)", c.last_price())
        await _run("ticker_24hr (spot)", c.ticker_24hr())
        await _run("klines (spot)", c.klines(SYMBOL, "1h", limit=3))

        # Методы без аргументов / с дефолтами
        await _run("futures_tickers", c.futures_tickers())
        await _run("futures_last_price", c.futures_last_price())
        await _run("futures_ticker_24hr", c.futures_ticker_24hr())
        await _run("futures_klines", c.futures_klines(SYMBOL, "1h", limit=3))

        # Фандинг — и общий словарь, и по конкретному тикеру
        await _run("funding_rate (all)", c.funding_rate())
        await _run("funding_rate (symbol)", c.funding_rate(SYMBOL))
        await _run("funding_interval (all)", c.funding_interval())
        await _run("funding_next_time (all)", c.funding_next_time())
        await _run("funding_info (all)", c.funding_info())
        await _run("funding_info (symbol)", c.funding_info(SYMBOL))

        # Открытый интерес
        await _run("open_interest (all)", c.open_interest())
        await _run("open_interest (symbol)", c.open_interest(SYMBOL))

        # Лучшие bid/ask и стакан
        await _run("futures_best_bid_ask (all)", c.futures_best_bid_ask())
        await _run("futures_best_bid_ask (symbol)", c.futures_best_bid_ask(SYMBOL))
        await _run("futures_depth", c.futures_depth(SYMBOL, limit=5))

        # Делистинги
        await _run("futures_delistings", c.futures_delistings())


if __name__ == "__main__":
    asyncio.run(main())
