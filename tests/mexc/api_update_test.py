"""Проверка обновления MEXC API (2026-11): домен фьючерсов, подпись futures, WS (U6, U10).

Офлайн: подпись приватных фьючерсных запросов (схема ApiKey + Request-Time + Signature).
Живые проверки — публичные эндпоинты и стримы (без ключей).

Запуск: `python tests/mexc/api_update_test.py`
"""

import asyncio
import hashlib
import hmac
import json
import time
from unittest.mock import patch

from loguru import logger

from unicex.enums import Timeframe
from unicex.mexc import Client, UniClient, UniWebsocketManager, WebsocketManager

ERRORS: list[str] = []
logger.remove()
logger.add(lambda m: ERRORS.append(str(m)), level="ERROR")

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


async def check_futures_signing() -> None:
    """GET: отсортированная query string; POST: компактное JSON-тело; подпись hex."""
    client = Client(session=None, api_key="key", api_secret="secret")  # type: ignore[arg-type]
    sent: dict = {}

    async def fake_request(self, **kwargs):  # noqa: ANN001, ANN003
        sent.clear()
        sent.update(kwargs)
        return {"success": True}

    def expected(payload: str) -> str:
        return hmac.new(
            b"secret", f"key1700000000123{payload}".encode(), hashlib.sha256
        ).hexdigest()

    with (
        patch("unicex.mexc.client.time.time", return_value=1700000000.123),
        patch("unicex._base.client.BaseClient._make_request", new=fake_request),
    ):
        await client.futures_orders_history(symbol="BTC_USDT", page_size=10, page_num=1)
        check(
            sent["headers"]["Signature"] == expected("page_num=1&page_size=10&symbol=BTC_USDT"),
            "GET signature over sorted query",
            str(sent["params"]),
        )
        check(
            sent["url"].startswith("https://api.mexc.com/"),
            "futures domain api.mexc.com",
            sent["url"],
        )

        await client.futures_order_create(
            "BTC_USDT", vol=1, side=1, type=5, open_type=2, leverage=10
        )
        body = sent["data"]
        check(
            body == '{"symbol":"BTC_USDT","vol":1,"leverage":10,"side":1,"type":5,"openType":2}',
            "POST body is compact JSON without None",
            body,
        )
        check(sent["headers"]["Signature"] == expected(body), "POST signature over body")

        await client.futures_order_cancel([1, 2])
        check(sent["data"] == "[1,2]", "cancel sends id list", sent["data"])


async def check_uni() -> None:
    """Публичные методы UniClient."""
    now = int(time.time() * 1000)
    async with await UniClient.create() as c:
        info = await c.funding_info("BTC_USDT")
        interval = await c.funding_interval("BTC_USDT")
        nxt = await c.funding_next_time("BTC_USDT")
        all_info = await c.funding_info()
        check(
            info["i"] == interval in (1, 2, 4, 8)
            and now < info["T"] == nxt
            and len(all_info) > 300,
            "funding_info / interval / next_time",
            f"{info}, n={len(all_info)}",
        )

        depth = await c.futures_depth("BTC_USDT", 20)
        check(
            len(depth["b"]) == 20
            and depth["b"][0][0] < depth["a"][0][0]
            and depth["b"][0][1] < 1_000,
            "futures_depth in coins",
            f"bid={depth['b'][0]} ask={depth['a'][0]}",
        )

        for name, prices in (
            ("last_price", await c.last_price()),
            ("futures_last_price", await c.futures_last_price()),
        ):
            zero = [s for s, p in prices.items() if p <= 0]
            check(not zero, f"{name} without zero prices", f"n={len(prices)}")

    async with await Client.create() as c:
        offline = await c.symbol_offline()
        check(bool(offline.get("data")), "symbol_offline", f"n={len(offline.get('data', []))}")
        announcements = await c.announcements(limit=10)
        check(bool(announcements.get("data")), "announcements", str(announcements)[:100])


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
    """U6: reduce=false в подписке; U10: t сделок — int; без ошибок адаптера."""
    message = WebsocketManager()._generate_futures_subscription_message(
        topic="sub.deal", symbol="BTC_USDT", reduce=False
    )[0]
    check(json.loads(message)["param"]["reduce"] is False, "U6 sub.deal has reduce=false", message)

    received: dict[str, list] = {"trades": [], "futures_trades": [], "futures_klines": []}

    def collector(key: str):  # noqa: ANN202
        async def cb(item) -> None:  # noqa: ANN001
            received[key].append(item)

        return cb

    uni = UniWebsocketManager()
    ERRORS.clear()
    await asyncio.gather(
        run_ws(uni.trades(collector("trades"), symbol="BTCUSDT")),
        run_ws(uni.futures_trades(collector("futures_trades"), symbol="BTC_USDT")),
        run_ws(uni.futures_klines(collector("futures_klines"), Timeframe.MIN_1, symbol="BTC_USDT")),
    )
    for key, items in received.items():
        ok = bool(items) and all(isinstance(i["t"], int) for i in items)
        check(
            ok, f"WS uni {key} (t is int)", f"n={len(items)} sample={items[0] if items else None}"
        )
    adapter_errors = [e for e in ERRORS if "adapting" in e]
    check(
        not adapter_errors,
        "WS no adapter errors",
        adapter_errors[0][:150] if adapter_errors else "",
    )


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    await check_futures_signing()
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
