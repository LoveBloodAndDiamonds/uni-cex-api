"""Проверка обновления BingX API (2026-11): WS-подписка спота (U5), новые uni-методы.

Запуск: `python tests/bingx/api_update_test.py`
"""

import asyncio
import json
import time

from loguru import logger

from unicex.bingx import Client, UniClient, UniWebsocketManager, WebsocketManager

ERRORS: list[str] = []
logger.remove()
logger.add(lambda m: ERRORS.append(str(m)), level="ERROR")

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


def check_offline() -> None:
    """Подписка всегда содержит id; спотовая сделка-объект адаптируется."""
    messages = WebsocketManager()._generate_subscription_messages(["BTC-USDT@trade"])
    msg = json.loads(messages[0])
    check(bool(msg.get("id")) and msg["reqType"] == "sub", "U5 subscription has id", messages[0])

    from unicex.bingx.adapter import Adapter

    spot = {
        "code": 0,
        "data": {
            "E": 1,
            "T": 1794547190957,
            "e": "trade",
            "m": True,
            "p": "1",
            "q": "2",
            "s": "BTC-USDT",
        },
        "dataType": "BTC-USDT@trade",
    }
    trades = Adapter.trades_message(spot)
    check(
        len(trades) == 1 and trades[0]["S"] == "SELL", "U5 spot trade object adapted", str(trades)
    )


async def check_uni() -> None:
    """Новые uni-методы."""
    now = int(time.time() * 1000)
    async with await UniClient.create() as c:
        info = await c.funding_info("BTC-USDT")
        interval = await c.funding_interval("BTC-USDT")
        next_time = await c.funding_next_time("BTC-USDT")
        all_info = await c.funding_info()
        check(
            info["i"] == interval in (1, 2, 4, 8)
            and now < info["T"] == next_time
            and len(all_info) > 300,
            "funding_info / interval / next_time",
            f"{info}, n={len(all_info)}",
        )

        bba = await c.futures_best_bid_ask()
        one = await c.futures_best_bid_ask("BTC-USDT")
        check(len(bba) > 300 and one["b"] < one["a"], "futures_best_bid_ask", str(one))

        depth = await c.futures_depth("BTC-USDT", 20)
        check(
            len(depth["b"]) == 20 and depth["b"][0][0] < depth["a"][0][0],
            "futures_depth",
            f"bid={depth['b'][0]} ask={depth['a'][0]}",
        )

        delistings = await c.futures_delistings()
        check(isinstance(delistings, dict), "futures_delistings", f"n={len(delistings)}")

    async with await Client.create() as c:
        for name, coro in {
            "futures_trading_schedule": c.futures_trading_schedule(),
            "futures_server_time": c.futures_server_time(),
            "futures_trading_rules": c.futures_trading_rules("BTC-USDT"),
        }.items():
            res = await coro
            check(res.get("code") == 0, name, str(res)[:100])


async def run_ws(ws, seconds: float = 6) -> int:
    """Запускает вебсокет на `seconds` секунд и возвращает число сообщений."""
    counter = {"n": 0}
    callback = ws._callback

    async def counting(msg):  # noqa: ANN001
        counter["n"] += 1
        await callback(msg)

    ws._callback = counting
    task = asyncio.create_task(ws.start())
    await asyncio.sleep(seconds)
    await ws.stop()
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass
    return counter["n"]


async def check_ws() -> None:
    """Спотовые и фьючерсные сделки через uni WS без ошибок адаптера."""
    received: dict[str, int] = {"trades": 0, "futures_trades": 0}

    async def on_spot(_trade) -> None:  # noqa: ANN001
        received["trades"] += 1

    async def on_futures(_trade) -> None:  # noqa: ANN001
        received["futures_trades"] += 1

    uni = UniWebsocketManager()
    ERRORS.clear()
    await asyncio.gather(
        run_ws(uni.trades(on_spot, symbol="BTC-USDT"), 8),
        run_ws(uni.futures_trades(on_futures, symbol="BTC-USDT"), 8),
    )
    for name, n in received.items():
        check(n > 0, f"WS uni {name}", f"{n} trades")
    adapter_errors = [e for e in ERRORS if "adapting" in e or "100400" in e]
    check(
        not adapter_errors,
        "WS no adapter errors",
        adapter_errors[0][:150] if adapter_errors else "",
    )


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    check_offline()
    await check_uni()
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
