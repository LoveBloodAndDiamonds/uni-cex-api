import time

from enum import StrEnum

class OrderStatus(StrEnum):



interval = 0.1
for _ in range(100):
    try:
        symbol = "BTCUSDT"
        last_price = get_last_price(symbol)
        order_id = place_market_order(symbol, last_price)
        time.sleep(0.1)
        status = check_order_status(order_id, symbol)
        if status in ["FILLED", "PARTIALLY_FILLED"]:
            return
        else:
            cancel_order(order_id, symbol)
    except Exception:
        pass
    time.sleep(interval)
