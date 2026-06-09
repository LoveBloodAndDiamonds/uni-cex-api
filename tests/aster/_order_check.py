"""Ad-hoc проверка размещения/отмены ордеров Aster (raw Client + UniClient).

Запускать ПОСЛЕ зачисления депозита. Размещает лимитный ордер далеко от рынка
(чтобы он не исполнился), проверяет его и отменяет.
"""

import asyncio
import math
import os

from loguru import logger

from unicex.aster import Client, ExchangeInfo, UniClient
from unicex.enums import OrderSide, OrderType

logger.remove()

SYMBOL = "BTCUSDT"
NOTIONAL_USDT = 6.0  # целевой нотионал ордера (минимум на Aster обычно ~5 USDT)
PRICE_FACTOR = 0.5  # лимит-цена = 50% от рынка -> ордер висит, не исполняется


def _short(value: object, limit: int = 260) -> str:
    """Укорачивает представление значения для компактного вывода."""
    text = repr(value)
    return text if len(text) <= limit else f"{text[:limit]}... (len={len(text)})"


async def _resting_price_qty(raw: Client) -> tuple[str, str]:
    """Считает лимит-цену (ниже рынка) и количество под целевой нотионал, округляя по фильтрам."""
    book = await raw.futures_ticker_book_ticker(SYMBOL)
    market_price = float(book["bidPrice"])  # текущий бид
    raw_price = market_price * PRICE_FACTOR
    price = ExchangeInfo.round_futures_price(SYMBOL, raw_price)

    # Количество: округляем вверх до целого числа шагов лота, минимум один шаг,
    # чтобы покрыть целевой нотионал и не получить qty=0 на дорогих символах.
    size_step = ExchangeInfo.get_futures_ticker_info(SYMBOL)["size_step"]
    steps = max(1, math.ceil(NOTIONAL_USDT / float(price) / size_step))
    qty = ExchangeInfo.round_futures_quantity(SYMBOL, steps * size_step)
    return price, qty


async def main() -> None:
    """Проверяет размещение/отмену ордера через raw Client и UniClient."""
    private_key = os.environ.get("ASTER_PRIVATE_KEY")
    if not private_key:
        raise SystemExit("ASTER_PRIVATE_KEY is not set")

    # Нужны фильтры символа для корректного округления цены/количества.
    await ExchangeInfo.load_exchange_info()

    # --- RAW Client ---
    print("=== RAW Client ===")
    raw = await Client.create(private_key=private_key)
    async with raw:
        price, qty = await _resting_price_qty(raw)
        print(f"price={price} qty={qty}")

        order = await raw.futures_order_create(
            symbol=SYMBOL,
            side="BUY",
            type="LIMIT",
            time_in_force="GTC",
            quantity=qty,
            price=price,
        )
        print(f"[OK]   create: {_short(order)}")

        order_id = order["orderId"]
        try:
            got = await raw.futures_order_get(SYMBOL, order_id=order_id)
            print(f"[OK]   get: {_short(got)}")

            canceled = await raw.futures_order_cancel(SYMBOL, order_id=order_id)
            print(f"[OK]   cancel: {_short(canceled)}")
        except Exception as exc:  # noqa: BLE001
            print(f"[FAIL] get/cancel: {type(exc).__name__}: {exc}")
            # На всякий случай чистим все открытые ордера символа.
            await raw.futures_orders_cancel_all(SYMBOL)

    # --- UniClient ---
    print("\n=== UniClient ===")
    uni = await UniClient.create(private_key=private_key)
    async with uni:
        price, qty = await _resting_price_qty(uni._client)
        print(f"price={price} qty={qty}")

        order = await uni.futures_order_create(
            symbol=SYMBOL,
            side=OrderSide.BUY,
            type=OrderType.LIMIT,
            quantity=qty,
            price=price,
        )
        print(f"[OK]   uni.create: {_short(order)}")

        # Отмена через raw-клиент внутри uni (унифицированной отмены пока нет).
        order_id = int(order["id"])
        canceled = await uni._client.futures_order_cancel(SYMBOL, order_id=order_id)
        print(f"[OK]   cancel: {_short(canceled)}")


if __name__ == "__main__":
    asyncio.run(main())
