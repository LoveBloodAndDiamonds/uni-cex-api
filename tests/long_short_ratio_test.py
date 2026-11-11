"""Живая проверка `long_short_ratio` и `long_short_ratio_history` на всех биржах.

Проверяет: long + short ≈ 1, ratio ≈ long / short, свежесть последней точки
(не старше 15 минут), сортировку истории по возрастанию.
"""

import asyncio
import math
import time

from loguru import logger

from unicex import Exchange, MarketType, get_uni_client
from unicex.utils import symbol_to_exchange_format

logger.remove()

SYMBOL = "BTCUSDT"
MAX_AGE_MS = 15 * 60 * 1000
TOLERANCE = 0.01


def check_item(item: dict) -> list[str]:
    """Проверяет инварианты одной точки и возвращает список ошибок."""
    errors = []
    if abs(item["long"] + item["short"] - 1) > TOLERANCE:
        errors.append(f"long + short = {item['long'] + item['short']:.4f}")
    if item["short"]:
        expected = item["long"] / item["short"]
        if not math.isclose(item["ratio"], expected, rel_tol=TOLERANCE):
            errors.append(f"ratio {item['ratio']:.4f} != long / short {expected:.4f}")
    elif item["ratio"] != float("inf"):
        errors.append(f"short == 0, but ratio = {item['ratio']}")
    return errors


async def test_exchange(exchange: Exchange) -> None:
    """Проверяет методы на одной бирже и печатает результат."""
    symbol = symbol_to_exchange_format(SYMBOL, exchange, MarketType.FUTURES)
    client = await get_uni_client(exchange).create()
    try:
        last = await client.long_short_ratio(symbol)
        history = await client.long_short_ratio_history(symbol, limit=3)
    except NotImplementedError as e:
        print(f"[{exchange}] ⚪ not implemented: {e}")
        return
    except Exception as e:
        print(f"[{exchange}] ❌ {type(e).__name__}: {e}")
        return
    finally:
        await client.close_connection()

    errors = check_item(last)
    for item in history:
        errors += check_item(item)
    age_ms = int(time.time() * 1000) - last["t"]
    if age_ms > MAX_AGE_MS:
        errors.append(f"last point is {age_ms / 60000:.1f} min old")
    times = [item["t"] for item in history]
    if times != sorted(times) or len(set(times)) != len(times):
        errors.append(f"history is not strictly ascending: {times}")
    if len(history) != 3:
        errors.append(f"history has {len(history)} points instead of 3")
    if history and history[-1] != last:
        errors.append("last history point differs from long_short_ratio")

    status = "✅" if not errors else "❌"
    print(
        f"[{exchange}] {status} {symbol}: long={last['long']:.4f} short={last['short']:.4f} "
        f"ratio={last['ratio']:.4f} age={age_ms / 60000:.1f}m history_t={times}"
    )
    for error in errors:
        print(f"   - {error}")


async def main() -> None:
    """Запускает проверку по всем биржам."""
    await asyncio.gather(*[test_exchange(e) for e in Exchange])


if __name__ == "__main__":
    asyncio.run(main())
