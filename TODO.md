** Пофиксить: **
- Способы авторизации слишком сильно отличаются на каждой бирже
- Какая то путаница в OCO ордерах на бинансе: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/trading-endpoints#new-order-list---oco-trade
- На Hyperliquid неправильно работает лимит (добавляет + 1 свечу при запросе свечей через UniClient)
- bingx adapter отрефакторить

** Сделано: **
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
