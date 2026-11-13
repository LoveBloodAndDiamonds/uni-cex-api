"""Проверка обновления Hyperliquid API (2026-11): webData3, isDelisted, HIP-4, новые действия.

Офлайн: формат новых действий `/exchange` и распаковка `fastAssetCtxs`.
Живые проверки — публичные info-запросы, uni-методы и WS-каналы.

Запуск: `python tests/hyperliquid/api_update_test.py`
"""

import asyncio
import time
import warnings
from unittest.mock import patch

from eth_account import Account
from loguru import logger

from unicex.hyperliquid import Client, UniClient, WebsocketManager

logger.remove()

RESULTS: list[tuple[bool, str]] = []
ZERO = "0x0000000000000000000000000000000000000000"


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


async def check_actions() -> None:
    """Новые действия подписываются и собираются в формате документации."""
    client = Client(session=None, private_key=Account.create().key)  # type: ignore[arg-type]
    sent: list[dict] = []

    async def fake_post(endpoint: str, data: dict) -> dict:
        sent.append(data)
        return {"status": "ok"}

    with patch.object(client, "_post_request", new=fake_post):
        order = {"tif": "Gtc"}
        await client.modify_order(1, 0, True, 100, 0.1, False, "limit", order)
        await client.modify_order(1, 0, True, 100, 0.1, False, "limit", order, always_place=True)
        plain, forced = sent[-2]["action"], sent[-1]["action"]
        check(
            plain["type"] == "modify" and "a" not in plain and forced["a"] is True,
            "modify: a only when always_place",
            str(plain),
        )
        check(
            plain["order"]
            == {"a": 0, "b": True, "p": "100", "s": "0.1", "r": False, "t": {"limit": order}},
            "modify: order payload",
        )
        check({"r", "s", "v"} <= sent[-1]["signature"].keys(), "modify: signed")

        await client.place_trailing_stop_order(0, False, 1, True, retracement_pct="1.5%")
        action = sent[-1]["action"]
        check(
            list(action)
            == ["type", "asset", "isBuy", "sz", "reduceOnly", "retracement", "activationPx"]
            and action["retracement"] == {"pct": "1.5%"},
            "trailingStop action",
            str(action),
        )
        try:
            await client.place_trailing_stop_order(0, False, 1, True)
            check(False, "trailingStop requires retracement")
        except ValueError:
            check(True, "trailingStop requires retracement")

        await client.agent_send_asset(ZERO, "", "spot", "USDC", 1, nonce=123)
        action = sent[-1]["action"]
        check(
            action["type"] == "agentSendAsset" and action["nonce"] == sent[-1]["nonce"] == 123,
            "agentSendAsset nonce matches",
        )

        await client.user_set_abstraction("Mainnet", "unifiedAccount", user=ZERO)
        action = sent[-1]["action"]
        check(
            action["signatureChainId"] == "0x66eee" and action["hyperliquidChain"] == "Mainnet",
            "userSetAbstraction user-signed",
            str(action),
        )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        WebsocketManager().web_data2(noop, ZERO)
    check(any(w.category is DeprecationWarning for w in caught), "WS web_data2 deprecated")


async def check_fast_asset_ctxs_decoding() -> None:
    """Пример из документации распаковывается в словарь."""
    received: list = []

    async def cb(msg) -> None:  # noqa: ANN001
        received.append(msg)

    ws = WebsocketManager().fast_asset_ctxs(cb)
    payload = "q1ZyCnFWsqpWyk0syg6oULJSsjQ3NTDQM1Wq1VFyDfFAkTI2MzXQMwJLVVRWWfmFuTiiyBuamOoZKdXWAgA="
    await ws._callback({"channel": "fastAssetCtxs", "data": payload})
    check(
        received[0]["data"]["xyz:NVDA"] == {"markPx": "145.2"},
        "fastAssetCtxs decoded",
        str(received[0]["data"]),
    )


