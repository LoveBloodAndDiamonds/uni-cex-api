# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Что это за проект?

`unicex` — асинхронная Python-библиотека с унифицированным интерфейсом для работы с криптовалютными биржами. Поддерживает REST и WebSocket API для спотового и USDT-фьючерсного рынков.

## Команды разработки

```bash
# Линтинг и автоисправление
ruff check . --fix
ruff format .

# Запуск отдельного теста (тесты — ad-hoc скрипты, не pytest)
python tests/binance/client_test.py
python tests/uni_client_test.py

# Установка из исходников
pip install -e .

# Установка pre-commit хуков
pre-commit install
```

## Структура проекта

```
unicex/
├── _abc/           # Абстрактные интерфейсы: IUniClient, IUniWebsocketManager, IExchangeInfo
├── _base/          # Базовые HTTP/WebSocket клиенты (переиспользуются всеми биржами)
├── <exchange>/     # Каждая биржа: client.py, adapter.py, uni_client.py, websocket_manager.py, ...
├── types.py        # TypedDict-модели для всех унифицированных ответов
├── enums.py        # Exchange, Timeframe, OrderSide, OrderType, MarginType, ...
├── exceptions.py   # NotSupported, NotAuthorized, ResponseError, AdapterError, ...
├── utils.py        # catch_adapter_errors, decorate_all_methods, batched_list, ...
└── mapper.py       # get_uni_client(), get_uni_websocket_manager(), get_exchange_info()

tests/              # Ad-hoc скрипты запускаются напрямую через python (не pytest)
docs/               # Сырые JSON-ответы от API бирж (для справки при реализации)
```

Поддерживаемые биржи (10): Aster, Binance, Bitget, Bybit, Gate.io, Hyperliquid, Mexc, OKX, Kucoin, BingX.

## Трёхслойная архитектура (на каждую биржу)

1. **`client.py`** — сырой REST-клиент, тонкая обёртка над HTTP. Методы возвращают `dict | list`. Докстринг содержит ссылку на документацию API биржи.
2. **`adapter.py`** — статические методы преобразования сырых данных в унифицированные TypedDict. Декорирован `@decorate_all_methods(catch_adapter_errors)`.
3. **`uni_client.py`** — реализует `IUniClient`: вызывает `client` → передаёт результат в `adapter` → возвращает типизированный ответ.

Дополнительно на каждую биржу:
- **`websocket_manager.py`** — сырой WebSocket-менеджер (потоки данных).
- **`uni_websocket_manager.py`** — реализует `IUniWebsocketManager` с унификацией сообщений через `_make_wrapper`.
- **`exchange_info.py`** — фоновая загрузка рыночных параметров (шаг цены, объём контракта).

## Ключевые паттерны

### overload для методов с опциональным symbol

```python
@overload
async def funding_rate(self, symbol: str) -> float: ...
@overload
async def funding_rate(self, symbol: None) -> dict[str, float]: ...
@overload
async def funding_rate(self) -> dict[str, float]: ...

async def funding_rate(self, symbol: str | None = None) -> dict[str, float] | float:
    ...
    return adapted_data[symbol] if symbol else adapted_data
```

### asyncio.gather() для параллельных запросов

```python
mark_data, funding_data = await asyncio.gather(
    self._client.futures_mark_price(symbol=symbol),
    self._client.futures_funding_info(),
)
```

### Заглушки для нереализованных методов

```python
async def method_name(self, ...) -> ...:
    raise NotImplementedError("Method will be implemented later.")
```

### IExchangeInfo — классовый паттерн (не инстанс)

`ExchangeInfo` используется как класс (не создаётся экземпляр). Все методы — `@classmethod`. Фоновое обновление: `await ExchangeInfo.start()`. Данные хранятся в `_tickers_info` и `_futures_tickers_info`.

## Типы данных (types.py)

- Все унифицированные ответы — `TypedDict`.
- Словари с тикером в качестве ключа — `type` alias: `type FundingInfoDict = dict[str, FundingInfoItem]`.
- Временны́е поля всегда в **миллисекундах** (`int`).
- Ставки фандинга — в **процентах** (умножены на 100 из долей).
- Новые типы обязательно добавлять в `__all__` в `types.py`.

## Docstring стиль

**Публичные методы (uni_client, abc):**
```python
"""Описание.

Параметры:
    symbol (`str | None`): Название тикера (Опционально).

Возвращает:
    `FundingInfoItem | FundingInfoDict`: Описание.
"""
```
**Сырой клиент (`client.py`):** одна строка + ссылка на документацию API.

**Приватный метод:** одна строка описания.

Ruff игнорирует `D102` в `uni_client.py`, `uni_websocket_manager.py`, `adapter.py` — докстринги для этих методов писать не нужно.

## Что НЕ делать

- Не добавлять новые методы в `IUniClient` или `IUniWebsocketManager` без реализации заглушек во всех 10 биржах.
- Не забывать обновлять счётчики в `README.md` (колонки `UniClient (N)`, `UniWebsocketManager (N)`) после добавления нового метода.
- Не возвращать `None` там, где ожидается `int` — биржи без поддержки должны кидать `NotImplementedError`.
- Не использовать `asyncio.sleep()` или синхронные вызовы внутри async-методов.
- Докстринги писать только в `_abc/` для интерфейсных методов; в реализациях биржи (`uni_client.py`, `adapter.py`) — не нужны.
