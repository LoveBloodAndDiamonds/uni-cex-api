"""Проверка обновления Aster API (2026-11): nonceWindow, guarded-отмена, withdraw, новые эндпоинты.

Офлайн: состав и подпись query string приватных запросов.
Живые проверки — публичные эндпоинты; приватные — случайным кошельком (ожидается "No agent found").

Запуск: `python tests/aster/api_update_test.py`
"""

import asyncio
import time
import urllib.parse
from unittest.mock import patch

from eth_account import Account
from eth_account.messages import encode_typed_data
from loguru import logger

from unicex.aster import Client, UniClient
from unicex.exceptions import ResponseError

logger.remove()

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


def recover_signer(query: str) -> str:
    """Восстанавливает адрес подписавшего по query string Aster V3."""
    msg, signature = query.rsplit("&signature=", 1)
    typed = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Message": [{"name": "msg", "type": "string"}],
        },
        "primaryType": "Message",
        "domain": {
            "name": "AsterSignTransaction",
            "version": "1",
            "chainId": 1666,
            "verifyingContract": "0x0000000000000000000000000000000000000000",
        },
        "message": {"msg": msg},
    }
    return Account.recover_message(encode_typed_data(full_message=typed), signature=signature)


async def check_signing() -> None:
    """NonceWindow только в изменяющих запросах и под подписью; явный nonce; userNonce."""
    wallet = Account.create()
    client = Client(session=None, private_key=wallet.key, nonce_window=5000)  # type: ignore[arg-type]
    sent: dict = {}

    async def fake_request(self, **kwargs):  # noqa: ANN001, ANN003
        sent.clear()
        sent.update(kwargs)
        return {}

    def query() -> dict[str, str]:
        return dict(urllib.parse.parse_qsl(sent["url"].split("?", 1)[1]))

    with patch("unicex._base.client.BaseClient._make_request", new=fake_request):
        await client.futures_noop()
        q = sent["url"].split("?", 1)[1]
        check(query().get("nonceWindow") == "5000", "POST has nonceWindow", q[:60])
        check(recover_signer(q) == wallet.address, "nonceWindow is covered by signature")
        check(int(query()["nonce"]) == client.last_nonce, "last_nonce matches sent nonce")

        await client.futures_stp_mode()
        check("nonceWindow" not in query(), "GET has no nonceWindow")

        await client.futures_order_create("BTCUSDT", "BUY", "LIMIT", quantity=1, price=1)
        order_nonce = client.last_nonce
        await client.futures_guarded_order_cancel("BTCUSDT", order_nonce, order_id=1)
        check(
            query()["nonce"] == str(order_nonce)
            and recover_signer(sent["url"].split("?", 1)[1]) == wallet.address,
            "guarded cancel signed with order nonce",
        )

        await client.withdraw("56", "USDT", 10, 1, wallet.address, "123", "0xsig")
        q = query()
        check(
            q["userNonce"] == "123" and q["nonce"] != "123",
            "withdraw: userNonce separate from signing nonce",
            str({k: q[k] for k in ("userNonce", "nonce")}),
        )

        await client.futures_strategy_order_create("OTOCO", [{"symbol": "BTCUSDT"}])
        check(query()["subOrderList"] == '[{"symbol":"BTCUSDT"}]', "subOrderList is compact JSON")

        await client.futures_leverage_brackets("BTCUSDT")
        check("/fapi/v3/leverageBrackets?" in sent["url"], "leverageBrackets (plural)")

    try:
        client._validate_response(200, "", {"code": -5050, "msg": "DEPOSIT_REQUIRED"})
        check(False, "-5050 with HTTP 200 raises")
    except ResponseError as e:
        check(e.code == "-5050", "-5050 with HTTP 200 raises")
    client._validate_response(200, "", {"code": "200", "msg": "done"})
    check(True, "success code '200' does not raise")


async def check_public() -> None:
    """Новые публичные эндпоинты и подпись на живом сервере."""
    async with await Client.create() as c:
        calls = {
            "futures_index_references": c.futures_index_references("BTCUSDT"),
            "futures_remaining_openable_notional": c.futures_remaining_openable_notional(
                "BTCUSDT", 10
            ),
            "futures_asset_logos": c.futures_asset_logos(),
            "futures_funding_info(symbol)": c.futures_funding_info("BTCUSDT"),
            "ticker_opt_24hr": c.ticker_opt_24hr(),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(bool(res), name, str(res)[:80])
            except Exception as e:
                check(False, name, f"{type(e).__name__}: {str(e)[:150]}")

        info = await c.futures_funding_info("BTCUSDT")
        check(len(info) == 1 and info[0]["symbol"] == "BTCUSDT", "funding_info filters by symbol")

    async with await Client.create(private_key=Account.create().key, nonce_window=5000) as c:
        try:
            await c.futures_noop()
            check(False, "signed POST with nonceWindow reaches auth check")
        except ResponseError as e:
            check(
                e.code == "-1000" and "agent" in str(e.response_json),
                "signed POST with nonceWindow reaches auth check",
                str(e.response_json),
            )

    async with await UniClient.create() as u, await Client.create() as c:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT"]
        oi, *official = await asyncio.gather(
            u.open_interest(),
            *(
                c._make_request(
                    "GET", c._BASE_FUTURES_URL + "/fapi/v1/openInterest", params={"symbol": s}
                )
                for s in symbols
            ),
        )
        ratios = [
            oi[s]["v"] / float(o["openInterest"]) for s, o in zip(symbols, official, strict=True)
        ]
        check(
            all(0.97 < r < 1.03 for r in ratios),
            "open_interest matches /fapi/v1/openInterest",
            str([round(r, 4) for r in ratios]),
        )

        delistings = await u.futures_delistings()
        now = int(time.time() * 1000)
        check(
            all(t > now for t in delistings.values()),
            "futures_delistings only future",
            str(delistings),
        )


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
