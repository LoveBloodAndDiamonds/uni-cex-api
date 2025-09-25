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

## ❗️ Возможные проблемы:
- Спот вебсокет на бинансе может отключиться и не переподключиться, потому что renew_listen_key не дает информации о том, когда ключ просрочен.

---

## Блок для разработчика:

### 📋 Todo
+ Добавить открытый интерес в клиента
+ Отрефакторить sync user websocket binance
- Добавить веса и рейт лимиты в документацию клиентов
- Привести в порядок обработку ответа после запроса
- Пересмотреть вопрос: должен ли быть адаптер интерфейсом?
- Добавить генерацию ссылок в extra
- Пересмотреть политику Literal в types
- Прокидывать ошибку дальше: 2025-09-24 13:08:06.552 | ERROR    | unicex._base.sync.websocket:_on_error:212 - Websocket error: Message queue is overflow
- Потестить bitget
- AdapterError можно сделать красивее и удобнее
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
+ Разобраться с логированием
- Написать 1-2 examples
- Написать октрытый интерес на бинанс uni
