# Unified Crypto Exchange API

| Exchange | Adapter | Client | AioClient | UniClient | WebsocketManager | UniWebsocketManager | AioWebsocketManager | UniAioWebsocketManager |
|----------|---------|--------|-----------|------------|------------------|---------------------|---------------------|------------------------|
| Binance  | [х]     | [x]    | [x]       | [x]        | [x]              | [x]                 | [ ]                 | [ ]                    |
| Bybit    | [ ]     | [ ]    | [ ]       | [ ]        | [ ]              | [ ]                 | [ ]                 | [ ]                    |
| Bitget   | [ ]     | [ ]    | [ ]       | [ ]        | [ ]              | [ ]                 | [ ]                 | [ ]                    |
| Okx      | [ ]     | [ ]    | [ ]       | [ ]        | [ ]              | [ ]                 | [ ]                 | [ ]                    |
| Mexc     | [ ]     | [ ]    | [ ]       | [ ]        | [ ]              | [ ]                 | [ ]                 | [ ]                    |
| Gate     | [ ]     | [ ]    | [ ]       | [ ]        | [ ]              | [ ]                 | [ ]                 | [ ]                    |

# ❗️ Project troubles:
- Спот вебсокет на бинансе может отключиться и не переподключиться, потому что renew_listen_key не дает информации о том, когда ключ просрочен.

# 📋 Todo
+ Добавить открытый интерес в клиента
+ Отрефакторить sync user websocket binance
- Добавить веса и рейт лимиты в документацию клиентов
- Привести в порядок обработку ответа после запроса


# 📋 Todo 22 september
- Добавить multiplex socket
- Доделать интерфейс IUniWebsocketManager
- Перепроверить все докстринги
- Разобраться с логированием
+ Названия классов в докстрингах
+ Доделать no_message_reconnect_timeout
+ Доделать Async User Webosocket Binance
