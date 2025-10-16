# Unified Crypto Exchange API

`unicex` — асинхронная библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс поверх «сырых» REST и WebSocket API разных бирж. Поддерживает спотовый и USDT-фьючерсный рынки.

## ✅ Статус реализации

| Exchange        | Client | Auth | WS Manager | User WS | Uni Client | Uni WS Manager | ExchangeInfo |
|-----------------|--------|------|------------|---------|------------|----------------|--------------|
| **Binance**     | ✓      | ✓    | ✓          | ✓       | ✓          | ✓              | ✓            |
| **Bitget**      | ✓      | ✓    | ✓          |         | ✓          |                | ✓            |
| **Bybit**       | ✓      | ✓    | ✓          |         | ✓          | ✓              | ✓            |
| **Gateio**      | ✓      | ✓    | ✓          |         | ✓          |                | ✓            |
| **Hyperliquid** | ✓      | ✓    | ✓          | ✓       | ✓          |                |              |
| **Mexc**        | ✓      | ✓    | ✓          |         | ✓          |                | ✓            |
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


### Пример: Округление цен используя фоновый класс ExchangeInfo


```python
import asyncio
from unicex import start_exchanges_info, get_exchange_info, Exchange


async def main() -> None:
    # ⏳ Запускаем фоновые процессы, которые собирают рыночные параметры всех бирж:
    #  - количество знаков после точки для цены и объема
    #  - множители контрактов для фьючерсов
    await start_exchanges_info()

    # Небольшая пауза, чтобы данные успели подгрузиться
    await asyncio.sleep(1)

    # 1️⃣ Пример 1: Округление цены для фьючерсов OKX
    okx_exchange_info = get_exchange_info(Exchange.OKX)
    okx_rounded_price = okx_exchange_info.round_futures_price("BTC-USDT-SWAP", 123456.1234567890)
    print(okx_rounded_price)  # >> 123456.1

    # 2️⃣ Пример 2: Округление объема для спота Binance
    binance_exchange_info = get_exchange_info(Exchange.BINANCE)
    binance_rounded_quantity = binance_exchange_info.round_quantity("BTCUSDT", 1.123456789)
    print(binance_rounded_quantity)  # >> 1.12345

    # 3️⃣ Пример 3: Получение множителя контракта (например, Mexc Futures)
    mexc_exchange_info = get_exchange_info(Exchange.MEXC)
    mexc_contract_multiplier = mexc_exchange_info.get_futures_ticker_info("BTC_USDT")["contract_size"]
    print(mexc_contract_multiplier)  # >> 0.0001

    # 4️⃣ Пример 4: Реальное применение — вычисляем тейк-профит вручную
    # Допустим, позиция открыта по 123123.1 USDT, хотим +3.5% тейк-профит:
    take_profit_raw = 123123.1 * 1.035
    print("До округления:", take_profit_raw)  # >> 127432.40849999999

    # Биржа требует цену в допустимом формате — округляем:
    take_profit = okx_exchange_info.round_futures_price("BTC-USDT-SWAP", take_profit_raw)
    print("После округления:", take_profit)  # >> 127432.4

    # Теперь это число можно безопасно передать в API без ошибок:
    # await client.create_order(symbol="BTC-USDT-SWAP", price=take_profit, ...)


if __name__ == "__main__":
    asyncio.run(main())
```
