# Unified Crypto Exchange API

`unicex` — асинхронная библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс поверх «сырых» REST и WebSocket API разных бирж.

## ✅ Статус реализации

## ✅ Статус реализации

| Exchange    | Client | Client Auth | Client Generic | WS Manager | User WS |
|-------------|--------|-------------|----------------|------------|---------|
| Binance     | ✅     | ✅          | ✅             | ✅         | ✅      |
| Bitget      | ✅     | ✅          | ✅             | ✅         |         |
| Bitrue      |        | ✅          | ✅             |            |         |
| Bitunix     |        |             |                |            |         |
| Btse        |        | ✅          | ✅             |            |         |
| Bybit       | ✅     | ✅          | ✅             |            |         |
| Gateio      |        |             | ✅             |            |         |
| Hyperliquid |        |             |                |            |         |
| Kcex        |        |             |                |            |         |
| Kraken      |        | ✅          | ✅             |            |         |
| Kucoin      |        | ✅          | ✅             |            |         |
| Mexc        | ✅     | ✅          | ✅             |            |         |
| Okx         |        | ✅          | ✅             |            |         |
| Weex        |        |             |                |            |         |
| Xt          |        |             |                |            |         |

---

### 📖 Описание колонок

- **Client** – Обертки над HTTP методами следующих разделов: market, order, position, account.
- **Client Auth** – Поддержка авторизации и приватных эндпоинтов.
- **Client Generic** – Универсальная функция для вызова не обернутых методов API.
- **WS Manager** – Обертки над вебсокетами биржи.
- **User WS** – Поддержка пользовательских вебсокетов.

---

## ✅ Статус реализации (Унифицированный интерфейс)

| Exchange    | UniClient | UniWebsocketManager |
|-------------|-----------|----------------------|
| Binance     | ✅        | ✅                   |
| Bitget      | ✅        |                      |
| Bitrue      |           |                      |
| Bitunix     |           |                      |
| Btse        |           |                      |
| Bybit       | ✅        |                      |
| Gateio      |           |                      |
| Hyperliquid |           |                      |
| Kcex        |           |                      |
| Kraken      |           |                      |
| Kucoin      |           |                      |
| Mexc        |           |                      |
| Okx         |           |                      |
| Weex        |           |                      |
| Xt          |           |                      |

---

## 🚀 Быстрый старт

- Установка: `pip install unicex` или из исходников: `pip install -e .`
- Библиотека полностью асинхронная. Примеры импорта:
  - Сырые клиенты: `from unicex.binance import Client`
  - Унифицированные клиенты: `from unicex.binance import UniClient`
  - Вебсокет менеджеры: `from unicex.binance import WebsocketManager, UniWebsocketManager`

Пример: получить последние цены через унифицированный клиент Binance

```
import asyncio
from unicex.binance import UniClient


async def main():
    client = await UniClient.create()
    prices = await client.last_price()
    print(prices["BTCUSDT"])
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Пример: подписаться на трейды через унифицированный WS‑менеджер Bitget

```
import asyncio
from unicex.bitget import UniWebsocketManager
from unicex import TradeDict


async def on_trade(msg: TradeDict):
    print(msg)


async def main():
    uwm = UniWebsocketManager()
    socket = uwm.trades(callback=on_trade, symbol="BTCUSDT")
    await socket.start()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧑‍💻 Блок для разработчика

### 📋 Todo
- Пересмотреть вопрос: должен ли быть адаптер интерфейсом?
- Доделать BitgetClient и проверить типы
- Добавить overload к методам с `None, None`
- Определить порядок полей, возвращаемых адаптером
- Написать 1–2 примера
- Не делать .get в адаптере
