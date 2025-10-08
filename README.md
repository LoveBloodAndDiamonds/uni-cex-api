# Unified Crypto Exchange API

`unicex` — асинхронная библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс поверх «сырых» REST и WebSocket API разных бирж.

## ✅ Статус реализации

| Exchange        | Client | Auth | WS Manager | User WS | Uni Client | Uni WS Manager | ExchangeInfo |
|-----------------|--------|------|------------|---------|------------|----------------|--------------|
| **Binance**     | ✓      | ✓    | ✓          | ✓       | ✓          | ✓              |              |
| **Bitget**      | ✓      | ✓    | ✓          |         | ✓          |                |              |
| **Bybit**       | ✓      | ✓    | ✓          |         | ✓          |                |              |
| **Gateio**      | ✓      | ✓    | ✓          |         | ✓          |                |              |
| **Hyperliquid** | ✓      | ✓    | ✓          | ✓       | ✓          |                |              |
| **Mexc**        | ✓      | ✓    | ✓          |         | ✓          |                |              |
| **Okx**         | ✓      | ✓    | ✓          |         | ✓          |                | ✓            |
---


### 📖 Описание колонок

- **Client** – Обертки над HTTP методами следующих разделов: market, order, position, account.
- **Auth** – Поддержка авторизации и приватных эндпоинтов.
- **WS Manager** – Обертки над вебсокетами биржи.
- **User WS** – Поддержка пользовательских вебсокетов.
- **UniClient** –Унифированный клиент.
- **UniWebsocketManager** – Унифированный менеджер вебсокетов.
- **ExchangeInfo** - Информация о бирже для округления цен и объемов
---

## 🚀 Быстрый старт

- Установка: `pip install unicex` или из исходников: `pip install -e .`
- Библиотека полностью асинхронная. Примеры импорта:
  - Сырые клиенты: `from unicex.binance import Client`
  - Унифицированные клиенты: `from unicex.binance import UniClient`
  - Вебсокет менеджеры: `from unicex.binance import WebsocketManager, UniWebsocketManager`

### Пример: Получение рыночных данных через API

```python
import asyncio

from unicex import Exchange, Timeframe, get_uni_client

# Выбираем биржу, с которой хотим работать.
# Поддерживаются: Binance, Bybit, Bitget, Mexc, Gateio, Hyperliquid и другие.
exchange = Exchange.BYBIT


async def main() -> None:
    """Пример простого использования унифицированного клиента unicex."""
    # 1️⃣ Создаём клиент для выбранной биржи
    client = await get_uni_client(exchange).create()

    # 2️⃣ Получаем открытый интерес по всем контрактам
    open_interest = await client.open_interest()
    print(open_interest)

    # Пример вывода:
    # {
    #   "BTCUSDT": {"t": 1759669833728, "v": 61099320.0},
    #   "ETHUSDT": {"t": 1759669833728, "v": 16302340.0},
    #   "SOLUSDT": {"t": 1759669833728, "v": 3427780.0},
    #   ...
    # }

    # 3️⃣ Можно точно так же получать другие данные в едином формате:
    await client.tickers()  # список всех тикеров
    await client.futures_tickers()  # тикеры фьючерсов
    await client.ticker_24hr()  # статистика за 24 часа (spot)
    await client.futures_ticker_24hr()  # статистика за 24 часа (futures)
    await client.klines("BTCUSDT", Timeframe.MIN_5)  # свечи спота
    await client.futures_klines("BTCUSDT", Timeframe.HOUR_1)  # свечи фьючерсов
    await client.funding_rate()  # ставка финансирования


if __name__ == "__main__":
    asyncio.run(main())

```

### Пример: Получение данных в реальном времени через Websocket API

```python
import asyncio
from unicex import Exchange, TradeDict, get_uni_websocket_manager
from unicex.enums import Timeframe

# Выбираем биржу, с которой хотим работать.
# Поддерживаются: Binance, Bybit, Bitget, Mexc, Gateio, Hyperliquid и другие.
exchange = Exchange.BITGET


async def main() -> None:
    """Пример простого использования унифицированного менеджера Websocket от UniCEX."""

    # 1️⃣ Создаём WebSocket-менеджер для выбранной биржи
    ws_manager = get_uni_websocket_manager(exchange)()

    # 2️⃣ Подключаемся к потоку сделок (aggTrades)
    aggtrades_ws = ws_manager.aggtrades(
        callback=callback,
        symbols=["BTCUSDT", "ETHUSDT"],
    )

    # Запускаем получение данных
    await aggtrades_ws.start()

    # 3️⃣ Примеры других типов потоков:
    futures_aggtrades_ws = ws_manager.futures_aggtrades(
        callback=callback,
        symbols=["BTCUSDT", "ETHUSDT"],
    )

    klines_ws = ws_manager.klines(
        callback=callback,
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe=Timeframe.MIN_5,
    )

    futures_klines_ws = ws_manager.futures_klines(
        callback=callback,
        symbols=["BTCUSDT", "ETHUSDT"],
        timeframe=Timeframe.MIN_1,
    )

    # 💡 Также у каждой биржи есть свой WebsocketManager:
    #     unicex.<exchange>.websocket_manager.WebsocketManager
    # В нём реализованы остальные методы для работы с WS API.


async def callback(trade: TradeDict) -> None:
    """Обработка входящих данных из Websocket."""
    print(trade)
    # Пример вывода:
    # {'t': 1759670527594, 's': 'BTCUSDT', 'S': 'BUY',  'p': 123238.87, 'v': 0.05}
    # {'t': 1759670527594, 's': 'BTCUSDT', 'S': 'BUY',  'p': 123238.87, 'v': 0.04}
    # {'t': 1759670346828, 's': 'ETHUSDT', 'S': 'SELL', 'p': 4535.0,    'v': 0.0044}
    # {'t': 1759670347087, 's': 'ETHUSDT', 'S': 'BUY',  'p': 4534.91,   'v': 0.2712}


if __name__ == "__main__":
    asyncio.run(main())
```