async def check_public() -> None:
    """Новые info-запросы и uni-методы."""
    now = int(time.time() * 1000)
    async with await Client.create() as c:
        calls = {
            "all_perp_metas": c.all_perp_metas(),
            "perp_dex_status": c.perp_dex_status(),
            "perp_annotation": c.perp_annotation("flx:BTC"),
            "perp_categories": c.perp_categories(),
            "perp_concise_annotations": c.perp_concise_annotations(),
            "outcome_meta": c.outcome_meta(),
            "outcome_templates": c.outcome_templates(),
            "web_data3": c.web_data3(ZERO),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(res is not None, name, str(res)[:80])
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")

        meta = await c.perp_metadata()
        delisted = {x["name"] for x in meta["universe"] if x.get("isDelisted")}

    async with await UniClient.create() as u:
        tickers = await u.futures_tickers()
        check(bool(tickers) and not delisted & set(tickers), "futures_tickers without delisted")

        prices = await u.futures_last_price()
        bad = [s for s in prices if s.startswith(("@", "#")) or "/" in s or s in delisted]
        check(
            not bad and len(prices) == len(tickers),
            "futures_last_price only active perps",
            f"bad={bad[:3]}",
        )

        spot = await u.last_price(resolve_symbols=False)
        check(
            "PURR/USDC" in spot and not any(s.startswith("#") for s in spot),
            "last_price: PURR/USDC, no outcomes",
        )

        info = await u.funding_info("BTC")
        nxt = await u.funding_next_time("BTC")
        check(
            info["i"] == 1 and now < info["T"] == nxt <= now + 3_600_000,
            "funding_info / next_time",
            str(info),
        )
        check(await u.funding_interval("ETH") == 1, "funding_interval")

        rates = await u.funding_rate()
        check(not delisted & set(rates), "funding_rate without delisted")

        depth = await u.futures_depth("BTC", 10)
        check(
            len(depth["b"]) == 10 and depth["b"][0][0] < depth["a"][0][0],
            "futures_depth",
            f"bid={depth['b'][0]} ask={depth['a'][0]}",
        )

        try:
            await u.futures_delistings()
            check(False, "futures_delistings NotImplementedError")
        except NotImplementedError:
            check(True, "futures_delistings NotImplementedError")


async def noop(_msg) -> None:  # noqa: ANN001
    """Пустой callback."""


async def count_messages(ws, seconds: float = 6) -> int:
    """Запускает вебсокет и считает сообщения с данными (без ответа на подписку)."""
    counter = {"n": 0}
    original = ws._callback

    async def cb(msg) -> None:  # noqa: ANN001
        if msg.get("channel") not in ("subscriptionResponse", "pong"):
            await original(msg)
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


async def check_ws() -> None:
    """Новые WS-каналы."""
    decoded: list = []

    async def fast_cb(msg) -> None:  # noqa: ANN001
        decoded.append(isinstance(msg.get("data"), dict))

    m = WebsocketManager()
    streams = {
        "web_data3": m.web_data3(noop, ZERO),
        "clearinghouse_state": m.clearinghouse_state(noop, ZERO),
        "open_orders": m.open_orders(noop, ZERO),
        "spot_state": m.spot_state(noop, ZERO),
        "all_dexs_clearinghouse_state": m.all_dexs_clearinghouse_state(noop, ZERO),
        "all_dexs_asset_ctxs": m.all_dexs_asset_ctxs(noop),
        "fast_asset_ctxs": m.fast_asset_ctxs(fast_cb),
    }
    counts = await asyncio.gather(*(count_messages(ws) for ws in streams.values()))
    for (name, _), n in zip(streams.items(), counts, strict=True):
        check(n > 0, f"WS {name}", f"{n} msgs")
    check(bool(decoded) and all(decoded), "WS fast_asset_ctxs data is dict")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    await check_actions()
    await check_fast_asset_ctxs_decoding()
    await check_public()
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
