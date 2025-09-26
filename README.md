# Unified Crypto Exchange API

`unicex` - библиотека для работы с криптовалютными биржами, реализующая унифицированный интерфейс для работы с различными криптовалютными биржами.

## ✅ Статус реализации:

**Sync:**
| Exchange | Client | UniClient | Adapter | WebsocketManager | UniWebsocketManager | UserWebsocket |
|----------|--------|-----------|---------|------------------|---------------------|---------------|
| Binance  | [x]    | [x]       | [x]     | [x]              | [x]                 | [x]           |
| Bybit    | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Bitget   | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Okx      | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Mexc     | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Gate     | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |

**Async:**
| Exchange | Client | UniClient | Adapter | WebsocketManager | UniWebsocketManager | UserWebsocket |
|----------|--------|-----------|---------|------------------|---------------------|---------------|
| Binance  | [x]    | [x]       | [x]     | [x]              | [x]                 | [x]           |
| Bybit    | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Bitget   | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Okx      | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Mexc     | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |
| Gate     | [ ]    | [ ]       | [ ]     | [ ]              | [ ]                 | [ ]           |

---

## Блок для разработчика:

### 📋 Todo
- Добавить веса и рейт лимиты в документацию клиентов
- Пересмотреть вопрос: должен ли быть адаптер интерфейсом?
- Прокидывать ошибку дальше: 2025-09-24 13:08:06.552 | ERROR    | unicex._base.sync.websocket:_on_error:212 - Websocket error: Message queue is overflow
- Доделать BitgetClient
- Проверить типы BitgetClient
```
2025-09-24 13:14:03.812 | ERROR    | unicex._base.sync.websocket:_on_error:212 - Websocket error: Message queue is overflow
2025-09-24 13:14:03.812 | INFO     | unicex._base.sync.websocket:stop:121 - Stopping websocket
2025-09-24 13:14:04.291 | ERROR    | unicex._base.sync.websocket:stop:144 - Error stopping websocket thread: cannot join current thread
2025-09-24 13:14:09.294 | INFO     | unicex._base.sync.websocket:start:87 - Starting websocket
2025-09-24 13:14:09.295 | ERROR    | unicex._base.sync.websocket:_on_error:212 - Websocket error: 'NoneType' object has no attribute 'pending'
2025-09-24 13:14:09.296 | INFO     | unicex._base.sync.websocket:stop:121 - Stopping websocket
2025-09-24 13:14:10.544 | INFO     | unicex._base.sync.websocket:_on_open:187 - Websocket opened
2025-09-24 13:14:10.544 | ERROR    | unicex._base.sync.websocket:_on_error:212 - Websocket error: 'NoneType' object has no attribute 'sock'
2025-09-24 13:14:10.544 | INFO     | unicex._base.sync.websocket:stop:121 - Stopping websocket
2025-09-24 13:14:10.545 | ERROR    | unicex._base.sync.websocket:stop:144 - Error stopping websocket thread: cannot join current thread
```

### 📋 Todo 24 september
- Написать 1-2 examples
- Написать октрытый интерес на бинанс uni


### 📋 Todo 26 september
+ Убрали Literal's, добавили str в сигнатуры методов
+ Привести в порядок обработку ответа после запроса
+ Добавить генерацию ссылок в extra
+ Пересмотреть политику Literal в types
+ Потестить bitget
+ Может быть uni socket manager будет принимать тип рынка?
+ AdapterError можно сделать красивее и удобнее
+ Добавить дефолтный overload для uniclient uniwebsoccketmanager
+ Добавить ссылку на доку во все вебсокет менеджер эндпоинты
- Добавить overload ко всем методам где None,None
- Определить в каком порядке возвращать значения из адаптера (это касается всех методов)
