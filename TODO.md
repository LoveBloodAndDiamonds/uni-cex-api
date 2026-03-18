** Пофиксить: **
- CallbackType сделать Generic
- Исправить таблицу в README.md
- убрать оверлоады, чтобы юзер мог сам на уровне своей программы вытаскивать нужный тикер, а мне не пришлось усложнять логику библиотеки (вопрос только с теми ситуациями когда без тикера никак)
- validate response to binance client
- тесты юни клиент обновить методы (список)
- Написать все to_exchange_format
- Сделать адаптер интерфейсом
- адаптер-обертка на байбит для топ- бидов и асков вроде как неверно работает (может быть проблема в RPI)
- проверить ненужные преобразования в adapter
- добавить унификацию ликвидаций
- добавить какой-то метод который вернет статусы реализаций различных направлений библиотеки
- Способы авторизации слишком сильно отличаются на каждой бирже
- Какая то путаница в OCO ордерах на бинансе: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/trading-endpoints#new-order-list---oco-trade
- bingx adapter отрефакторить
- красивое округление
- может быть deprecate Client и WebsocketManager
- self._logger = logger or _logger ничего не делает
- ключ "х" в KlineDict обрабатывать при HTTP запросах а не просто
- рефакторинг OKX Websocket Manager
- в uniwebsocketmanager можно принимать symbol: str | list[str] а не возиться с overload который усложняет чтение и поддержку кодовой базы
- Промпт “устойчивые адаптеры”**

- Для выбранной биржи найди в её адаптере все методы, где используется dict/list comprehension для обхода ответов API (пример: `ticker_24hr`, `open_interest`, `funding_rate`, `funding_interval`, `last_price`, `best_bid_ask`, `depth`).  
- Перепиши каждый comprehension в явный цикл `for item in ...:` с `try/except Exception as e:` внутри. При ошибке записывай её через `loguru.logger.error(f"Item {item} iteration {type(e)} error: {e}")` и переходи к следующему элементу, чтобы единичный мусор не ломал весь результат.  
- Не меняй формулу вычисления значений и итоговые структуры (`TickerDailyItem`, `OpenInterestItem`, `BookDepthDict` и т.п.) — только добавь безопасную обёртку.  
- Для списков, где раньше возвращали `[... for ...]`, собирай результаты в обычный список (или словарь) и возвращай его по завершении цикла.  
- В depth‑методах split bids/asks на отдельные циклы с логированием; множители контрактов, времени и т.п. оставь без изменений.

**Мини‑пример**

Было:
```python
return {
    item["symbol"]: float(item["lastPrice"])
    for item in raw_data["result"]["list"]
}
```

Стало:
```python
result = {}
for item in raw_data["result"]["list"]:
    try:
        result[item["symbol"]] = float(item["lastPrice"])
    except Exception as e:
        logger.error(f"Item {item} iteration {type(e)} error: {e}")
return result
```

Сохраняй стиль по файлу (единичные кавычки/ppi и т.д.), не добавляй новые фичи.

** Сделано: **
+ починить докстринги в aster.client
+ документацию в случаях с alias не хочется дублировать
+ добавить в README примеры extra
+ зачем нужна функция _client_cls
+ gate.client не умеет работать с :bool
+ На Hyperliquid неправильно работает лимит (добавляет + 1 свечу при запросе свечей через UniClient)
+ try except в Exchbange Info
+ проверить порядок в uni_client.futures_depth
+ добавить поддержку testnet?
+ Добавить Workflow (pypi)
+ убрать overload из uni client and uni weboskcet manager
+ start_exchanges_info должна возвращать список задач
+ aster.adapter куча лишних преобразований, когда и так все приходит float|int
+ убрать все bool из aster.client, вроде как они не поддерживаются
+ okx.exchange_info ошибка
+ mexc.adapter.futures_aggtrades - возвращает контракты
+ gate вебсокеты возвращают контракты?
+ На фьючерсах WS OKX возвращают объем в контрактах (В UniWebsocketManager 'sz' надо умножать на количество контрактов)
+ Отрефакторить Okx Websocket Manager 
+ AggTradeDict удалить 
+ Почистить тесты
+ mexc.adapter.futures_klines отрефакторить
+ gate adapter.py trades_message Отрефакторить
+ bingx: if message == "Ping": raise ValueError("Ping message received")
+ bingx: сделать что-то с recvwindow, а так же проверить ссылки на докуменьацию, адаптер в свечах проверить 
+ на KuCoin фандинг рейт работает странно, возвращает неверное значение
+ symbol_to_exchange_format скорее всего перенести в extra.py            
+ проверить ключ "u" во всех унифицированных open interest (особенно на мексе)        
+ generate_cg_link - для спота есть корректная ссылка не только для OKX и переделать под ticker
+ generate_ex_link - переделать под ticker
+ generate_tv_link - переделать под ticker
+ там где нет aggtrades возвращать trades вебсокет и наоборот
+ Как реализовать типы (quantity, price и т.д.) в сырых клиентах? str | int | float?
+ передавать ws_kwargs через uniwebsocketmanager

** Под вопросом: **
- NotSupported вместо NotImplementedError
- Возможно во всех WebsocketManager принимать symbols: list[str] а не (symbol и symbols)

** Улучшения на будущее: **
- добавить ликвидации в вебсокет юни менеджер
- добавить orderbook в вебсокет юни менеджер
- добавить min_order_size,max_order_size в ExchangeInfo
