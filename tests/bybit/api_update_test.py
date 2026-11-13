"""Проверка обновления Bybit API (2026-11): новые эндпоинты и WS-каналы, abandoned-методы.

Запуск: `python tests/bybit/api_update_test.py`
"""

import asyncio
import time
import warnings

from loguru import logger

from unicex.bybit import Client, WebsocketManager

logger.remove()

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


async def check_client() -> None:
    """Новые публичные эндпоинты и предупреждения abandoned-методов."""
    async with await Client.create() as c:
        calls = {
            "full_orderbook": c.full_orderbook("linear", "BTCUSDT"),
            "instrument_summary": c.instrument_summary("linear", symbol="BTCUSDT"),
            "corporate_action": c.corporate_action(),
            "option_base_coins": c.option_base_coins(),
            "announcements": c.announcements("en-US", limit=3),
            "system_status": c.system_status(),
            "instruments_info(symbolType)": c.instruments_info("linear", symbol="BTCUSDT"),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(res.get("retCode") == 0, name, str(res.get("result"))[:90])
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")

        full = (await c.full_orderbook("linear", "BTCUSDT"))["result"]
        check(len(full["b"]) > 1000, "full_orderbook depth > 1000 levels", f"bids={len(full['b'])}")

    client = Client(session=None, api_key="k", api_secret="s")  # type: ignore[arg-type]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        coro = client.set_tpsl_mode("linear", "BTCUSDT", "Full")
        try:
            coro.send(None)
        except Exception:  # noqa: S110
            pass
        finally:
            coro.close()
    check(
        any(issubclass(w.category, DeprecationWarning) for w in caught),
        "abandoned set_tpsl_mode warns",
    )


async def count_messages(ws, seconds: float = 6) -> int:
    """Запускает вебсокет и считает сообщения с данными (без ответов на подписку)."""
    counter = {"n": 0}

    async def cb(msg) -> None:  # noqa: ANN001
        if "topic" in msg:
            counter["n"] += 1

    ws._callback = cb
    task = asyncio.create_task(ws.start())
    await asyncio.sleep(seconds)
    await ws.stop()
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass
    return counter["n"]


async def noop(_msg) -> None:  # noqa: ANN001
    """Пустой callback."""


async def check_ws() -> None:
    """Новые публичные WS-каналы."""
    m = WebsocketManager()
    streams = {
        "orderbook depth=1000": m.orderbook(noop, "linear", depth=1000, symbol="BTCUSDT"),
        "full_orderbook": m.full_orderbook(noop, "linear", symbol="BTCUSDT"),
        "orderbook_rpi": m.orderbook_rpi(noop, "linear", symbol="BTCUSDT"),
        "order_price_limit": m.order_price_limit(noop, "linear", symbol="BTCUSDT"),
        "adl_alert": m.adl_alert(noop, "USDT"),
        "insurance_pool": m.insurance_pool(noop, "USDT"),
    }
    counts = await asyncio.gather(*(count_messages(ws) for ws in streams.values()))
    for (name, _), n in zip(streams.items(), counts, strict=True):
        check(n > 0, f"WS {name}", f"{n} msgs")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
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
