import time
from collections import defaultdict

from loguru import logger

from unicex import (
    AggTradeDict,
    Exchange,
    MarketType,
    Websocket,
    get_uni_client,
    get_uni_websocket_manager,
)
from unicex.extra import TimeoutTracker, generate_tv_link, percent_greater, percent_less

# Настройки скринера
EXCHANGE = Exchange.BINANCE  # Биржа
MARKET_TYPE = MarketType.SPOT  # Тип рынка
MIN_PRICE_CHANGE_PCT = 1  # Порог изменения цены в процентах для того, чтобы прислать сигнал
MAX_CHANGE_TIME_SEC = 60  # Максимальное допустимое время изменения цены в секундах


class PumpDumpScreener:
    """Скринер пампов и дампов."""

    def __init__(
        self,
        exchange: Exchange,
        market_type: MarketType,
        min_price_change_pct: float,
        max_change_time_sec: int,
    ) -> None:
        """Инициализация скринера пампов и дампов.

        Параметры:
            exchange (`Exchange`): Маркетплейс.
            market_type (`MarketType`): Тип рынка.
            min_price_change_pct (`float`): Минимальный порог изменения цены в процентах для того, чтобы прислать сигнал.
            max_change_time_sec (`int`): Максимальное допустимое время изменения цены в секундах.
        """
        self.exchange = exchange
        self.market_type = market_type
        self.min_price_change_pct = min_price_change_pct
        self.max_change_time_sec = max_change_time_sec
        self.client = get_uni_client(exchange)()
        self.websocket_manager = get_uni_websocket_manager(exchange)()
        self.aggtrades: dict[str, list] = defaultdict(list)
        self.timeout_tracker = TimeoutTracker[str]()
        self.running = False

    def start(self) -> None:
        """Запуск скринера пампов и дампов."""
        logger.info("Запуск скринера пампов и дампов")
        self.running = True

        # Получаем список тикеров, котоыре нужно запустить
        tickers_chunks = self._get_chunked_tickers_list()

        # Запускаем вебсокеты
        websockets = self._create_aggtrades_websockets(tickers_chunks)
        self._start_aggtrades_websockets(websockets)

        # Ожидаем завершения
        self._wait_until_stopped()

        # Освобождаем ресурсы
        for websocket in websockets:
            websocket.stop()
        self.client.close()

    def stop(self) -> None:
        """Остановка скринера пампов и дампов."""
        logger.info("Остановка скринера пампов и дампов")
        self.running = False

    def _wait_until_stopped(self) -> None:
        """Блокирует выполнение скрипта, до остановки скринера."""
        while self.running:
            time.sleep(1)

    def _get_chunked_tickers_list(self) -> list[tuple[str, ...]]:
        """Получение списка тикеров."""
        if self.market_type == MarketType.SPOT:
            return self.client.tickers_batched()
        return self.client.futures_tickers_batched()

    def _create_aggtrades_websockets(
        self, tickers_chunks: list[tuple[str, ...]]
    ) -> list[Websocket]:
        """Запуск вебсокета для получения сделок, по которым мы будем отслеживать изменение цены."""
        websockets = []
        for batch in tickers_chunks:
            if self.market_type == MarketType.SPOT:
                websocket = self.websocket_manager.aggtrades(
                    callback=self._handle_aggtrades_message,
                    symbols=batch,
                )
            else:
                websocket = self.websocket_manager.futures_aggtrades(
                    callback=self._handle_aggtrades_message,
                    symbols=batch,
                )
            websockets.append(websocket)
        return websockets

    def _start_aggtrades_websockets(self, websockets: list[Websocket]) -> None:
        """Запуск вебсокетов для получения сделок."""
        for websocket in websockets:
            websocket.start()
            time.sleep(1)

    def _handle_aggtrades_message(self, aggtrade: AggTradeDict) -> None:
        """Обработка аггрегированной сделки."""
        symbol = aggtrade["s"]
        price = aggtrade["p"]
        timestamp = aggtrade["t"] // 1000  # ms -> sec

        # Добавляем новую сделку
        self.aggtrades[symbol].append((timestamp, price))

        # Очищаем старые сделки (оставляем только за max_change_time_sec)
        cutoff = time.time() - self.max_change_time_sec
        self.aggtrades[symbol] = [(ts, p) for ts, p in self.aggtrades[symbol] if ts >= cutoff]

        # Проверяем таймаут
        if self.timeout_tracker.is_blocked(symbol):
            return

        # Если слишком мало данных — выходим
        if not self.aggtrades[symbol]:
            return

        prices = [p for _, p in self.aggtrades[symbol]]
        min_price = min(prices)
        max_price = max(prices)

        # Проверяем памп
        pump_change = percent_greater(lower=min_price, higher=price)
        if pump_change >= self.min_price_change_pct:
            self.timeout_tracker.block(symbol, self.max_change_time_sec)
            tv_link = generate_tv_link(self.exchange, self.market_type, symbol)
            logger.success(
                f"[PUMP] {symbol}: цена выросла на {pump_change:.2f}% (с {min_price} → {price})\n{tv_link}"
            )

        # Проверяем дамп
        dump_change = percent_less(higher=max_price, lower=price)
        if dump_change >= self.min_price_change_pct:
            self.timeout_tracker.block(symbol, self.max_change_time_sec)
            tv_link = generate_tv_link(self.exchange, self.market_type, symbol)
            logger.success(
                f"[DUMP] {symbol}: цена упала на {dump_change:.2f}% (с {max_price} → {price})\n{tv_link}"
            )


def main() -> None:
    """Точка входа в приложение."""
    screener = PumpDumpScreener(
        EXCHANGE,
        MARKET_TYPE,
        min_price_change_pct=MIN_PRICE_CHANGE_PCT,
        max_change_time_sec=MAX_CHANGE_TIME_SEC,
    )
    screener.start()
    screener.stop()


if __name__ == "__main__":
    main()
