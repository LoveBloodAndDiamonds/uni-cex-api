import asyncio
import sys
import time
from collections.abc import Awaitable, Callable

from loguru import logger

from unicex import Exchange, get_uni_websocket_manager, start_exchanges_info
from unicex.enums import MarketType
from unicex.types import KlineDict, LoggerLike, TradeDict
from unicex.utils import symbol_to_exchange_format
from unicex.mexc.exchange_info import ExchangeInfo


class MinuteKlineAggregator:
    """Агрегирует сделки в минутные свечи и выводит их через логгер."""

    _MINUTE_MS = 60_000

    def __init__(self, symbol: str, logger_instance: LoggerLike) -> None:
        """Создает агрегатор для указанного символа.

        - Параметры:
        symbol (`str`): Символ, для которого собираются свечи.
        logger_instance (`LoggerLike`): Логгер для вывода результатов.

        Возвращает:
          `None`: Ничего не возвращает.
        """

        self._symbol = symbol
        self._logger = logger_instance
        self._current_minute: int | None = None
        self._current_kline: KlineDict | None = None
        self._flush_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def add_trade(self, trade: TradeDict) -> None:
        """Добавляет сделку в текущую минутную свечу.

        - Параметры:
        trade (`TradeDict`): Сделка, полученная из веб-сокета.

        Возвращает:
          `None`: Ничего не возвращает.
        """

        async with self._lock:
            minute_start = self._minute_start(trade["t"])

            if self._current_minute != minute_start:
                # Закрываем предыдущую свечу перед переходом на новую минуту.
                self._flush_current_kline()
                self._start_new_kline(trade, minute_start)
                return

            self._update_kline(trade)

    def _start_new_kline(self, trade: TradeDict, minute_start: int) -> None:
        """Создает новую свечу для только что наступившей минуты."""

        price = trade["p"]
        volume = trade["v"]
        self._current_minute = minute_start
        self._current_kline = KlineDict(
            s=trade["s"],
            t=minute_start,
            o=price,
            h=price,
            l=price,
            c=price,
            v=volume,
            q=price * volume,
            T=None,
            x=None,
        )
        self._schedule_flush(minute_start)

    def _update_kline(self, trade: TradeDict) -> None:
        """Обновляет цену и объем текущей свечи."""

        if self._current_kline is None:
            return

        price = trade["p"]
        volume = trade["v"]
        self._current_kline["h"] = max(self._current_kline["h"], price)
        self._current_kline["l"] = min(self._current_kline["l"], price)
        self._current_kline["c"] = price
        self._current_kline["v"] += volume
        self._current_kline["q"] += price * volume

    def _flush_current_kline(self) -> None:
        """Финализирует и печатает текущую свечу."""

        if self._current_kline is None or self._current_minute is None:
            return

        self._current_kline["T"] = self._current_minute + self._MINUTE_MS
        self._current_kline["x"] = True
        self._logger.info("Минутная свеча {}: {}", self._symbol, self._current_kline)

        self._current_kline = None
        self._current_minute = None
        self._cancel_flush_task()

    def _schedule_flush(self, minute_start: int) -> None:
        """Планирует автоматическое закрытие свечи по истечению минуты."""

        self._cancel_flush_task()

        async def _delayed_flush() -> None:
            """Закрывает свечу по таймеру."""

            delay = max(0.0, (minute_start + self._MINUTE_MS - self._now_ms()) / 1000)
            await asyncio.sleep(delay)
            async with self._lock:
                if self._current_minute == minute_start:
                    self._flush_current_kline()

        self._flush_task = asyncio.create_task(_delayed_flush())

    def _cancel_flush_task(self) -> None:
        """Отменяет отложенное закрытие свечи."""

        if self._flush_task is None:
            return

        self._flush_task.cancel()
        self._flush_task = None

    @staticmethod
    def _minute_start(timestamp_ms: int) -> int:
        """Возвращает отметку начала минуты для таймстампа."""

        return (timestamp_ms // MinuteKlineAggregator._MINUTE_MS) * MinuteKlineAggregator._MINUTE_MS

    @staticmethod
    def _now_ms() -> int:
        """Возвращает текущее время в миллисекундах."""

        return int(time.time() * 1000)


def create_callback(aggregator: MinuteKlineAggregator) -> Callable[[TradeDict], Awaitable[None]]:
    """Создает callback, пересылающий сделки в агрегатор.

    - Параметры:
    aggregator (`MinuteKlineAggregator`): Экземпляр агрегатора минутных свечей.

    Возвращает:
      `Callable[[TradeDict], Awaitable[None]]`: Асинхронный callback для менеджера.
    """

    async def _callback(trade: TradeDict) -> None:
        """Передает сделку в агрегатор."""
        await aggregator.add_trade(trade)

    return _callback


logger.remove()
logger.add(sys.stderr, level="DEBUG")
symbol = "BTCUSDT"


async def main() -> None:
    """Запускает поток трейдов и агрегирует их в минутные свечи.

    Возвращает:
      `None`: Ничего не возвращает.
    """

    await start_exchanges_info()
    await asyncio.sleep(1.5)

    for e in [
        # Exchange.BINANCE,
        # Exchange.BYBIT,
        # Exchange.BITGET,
        # Exchange.OKX,
        # Exchange.MEXC,
        Exchange.GATE,
    ]:
        aggregator = MinuteKlineAggregator(symbol=symbol, logger_instance=logger)
        callback = create_callback(aggregator)
        uni_websocket_manager_factory = get_uni_websocket_manager(e)
        weboskcet_manager = uni_websocket_manager_factory(logger=logger)
        websocket = weboskcet_manager.futures_trades(
            callback=callback, symbol=symbol_to_exchange_format(symbol, e, MarketType.FUTURES)
        )
        await websocket.start()


if __name__ == "__main__":
    asyncio.run(main())


"""
+ Exchange.BINANCE,
+ Exchange.BYBIT,
+ Exchange.BITGET,
+ Exchange.OKX,
+ Exchange.MEXC,
Exchange.GATE,
"""
