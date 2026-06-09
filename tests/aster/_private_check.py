"""Ad-hoc проверка приватных методов Aster (read-only + мутирующие, без ордеров).

Проверяет корректность EIP-712 подписи V3 на raw Client и UniClient.
"""

import asyncio
import os

from loguru import logger

from unicex.aster import Client, UniClient
from unicex.enums import MarginType

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
    """Прогоняет приватные методы по очереди."""
    private_key = os.environ.get("ASTER_PRIVATE_KEY")
    if not private_key:
        raise SystemExit("ASTER_PRIVATE_KEY is not set")

    print("=== RAW Client (read-only) ===")
    raw = await Client.create(private_key=private_key)
    print(f"signer: {raw._signer}")
    async with raw:
        await _run("futures_balance", raw.futures_balance())
        await _run("futures_account", raw.futures_account())
        await _run("futures_position_info", raw.futures_position_info(SYMBOL))
        await _run("futures_orders_open", raw.futures_orders_open())
        await _run("futures_commission_rate", raw.futures_commission_rate(SYMBOL))
        await _run("futures_position_mode_get", raw.futures_position_mode_get())

        # listenKey: создаём и тут же закрываем
        await _run("futures_listen_key", raw.futures_listen_key())
        await _run("futures_close_listen_key", raw.futures_close_listen_key())

    print("\n=== UniClient (read-only) ===")
    uni = await UniClient.create(private_key=private_key)
    async with uni:
        await _run("futures_position_info", uni.futures_position_info(SYMBOL))

    print("\n=== Мутирующие (меняют настройки символа) ===")
    raw2 = await Client.create(private_key=private_key)
    async with raw2:
        await _run("futures_leverage_change(5)", raw2.futures_leverage_change(SYMBOL, 5))
        await _run(
            "futures_margin_type_change(ISOLATED)",
            raw2.futures_margin_type_change(SYMBOL, "ISOLATED"),
        )

    uni2 = await UniClient.create(private_key=private_key)
    async with uni2:
        await _run("uni.futures_set_leverage(10)", uni2.futures_set_leverage(SYMBOL, 10))
        await _run(
            "uni.futures_set_margin_type(CROSSED)",
            uni2.futures_set_margin_type(SYMBOL, MarginType.CROSSED),
        )


if __name__ == "__main__":
    asyncio.run(main())
