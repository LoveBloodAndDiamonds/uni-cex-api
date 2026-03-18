# Repository Guidelines

> Проектные инструкции для Claude Code. Дополняют глобальный `~/.claude/CLAUDE.md`.

## Что это за проект?

`unicex` — асинхронная Python-библиотека с унифицированным интерфейсом для работы с криптовалютными биржами. Поддерживает REST и WebSocket API для спотового и USDT-фьючерсного рынков.

## Структура проекта

```
unicex/
├── _abc/           # Абстрактные интерфейсы: IUniClient, IUniWebsocketManager
├── _base/          # Базовые HTTP/WebSocket клиенты (переиспользуются биржами)
├── binance/        # Каждая биржа: client.py, adapter.py, uni_client.py, ...
├── bybit/
├── bitget/
├── gate/
├── okx/
├── aster/
├── hyperliquid/
├── mexc/
├── kucoin/
├── bingx/
├── types.py        # TypedDict-модели для всех унифицированных ответов
├── enums.py        # Exchange, Timeframe, OrderSide, OrderType, MarginType, ...
├── exceptions.py   # NotSupported, NotAuthorized, ResponseError, ...
├── utils.py        # catch_adapter_errors, decorate_all_methods, batched_list, ...
└── mapper.py       # get_uni_client(), get_uni_websocket_manager()

tests/              # Ad-hoc скрипты и примеры (не формальная тест-матрица)
docs/               # Сырые JSON-ответы от API бирж (для справки при реализации)
```

## Архитектурные паттерны

### Трёхслойная архитектура (на каждую биржу)

1. **`client.py`** — сырой REST-клиент, тонкая обёртка над HTTP. Методы возвращают `dict | list` без обработки. Докстринг содержит ссылку на документацию API.
2. **`adapter.py`** — статические методы преобразования сырых данных в унифицированные TypedDict. Декорирован `@decorate_all_methods(catch_adapter_errors)` для обработки ошибок итерации.
3. **`uni_client.py`** — унифицированный клиент, реализующий `IUniClient`. Вызывает `client` → передаёт результат в `adapter` → возвращает типизированный ответ.

### Паттерн overload в uni_client

Методы с опциональным `symbol` используют три overload'а:
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

Когда метод требует данных из двух разных endpoint'ов — они запрашиваются параллельно:
```python
mark_data, funding_data = await asyncio.gather(
    self._client.futures_mark_price(symbol=symbol),
    self._client.futures_funding_info(),
)
```

### Заглушки для нереализованных методов

```python
async def funding_info(self, symbol: str | None = None) -> FundingInfoItem | FundingInfoDict:
    raise NotImplementedError("Method will be implemented later.")
```

## Типы данных (`unicex/types.py`)

Все унифицированные ответы — `TypedDict`. Словари с тикером в качестве ключа оформляются через `type` alias:

```python
class FundingInfoItem(TypedDict):
    rate: float       # ставка фандинга в %
    interval: int     # интервал в часах
    next_time: int    # unix timestamp в мс

type FundingInfoDict = dict[str, FundingInfoItem]
```

Временны́е поля всегда в **миллисекундах** (`int`). Ставки фандинга — в **процентах** (умножены на 100 из долей).

## Стиль докстрингов

**Унифицированный клиент / публичные методы:**
```python
"""Описание.

Параметры:
    symbol (`str | None`): Название тикера (Опционально).

Возвращает:
    `FundingInfoItem | FundingInfoDict`: Описание возвращаемого значения.
"""
```

**Сырой клиент (`client.py`):**
```python
"""Описание метода.

https://docs.exchange.com/api/endpoint
"""
```

**Приватный метод (начинается с `_`):**
```python
"""Краткое описание."""
```

## Что НЕ делать

- Не добавлять новые методы в `IUniClient` без реализации заглушек во всех 10 биржах.
- Не забывать добавлять новые типы в `__all__` в `types.py`.
- Не использовать `asyncio.sleep()` или синхронные вызовы внутри async-методов.
- Не менять возвращаемый тип `int` на `int | None` в TypedDict — биржи без поддержки должны кидать `NotImplementedError`, а не возвращать `None`.
- После добавления нового метода обновить счётчики в `README.md` (колонка `UniClient (N)`).
