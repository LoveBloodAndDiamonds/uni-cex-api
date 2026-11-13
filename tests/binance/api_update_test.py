"""Проверка обновления Binance API (2026-11): подпись, новые эндпоинты, WS-маршрутизация.

Офлайн: подпись REST и WebSocket API сверяется с примерами из официальной документации.
Живые проверки (без ключей): публичные эндпоинты, стримы и подписка WS API с фейковым ключом.

Запуск: `python tests/binance/api_update_test.py`
"""

import asyncio
import time
from unittest.mock import patch

import orjson
import websockets
from loguru import logger

from unicex.binance import Client, UniClient, WebsocketManager
from unicex.binance.user_websocket import _SpotUserDataWebsocket
from unicex.exceptions import NotSupported, ResponseError

logger.remove()

# Ключи из примеров документации Binance (не настоящие)
DOC_API_KEY = "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
DOC_SECRET = "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"

RESULTS: list[tuple[bool, str]] = []


def check(ok: bool, name: str, details: str = "") -> None:
    """Запоминает и печатает результат проверки."""
    RESULTS.append((ok, name))
    print(f"{'✅' if ok else '❌'} {name}" + (f" — {details}" if details else ""))


async def check_rest_signature() -> None:
    """Подпись REST совпадает с примерами docs (ASCII и non-ASCII символ)."""
    client = await Client.create(api_key=DOC_API_KEY, api_secret=DOC_SECRET)
    async with client:
        with patch("unicex.binance.client.time.time", return_value=1499827319.559):
            for symbol, expected in (
                ("LTCBTC", "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71"),
                (
                    "１２３４５６",
                    "e1353ec6b14d888f1164ae9af8228a3dbd508bc82eb867db8ab6046442f33ef3",
                ),
            ):
                params = {
                    "symbol": symbol,
                    "side": "BUY",
                    "type": "LIMIT",
                    "timeInForce": "GTC",
                    "quantity": 1,
                    "price": 0.1,
                }
                query = client._sign_query(client._normalize_params(params))
                signature = query.rsplit("signature=", 1)[1]
                check(signature == expected, f"REST signature ({symbol})", signature[:16])

        normalized = client._normalize_params({"symbols": ["BTCUSDT", "ETHUSDT"], "flag": True})
        check(
            normalized == {"symbols": '["BTCUSDT","ETHUSDT"]', "flag": "true"},
            "list/bool params are normalized",
            str(normalized),
        )


def check_ws_api_signature() -> None:
    """Подпись WebSocket API совпадает с примером docs; фильтр подписывается без пробелов."""
    ws = _SpotUserDataWebsocket(
        callback=None,  # type: ignore[arg-type]
        url="",
        api_key=DOC_API_KEY,
        api_secret=DOC_SECRET,
        recv_window=100,
    )
    with patch("unicex.binance.user_websocket.time.time", return_value=1645423376.532):
        msg = orjson.loads(ws._subscribe_message())
    check(
        msg["method"] == "userDataStream.subscribe.signature"
        and set(msg["params"]) == {"apiKey", "recvWindow", "timestamp", "signature"},
        "WS API subscribe message shape",
    )

    from unicex.utils import generate_hmac_sha256_signature

    ws_filter = _SpotUserDataWebsocket(
        callback=None,  # type: ignore[arg-type]
        url="",
        api_key=DOC_API_KEY,
        api_secret=DOC_SECRET,
        event_filter={"x": ["TRADE"], "e": ["executionReport"], "s": ["BAZUSD"]},
    )
    with patch("unicex.binance.user_websocket.time.time", return_value=1645423376.532):
        msg = orjson.loads(ws_filter._subscribe_message())
    expected_payload = (
        f"apiKey={DOC_API_KEY}"
        '&filter={"e":["executionReport"],"s":["BAZUSD"],"x":["TRADE"]}'
        "&recvWindow=5000&timestamp=1645423376532"
    )
    expected = generate_hmac_sha256_signature(DOC_SECRET, expected_payload, "hex")
    check(msg["params"]["signature"] == expected, "WS API signature with sorted filter")


async def check_ws_api_live() -> None:
    """Сервер принимает формат подписки и отвечает ошибкой ключа (а не формата)."""
    ws = _SpotUserDataWebsocket(
        callback=None,  # type: ignore[arg-type]
        url="",
        api_key="x" * 64,
        api_secret="y" * 64,
    )
    async with websockets.connect("wss://ws-api.binance.com:443/ws-api/v3") as conn:
        await conn.send(ws._subscribe_message())
        response = orjson.loads(await asyncio.wait_for(conn.recv(), 10))
    code = response.get("error", {}).get("code")
    check(code in (-2014, -2015, -1022), "WS API rejects only the fake key", str(response)[:120])


