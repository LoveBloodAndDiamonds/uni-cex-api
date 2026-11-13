"""Проверка обновления Gate API (2026-11): U10, методы без ExchangeInfo, новые эндпоинты.

Запуск: `python tests/gate/api_update_test.py`
"""

import asyncio
import time

from loguru import logger

from unicex.enums import Timeframe
from unicex.gate import Client, UniClient, UniWebsocketManager

ERRORS: list[str] = []
logger.remove()
logger.add(lambda m: ERRORS.append(str(m)), level="ERROR")

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


def check_offline() -> None:
    """U10: время сделки со строкой вида '1794544524547.024000' приводится к int."""
    from unicex.gate.adapter import Adapter

    msg = {
        "result": {
            "create_time_ms": "1794544524547.024000",
            "currency_pair": "BTC_USDT",
            "side": "buy",
            "price": "1",
            "amount": "2",
        }
    }
    trades = Adapter.trades_message(msg)
    check(trades[0]["t"] == 1794544524547, "U10 spot WS trade t is int", str(trades))


async def check_uni_without_exchange_info() -> None:
    """Фьючерсные методы работают без запущенного ExchangeInfo (раньше падали)."""
    async with await UniClient.create() as c:
        klines = await c.futures_klines("BTC_USDT", Timeframe.MIN_1, limit=5)
        k = klines[-2]
        ratio = k["q"] / (k["v"] * k["c"]) if k["v"] else 0
        check(0.98 < ratio < 1.02, "futures_klines: v in coins", f"q/(v*c)={ratio:.4f}")

        depth = await c.futures_depth("BTC_USDT", 10)
        check(
            depth["b"][0][0] < depth["a"][0][0] and depth["b"][0][1] < 1_000,
            "futures_depth in coins",
            f"bid={depth['b'][0]}",
        )

        bba = await c.futures_best_bid_ask("BTC_USDT")
        check(bba["b"] < bba["a"] and bba["B"] < 1_000, "futures_best_bid_ask in coins", str(bba))


async def check_client() -> None:
    """Новые публичные эндпоинты."""
    async with await Client.create() as c:
        calls = {
            "server_time": c.server_time(),
            "rpi_order_book": c.rpi_order_book("BTC_USDT"),
            "futures_rpi_order_book": c.futures_rpi_order_book("usdt", "BTC_USDT"),
            "futures_adl_risk_states": c.futures_adl_risk_states("usdt"),
            "futures_contracts_all": c.futures_contracts_all("usdt", limit=5),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(bool(res), name, f"{type(res).__name__} {str(res)[:80]}")
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")

        try:
            await c.futures_trail_orders("usdt")
            check(False, "futures_trail_orders requires auth")
        except Exception as e:
            check(type(e).__name__ == "NotAuthorized", "futures_trail_orders requires auth")


async def run_ws(ws, seconds: float = 8) -> None:
    """Запускает вебсокет на `seconds` секунд."""
    task = asyncio.create_task(ws.start())
    await asyncio.sleep(seconds)
    await ws.stop()
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass


async def check_ws() -> None:
    """Спотовые сделки через uni WS: t — int."""
    received: list = []

    async def cb(item) -> None:  # noqa: ANN001
        received.append(item)

    ERRORS.clear()
    await run_ws(UniWebsocketManager().trades(cb, symbol="BTC_USDT"))
    ok = bool(received) and all(isinstance(t["t"], int) for t in received)
    check(ok, "WS uni trades (t is int)", f"n={len(received)} sample={received[:1]}")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    check_offline()
    await check_uni_without_exchange_info()
    await check_client()
    await check_ws()
    failed = [name for ok, name in RESULTS if not ok]
    print(
        f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed in {time.monotonic() - started:.1f}s"
    )
    if failed:
        print("FAILED:", ", ".join(failed))
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
