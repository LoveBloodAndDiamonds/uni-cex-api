"""Ad-hoc проверка спотовых приватных методов Aster (read-only) + публичного спот-WS.

Проверяет EIP-712 подпись V3 на спотовом хосте (sapi.asterdex.com) и спот-вебсокет
(sstream.asterdex.com). Ордера здесь не размещаются.
"""

import asyncio
import os

from loguru import logger

from unicex.aster import Client, UniWebsocketManager

logger.remove()

SYMBOL = "BTCUSDT"


def _short(value: object, limit: int = 220) -> str:
    """Укорачивает представление значения для компактного вывода."""
    text = repr(value)
    return text if len(text) <= limit else f"{text[:limit]}... (len={len(text)})"


async def _run(name: str, coro) -> None:
    """Выполняет один вызов и печатает результат или ошибку."""
    try:
        result = await coro
        print(f"[OK]   {name}: {_short(result)}")
    except Exception as exc:  # noqa: BLE001 - в тесте ловим всё, чтобы пройти весь список
        print(f"[FAIL] {name}: {type(exc).__name__}: {exc}")


async def main() -> None:
    """Прогоняет спотовые приватные read-only методы и публичный спот-WS."""
    private_key = os.environ.get("ASTER_PRIVATE_KEY")
    if not private_key:
        raise SystemExit("ASTER_PRIVATE_KEY is not set")

    print("=== RAW Client (spot, read-only) ===")
    raw = await Client.create(private_key=private_key)
    print(f"signer: {raw._signer}")
    async with raw:
        await _run("account", raw.account())
        await _run("commission_rate", raw.commission_rate(SYMBOL))
        await _run("orders_open", raw.orders_open())

        # listenKey: создаём и тут же закрываем
        await _run("listen_key", raw.listen_key())
        await _run("close_listen_key", raw.close_listen_key())

    print("\n=== Spot public WS (trade + kline) ===")
    counters = {"trade": 0, "kline": 0}

    async def on_trade(msg) -> None:
        counters["trade"] += 1
        if counters["trade"] == 1:
            print(f"[OK]   ws trade: {_short(msg)}")

    async def on_kline(msg) -> None:
        counters["kline"] += 1
        if counters["kline"] == 1:
            print(f"[OK]   ws kline: {_short(msg)}")

    from unicex.enums import Timeframe

    manager = UniWebsocketManager()
    trade_ws = manager.trades(callback=on_trade, symbol=SYMBOL)
    kline_ws = manager.klines(callback=on_kline, timeframe=Timeframe.MIN_1, symbol=SYMBOL)
    await trade_ws.start()
    await kline_ws.start()

    # Ждём несколько сообщений, затем останавливаем.
    for _ in range(15):
        if counters["trade"] and counters["kline"]:
            break
        await asyncio.sleep(1)

    await trade_ws.stop()
    await kline_ws.stop()
    print(f"counters: {counters}")


if __name__ == "__main__":
    asyncio.run(main())