async def check_rest_live() -> None:
    """Публичные эндпоинты: старые с новыми параметрами и новые."""
    async with await Client.create() as client:
        prices = await client.ticker_price(symbols=["BTCUSDT", "ETHUSDT"])
        check(len(prices) == 2, "ticker_price(symbols=[...]) sends JSON list", str(len(prices)))

        all_prices = await client.ticker_price()
        trading = await client.ticker_price(symbol_status="TRADING")
        zero = [p for p in trading if float(p["price"]) <= 0]
        check(
            len(trading) < len(all_prices) and not zero,
            "ticker_price(symbol_status='TRADING') drops delisted",
            f"{len(all_prices)} → {len(trading)}, zero prices: {len(zero)}",
        )

        calls = {
            "exchange_info(symbols=...)": client.exchange_info(symbols=["BTCUSDT"]),
            "execution_rules": client.execution_rules(symbol="BTCUSDT"),
            "reference_price": client.reference_price("BTCUSDT"),
            "reference_price_calculation": client.reference_price_calculation("BTCUSDT"),
            "futures_rpi_depth": client.futures_rpi_depth("BTCUSDT"),
            "futures_continuous_klines": client.futures_continuous_klines(
                "BTCUSDT", "PERPETUAL", "1m", limit=3
            ),
            "futures_index_price_klines": client.futures_index_price_klines(
                "BTCUSDT", "1m", limit=3
            ),
            "futures_mark_price_klines": client.futures_mark_price_klines("BTCUSDT", "1m", limit=3),
            "futures_premium_index_klines": client.futures_premium_index_klines(
                "BTCUSDT", "1m", limit=3
            ),
            "futures_adl_risk": client.futures_adl_risk("BTCUSDT"),
            "futures_trading_schedule": client.futures_trading_schedule(),
            "futures_index_constituents": client.futures_index_constituents("BTCUSDT"),
            "futures_asset_index": client.futures_asset_index(),
            "futures_insurance_balance": client.futures_insurance_balance("BTCUSDT"),
            "futures_basis": client.futures_basis("BTCUSDT", "PERPETUAL", "5m", limit=3),
            "futures_delivery_price": client.futures_delivery_price("BTCUSDT"),
            "futures_convert_exchange_info": client.futures_convert_exchange_info(
                from_asset="USDT"
            ),
        }
        for name, coro in calls.items():
            try:
                res = await coro
                check(bool(res), name, f"{type(res).__name__} len={len(res)}")
            except ResponseError as e:
                check(False, name, f"{e.status_code} {e.code}")

        try:
            await client.futures_algo_orders_open()
            check(False, "futures_algo_orders_open requires auth")
        except Exception as e:
            check(type(e).__name__ == "NotAuthorized", "futures_algo_orders_open requires auth")

    async with await UniClient.create() as uni:
        last = await uni.last_price()
        zero = [s for s, p in last.items() if p <= 0]
        check(not zero, "UniClient.last_price has no zero prices", f"n={len(last)}")


async def count_messages(ws, seconds: float = 6) -> int:
    """Запускает вебсокет на `seconds` секунд и считает сообщения."""
    counter = {"n": 0}
    original = ws._callback

    async def callback(msg):  # noqa: ANN001
        counter["n"] += 1
        if original:
            await original(msg)

    ws._callback = callback
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


async def check_ws_live() -> None:
    """Стримы: futures @trade на /public, мультиплекс спота, новые стримы."""
    manager = WebsocketManager()
    streams = {
        "futures_trade (/public)": manager.futures_trade(noop, symbol="BTCUSDT"),
        "multiplex_socket": manager.multiplex_socket(noop, "btcusdt@trade/ethusdt@trade"),
        "reference_price": manager.reference_price(noop, symbol="BTCUSDT"),
        "futures_rpi_diff_depth": manager.futures_rpi_diff_depth(noop, symbol="BTCUSDT"),
        "futures_trading_session": manager.futures_trading_session(noop),
        "rolling_window_ticker(1h)": manager.rolling_window_ticker(noop, window="1h"),
    }
    counts = await asyncio.gather(*(count_messages(ws) for ws in streams.values()))
    for (name, _), n in zip(streams.items(), counts, strict=True):
        check(n > 0, f"WS {name}", f"{n} msgs")

    try:
        manager.ticker(noop)
        check(False, "WS ticker() raises NotSupported")
    except NotSupported:
        check(True, "WS ticker() raises NotSupported")


async def main() -> None:
    """Запускает все проверки."""
    started = time.monotonic()
    await check_rest_signature()
    check_ws_api_signature()
    await check_ws_api_live()
    await check_rest_live()
    await check_ws_live()
    failed = [name for ok, name in RESULTS if not ok]
    print(
        f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed in {time.monotonic() - started:.1f}s"
    )
    if failed:
        print("FAILED:", ", ".join(failed))
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
