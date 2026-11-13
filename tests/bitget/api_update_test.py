"""Проверка обновления Bitget API (2026-11): подпись POST-запросов, новые эндпоинты.

Офлайн: приватные POST подписаны, тело — компактный JSON без None, отправляется та же строка.
Живые проверки — публичные эндпоинты (без ключей).

Запуск: `python tests/bitget/api_update_test.py`
"""

import asyncio
import base64
import hashlib
import hmac
import time
from unittest.mock import patch

from loguru import logger

from unicex.bitget import Client
from unicex.exceptions import NotAuthorized

logger.remove()

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


async def check_signing() -> None:
    """Приватные POST-методы подписаны и шлют тело, а не query."""
    client = Client(session=None, api_key="key", api_secret="secret", api_passphrase="pass")  # type: ignore[arg-type]
    sent: dict = {}

    async def fake_request(self, **kwargs):  # noqa: ANN001, ANN003
        sent.clear()
        sent.update(kwargs)
        return {"code": "00000"}

    def expected(prehash: str) -> str:
        digest = hmac.new(b"secret", prehash.encode(), hashlib.sha256).digest()
        return base64.b64encode(digest).decode()

    with (
        patch("unicex.bitget.client.time.time", return_value=1700000000.123),
        patch("unicex._base.client.BaseClient._make_request", new=fake_request),
    ):
        await client.withdraw(coin="USDT", transfer_type="on_chain", address="addr", size=10)
        body = '{"coin":"USDT","transferType":"on_chain","address":"addr","size":10}'
        check(sent["data"] == body and not sent["params"], "withdraw sends compact body", sent["data"])
        check(
            sent["headers"]["ACCESS-SIGN"]
            == expected(f"1700000000123POST/api/v2/spot/wallet/withdrawal{body}"),
            "withdraw is signed over body",
        )

        calls = {
            "modify_plan_order": client.modify_plan_order(1, 2, "limit", order_id="1"),
            "transfer": client.transfer("spot", "usdt_futures", 1, "USDT", "BTCUSDT"),
            "sub_transfer": client.sub_transfer("spot", "spot", 1, "USDT"),
            "modify_deposit_account": client.modify_deposit_account("spot", "USDT"),
            "futures_change_position_mode": client.futures_change_position_mode("one_way_mode"),
            "cancel_withdrawal": client.cancel_withdrawal("123"),
        }
        for name, coro in calls.items():
            await coro
            ok = bool(sent["data"]) and not sent["params"] and "ACCESS-SIGN" in sent["headers"]
            check(ok and "null" not in sent["data"], f"{name}: signed body", sent["data"])

        await client.get_account_transfer_records("USDT", "spot", limit="10")
        check(
            sent["params"] == {"coin": "USDT", "fromType": "spot", "limit": "10"}
            and sent["data"] is None
            and sent["headers"]["ACCESS-SIGN"]
            == expected(
                "1700000000123GET/api/v2/spot/account/transferRecords"
                "?coin=USDT&fromType=spot&limit=10"
            ),
            "GET signed over sorted query",
            str(sent["params"]),
        )

        await client.futures_interest_rate_history("USDT")
        check(sent["params"] == {"coin": "USDT"}, "futures_interest_rate_history sends coin")


async def check_public() -> None:
    """Новые публичные эндпоинты."""
    async with await Client.create() as c:
        calls = {
            "announcements": c.announcements(),
            "trading_insight_symbols": c.trading_insight_symbols(),
            "fund_flow": c.fund_flow("BTCUSDT"),
            "fund_net_flow": c.fund_net_flow("BTCUSDT"),
            "futures_taker_buy_sell_volume": c.futures_taker_buy_sell_volume("BTCUSDT"),
            "futures_position_long_short_ratio": c.futures_position_long_short_ratio("BTCUSDT"),
            "margin_long_short_ratio": c.margin_long_short_ratio("BTCUSDT"),
            "futures_long_short": c.futures_long_short("BTCUSDT"),
            "margin_loan_growth": c.margin_loan_growth("BTCUSDT"),
            "margin_isolated_borrow_ratio": c.margin_isolated_borrow_ratio("BTCUSDT"),
            "futures_interest_rate_history": c.futures_interest_rate_history("USDT"),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(res.get("code") == "00000", name, str(res.get("data"))[:80])
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")

        try:
            await c.futures_max_open("BTCUSDT", "USDT-FUTURES", "USDT", "long", "market")
            check(False, "futures_max_open requires auth")
        except NotAuthorized:
            check(True, "futures_max_open requires auth")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    await check_signing()
    await check_public()
    failed = [name for ok, name in RESULTS if not ok]
    print(
        f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed in {time.monotonic() - started:.1f}s"
    )
    if failed:
        print("FAILED:", ", ".join(failed))
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
