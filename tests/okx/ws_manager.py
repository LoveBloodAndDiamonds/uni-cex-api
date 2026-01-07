import asyncio
from datetime import datetime
from typing import Any, TypedDict

from unicex.okx import WebsocketManager, ExchangeInfo, start_exchange_info


class Candle(TypedDict):
    """Описывает агрегированную свечу."""

    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class OneSecondCandleAggregator:
    """Агрегирует сделки в свечи с таймфреймом 1 секунда."""

    def __init__(self) -> None:
        """Инициализирует агрегатор без активной свечи."""
        self._current_second: int | None = None
        self._open_price: float = 0.0
        self._high_price: float = 0.0
        self._low_price: float = 0.0
        self._close_price: float = 0.0
        self._volume: float = 0.0

    def process_trade(self, timestamp: float, price: float, size: float) -> Candle | None:
        """Добавляет сделку и возвращает закрытую свечу, если таймфрейм завершён.

        - Параметры:
        timestamp (`float`): Метка времени сделки в секундах.
        price (`float`): Цена сделки.
        size (`float`): Объём сделки.

        Возвращает:
          `Candle | None`: Свеча прошлого интервала, если он завершился.
        """
        second = int(timestamp)

        if self._current_second is None:
            self._start_new(second, price, size)
            return None

        if second == self._current_second:
            self._update_current(price, size)
            return None

        closed_candle = self._build_candle()
        self._start_new(second, price, size)
        return closed_candle

    def _start_new(self, candle_second: int, price: float, size: float) -> None:
        """Создаёт новую текущую свечу."""
        self._current_second = candle_second
        self._open_price = price
        self._high_price = price
        self._low_price = price
        self._close_price = price
        self._volume = size

    def _update_current(self, price: float, size: float) -> None:
        """Обновляет параметры активной свечи."""
        if price > self._high_price:
            self._high_price = price
        if price < self._low_price:
            self._low_price = price

        self._close_price = price
        self._volume += size

    def _build_candle(self) -> Candle:
        """Возвращает словарь с данными завершённой свечи."""
        assert self._current_second is not None
        return Candle(
            ts=self._current_second,
            open=self._open_price,
            high=self._high_price,
            low=self._low_price,
            close=self._close_price,
            volume=self._volume,
        )


CANDLE_AGGREGATOR = OneSecondCandleAggregator()


async def callback(msg: dict[str, Any]) -> None:
    """Обрабатывает входящие сделки и печатает закрытые свечи 1 секунды.

    - Параметры:
    msg (`dict[str, Any]`): Сообщение от WebSocket со списком сделок.

    Возвращает:
      `None`: Ничего не возвращает, только выводит свечи в терминал.
    """
    try:
        data = msg["data"]
        for item in data:
            px = float(item["px"])
            sz = float(item["sz"]) * 0.01
            ts = int(item["ts"]) / 1000
            closed_candle = CANDLE_AGGREGATOR.process_trade(
                timestamp=ts,
                price=px,
                size=sz,
            )

            # Выводим свечу, когда завершился секундный интервал.
            if closed_candle:
                dt = datetime.fromtimestamp(closed_candle["ts"])
                print(
                    f"{dt} "
                    f"O:{closed_candle['open']:.4f} "
                    f"H:{closed_candle['high']:.4f} "
                    f"L:{closed_candle['low']:.4f} "
                    f"C:{closed_candle['close']:.4f} "
                    f"V:{closed_candle['volume']:.4f}"
                )

    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    await start_exchange_info()

    await asyncio.sleep(2)

    ticker_info = ExchangeInfo.get_futures_ticker_info("BTC-USDT-SWAP")

    # for k in ticker_info.keys():
    # print(k)
    print(ticker_info)

    # return

    manager = WebsocketManager()

    c = {"callback": callback}
    # ws = manager.instruments(**c, inst_type="SWAP")
    # ws = manager.open_interest(**c, inst_id="BTC-USDT-SWAP")
    # ws = manager.funding_rate(**c, inst_id="BTC-USDT-SWAP")
    # ws = manager.price_limit(**c, inst_id="BTC-USDT-SWAP")
    # ws = manager.option_summary(**c, inst_family="BTC-USD")
    # ws = manager.estimated_price(**c, inst_type="FUTURES", inst_family="BTC-USD")  # type: ignore
    # ws = manager.mark_price(**c, inst_id="BTC-USDT-SWAP")
    # ws = manager.index_tickers(**c, inst_id="BTC-USDT")
    # ws = manager.mark_price_candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    # ws = manager.index_candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    # ws = manager.liquidation_orders(**c, inst_type="SWAP")
    # ws = manager.adl_warning(**c, inst_type="SWAP")  # type: ignore
    # ws = manager.tickers(**c, inst_id="BTC-USDT")
    # ws = manager.candlesticks(**c, inst_id="BTC-USDT", interval="1m")
    # ws = manager.trades(**c, inst_id="BTC-USDT-SWAP")
    ws = manager.all_trades(**c, inst_id="BTC-USDT-SWAP")
    # ws = manager.order_book(**c, channel="books", inst_id="BTC-USDT-SWAP")

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
