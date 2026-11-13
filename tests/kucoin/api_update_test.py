"""Проверка обновления KuCoin API (2026-11): UTA V2, свечи U4, новые uni-методы, подпись.

Офлайн: подпись запросов и пассфразы, компактное тело POST.
Живые проверки — публичные эндпоинты (без ключей).

Запуск: `python tests/kucoin/api_update_test.py`
"""

import asyncio
import base64
import hashlib
import hmac
import time
from unittest.mock import AsyncMock, patch

from loguru import logger

from unicex.enums import Timeframe
from unicex.kucoin import Client, UniClient

ERRORS: list[str] = []
logger.remove()
logger.add(lambda m: ERRORS.append(str(m)), level="ERROR")

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


def b64_hmac(secret: str, message: str) -> str:
    """Эталон подписи KuCoin."""
    digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


async def check_signing() -> None:
    """Подпись: timestamp + METHOD + путь с незакодированным query + компактное тело."""
    client = Client(session=None, api_key="key", api_secret="secret", api_passphrase="pass")  # type: ignore[arg-type]
    sent: dict = {}

    async def fake_request(**kwargs):  # noqa: ANN003
        sent.update(kwargs)
        return {"code": "200000"}

    with (
        patch("unicex.kucoin.client.time.time", return_value=1700000000.123),
        patch("unicex._base.client.BaseClient._make_request", AsyncMock(side_effect=fake_request)),
    ):
        await client.order_place(
            trade_type="FUTURES",
            symbol="XBTUSDTM",
            side="BUY",
            order_type="LIMIT",
            size="1",
            size_unit="UNIT",
            price="50000",
        )
        body = sent["data"]
        headers = sent["headers"]
        expected_body = (
            '{"tradeType":"FUTURES","symbol":"XBTUSDTM","side":"BUY","orderType":"LIMIT",'
            '"size":"1","sizeUnit":"UNIT","price":"50000"}'
        )
        check(body == expected_body, "POST body is compact JSON without None", body)
        expected_sign = b64_hmac(
            "secret", "1700000000123POST/api/ua/v2/unified/order/place" + expected_body
        )
        check(headers["KC-API-SIGN"] == expected_sign, "POST signature")
        check(headers["KC-API-PASSPHRASE"] == b64_hmac("secret", "pass"), "passphrase is signed")
        check(headers["KC-API-KEY-VERSION"] == "3", "key version 3")

        await client.deposit_address(currency="USDT", chain="trc20")
        query = "&".join(f"{k}={v}" for k, v in sent["params"].items())
        path = f"/api/ua/v2/asset/deposit/address?{query}"
        check(
            sent["headers"]["KC-API-SIGN"] == b64_hmac("secret", "1700000000123GET" + path),
            "GET signature includes raw query",
            str(sent["params"]),
        )


async def check_uni() -> None:
    """Публичные методы UniClient."""
    now = int(time.time() * 1000)
    async with await UniClient.create() as c:
        for name, klines in (
            ("spot", await c.klines("BTC-USDT", Timeframe.MIN_1, limit=5)),
            ("futures", await c.futures_klines("XBTUSDTM", Timeframe.MIN_1, limit=5)),
        ):
            k = klines[-2]
            ratio = k["q"] / (k["v"] * k["c"]) if k["v"] else 0
            ok = (
                now - 10 * 60_000 < k["t"] < now
                and k["l"] <= min(k["o"], k["c"]) <= max(k["o"], k["c"]) <= k["h"]
                and 0.98 < ratio < 1.02
            )
            check(ok, f"U4 {name} klines (ms, OHLC order, base volume)", f"{k}")

        rates = await c.funding_rate()
        one = await c.funding_rate("XBTUSDTM")
        check(
            len(rates) > 300 and abs(one) < 1, "funding_rate() all and by symbol", f"n={len(rates)}"
        )
        info = await c.funding_info("XBTUSDTM")
        interval = await c.funding_interval("XBTUSDTM")
        next_time = await c.funding_next_time("XBTUSDTM")
        check(
            info["i"] == interval in (1, 2, 4, 8) and now < info["T"] == next_time,
            "funding_info / interval / next_time",
            str(info),
        )

        oi = await c.open_interest("XBTUSDTM")
        check(1_000 < oi["v"] < 10_000_000 and oi["t"] < 10**13, "open_interest in coins", str(oi))

        bba = await c.futures_best_bid_ask()
        one_bba = await c.futures_best_bid_ask("XBTUSDTM")
        check(
            len(bba) > 300 and one_bba["b"] < one_bba["a"] and one_bba["t"] < 10**13,
            "futures_best_bid_ask",
            str(one_bba),
        )

        depth = await c.futures_depth("XBTUSDTM", 20)
        check(
            len(depth["b"]) == 20 and depth["b"][0][0] < depth["a"][0][0] and depth["t"] < 10**13,
            "futures_depth",
            f"bid={depth['b'][0]} ask={depth['a'][0]}",
        )

        delistings = await c.futures_delistings()
        check(isinstance(delistings, dict), "futures_delistings", f"n={len(delistings)}")


async def check_client() -> None:
    """Новые публичные эндпоинты клиента."""
    async with await Client.create() as c:
        calls = {
            "trades": c.trades("FUTURES", "XBTUSDTM"),
            "index_price": c.index_price("XBTUSDTM"),
            "currency": c.currency("BTC"),
            "currencies": c.currencies(),
            "trade_statistics": c.trade_statistics(),
            "server_status": c.server_status("SPOT"),
            "announcements": c.announcements(),
            "kline(klineType)": c.kline("FUTURES", "XBTUSDTM", "1min", kline_type="MARK_PRICE"),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(res.get("code") == "200000", name, str(res)[:100])
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    await check_signing()
    await check_uni()
    await check_client()
    adapter_errors = [e for e in ERRORS if "error" in e.lower()]
    check(
        not adapter_errors,
        "no adapter errors logged",
        adapter_errors[0][:200] if adapter_errors else "",
    )
    failed = [name for ok, name in RESULTS if not ok]
    print(
        f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed in {time.monotonic() - started:.1f}s"
    )
    if failed:
        print("FAILED:", ", ".join(failed))
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
