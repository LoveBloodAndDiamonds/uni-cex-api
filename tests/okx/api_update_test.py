"""Проверка обновления OKX API (2026-11): адаптеры U7–U9, WS без порта 8443, новые эндпоинты.

Запуск: `python tests/okx/api_update_test.py`
"""

import asyncio
import time

from loguru import logger

from unicex.enums import Timeframe
from unicex.okx import Client, UniClient, UniWebsocketManager, WebsocketManager

ERRORS: list[str] = []
logger.remove()
logger.add(lambda m: ERRORS.append(str(m)), level="ERROR")

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


def check_offline() -> None:
    """None-поля не попадают в подписываемое тело POST-запроса."""
    client = Client(session=None, api_key="k", api_secret="s", api_passphrase="p")  # type: ignore[arg-type]
    _, _, body, _ = client._prepare_request_params(
        method="POST",
        endpoint="/api/v5/trade/order-algo",
        signed=True,
        params=None,
        body={"instId": "BTC-USDT-SWAP", "sz": "1", "tag": None},
    )
    check(body == {"instId": "BTC-USDT-SWAP", "sz": "1"}, "POST body drops None", str(body))


async def check_uni_client() -> None:
    """Публичные методы UniClient, затронутые фиксами."""
    async with await UniClient.create() as c:
        bba = await c.futures_best_bid_ask()
        one = await c.futures_best_bid_ask("BTC-USDT-SWAP")
        check(len(bba) > 300 and one["b"] < one["a"], "U7 futures_best_bid_ask", f"n={len(bba)}")

        rates = await c.funding_rate()
        check(
            len(rates) > 300 and all(s.endswith("-SWAP") for s in rates),
            "U8 funding_rate() returns all SWAP",
            f"n={len(rates)}",
        )

        info = await c.funding_info()
        nxt = await c.funding_next_time("BTC-USDT-SWAP")
        now = int(time.time() * 1000)
        item = info["BTC-USDT-SWAP"]
        check(
            item["i"] in (1, 2, 4, 8) and now < item["T"] == nxt < now + 9 * 3600_000,
            "funding_info / funding_next_time",
            str(item),
        )

        delistings = await c.futures_delistings()
        check(isinstance(delistings, dict), "futures_delistings", f"n={len(delistings)}")

        spot = (await c.klines("BTC-USDT", Timeframe.MIN_1, limit=5))[-2]
        swap = (await c.futures_klines("BTC-USDT-SWAP", Timeframe.MIN_1, limit=5))[-2]
        for name, k in (("spot", spot), ("swap", swap)):
            ratio = k["q"] / (k["v"] * k["c"]) if k["v"] else 0
            check(0.98 < ratio < 1.02, f"U9 {name} kline v is base volume", f"q/(v*c)={ratio:.4f}")

        start = now - 3 * 3600_000
        ks = await c.klines("BTC-USDT", Timeframe.MIN_1, start_time=start, end_time=start + 600_000)
        check(
            bool(ks) and all(start < k["t"] < start + 600_000 for k in ks),
            "№7 klines start_time/end_time window",
            f"{[(k['t'] - start) // 60000 for k in ks]}",
        )


async def check_client() -> None:
    """Новые публичные эндпоинты клиента."""
    async with await Client.create() as c:
        calls = {
            "get_rpi_order_book": c.get_rpi_order_book("BTC-USDT-SWAP"),
            "get_block_tickers": c.get_block_tickers("SWAP"),
            "get_corporate_actions": c.get_corporate_actions(),
            "get_delta_hedge_currencies": c.get_delta_hedge_currencies(),
            "get_mm_instrument_types": c.get_mm_instrument_types(),
            "get_support_coin": c.get_support_coin(),
            "get_taker_volume": c.get_taker_volume("BTC", "CONTRACTS"),
            "get_contract_open_interest_history": c.get_contract_open_interest_history(
                "BTC-USDT-SWAP"
            ),
            "get_top_trader_long_short_position_ratio": c.get_top_trader_long_short_position_ratio(
                "BTC-USDT-SWAP"
            ),
            "get_put_call_ratio": c.get_put_call_ratio("BTC"),
            "get_event_contract_series": c.get_event_contract_series(),
            "get_exchange_list": c.get_exchange_list(),
            "get_candlesticks(adjust)": c.get_candlesticks("BTC-USDT", bar="1m", limit=2),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                ok = res.get("code") == "0"
                check(ok, name, f"code={res.get('code')} n={len(res.get('data', []))}")
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {e}")


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


async def noop(_msg) -> None:  # noqa: ANN001
    """Пустой callback."""


async def check_ws() -> None:
    """WS без порта 8443: сообщения идут, адаптер не логирует ошибок на notice/subscribe."""
    check(
        ":8443" not in WebsocketManager._BASE_URL,
        "U11 WS URL without :8443",
        WebsocketManager._BASE_URL,
    )
    raw = WebsocketManager()
    uni = UniWebsocketManager()
    ERRORS.clear()
    streams = {
        "uni futures_klines": uni.futures_klines(noop, Timeframe.MIN_1, symbol="BTC-USDT-SWAP"),
        "uni trades": uni.trades(noop, symbol="BTC-USDT"),
        "uni futures_best_bid_ask": uni.futures_best_bid_ask(noop, symbol="BTC-USDT-SWAP"),
        "raw books-rpi": raw.order_book(noop, "books-rpi", "BTC-USDT-SWAP"),
        "raw bbo-rpi-tbt": raw.order_book(noop, "bbo-rpi-tbt", "BTC-USDT-SWAP"),
    }
    counts = await asyncio.gather(*(run_ws(ws) for ws in streams.values()))
    for (name, _), n in zip(streams.items(), counts, strict=True):
        check(n > 0, f"WS {name}", f"{n} msgs")
    adapter_errors = [e for e in ERRORS if "adapting message" in e]
    check(
        not adapter_errors,
        "WS no adapter errors",
        adapter_errors[0][:150] if adapter_errors else "",
    )


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    check_offline()
    await check_uni_client()
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
