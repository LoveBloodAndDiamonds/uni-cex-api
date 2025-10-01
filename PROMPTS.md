Цель: сгенерировать корректную реализацию метода(ов) в `unicex/bybit/client.py` строго в стиле проекта и существующих методов файла, на основе ссылки на документацию Bybit и распарсенной HTML‑страницы конкретного эндпоинта.

Что я передаю модели как вход:
- `docs_url`: ссылка на страницу документации Bybit конкретного эндпоинта.
- `endpoint_html`: распарсенная HTML‑страница (текст) этой документации, содержащая описание HTTP‑метода, пути, списка параметров, требований к подписи и формату ответа.
- опционально: целевое имя метода, если оно заранее выбрано.

Контекст кода (важно для стиля):
- Файл: `unicex/bybit/client.py`.
- Все публичные методы клиента — асинхронные (`async def`) и возвращают `dict`.
- Параметры метода объявляются в `snake_case`. При формировании `params` ключи приводятся к требуемому API формату (часто `camelCase`). Значения `None` должны отфильтровываться через `filter_params` — это уже реализовано внутри `_make_request` файла, поэтому достаточно передавать словарь `params` с возможными `None`.
- Для публичных эндпоинтов используется `await self._make_request(method, url, params=params)`.
- Для приватных эндпоинтов обязательно `signed=True`: `await self._make_request(method, url, params=params, signed=True)`. Внутри клиента уже реализованы заголовки и подпись (`_get_headers`, `_generate_signature`). Для `POST` параметры уходят в `body`, для `GET` — в `query params` (это также уже реализовано внутри `_make_request`).
- Базовый URL: `self._BASE_URL` (например, `self._BASE_URL + "/v5/market/kline"`).
- Докстринги для публичных методов: краткое русскоязычное описание + пустая строка + ссылка на документацию. Для приватных (`_...`) — однострочный докстринг без ссылки. Пример см. ниже.

Требования к результату (строго):
- Одна или несколько готовых к вставке реализаций методов внутри класса `Client` в `unicex/bybit/client.py`.
- Код должен полностью соответствовать стилю существующих методов файла (аннотации типов, форматирование, построение `url` и `params`, вызов `_make_request`).
- Имена методов — осмысленные `snake_case`, соответствующие назначению эндпоинта. Если в проекте уже есть аналогичное имя — использовать его стиль именования.
- Аннотации типов параметров подбирать по документации:
  - идентификаторы и символы: `str`;
  - временные метки и лимиты: `int | None`;
  - цены/количества и иные строковые поля Bybit: `str | None` (если по докам тип «string»);
  - перечислимые поля, если в текущем файле уже используется `Literal[...]` (например, `category: Literal["spot", "linear", "inverse"]`) — сохранять такой же подход.
- Ключи в `params` должны иметь формат, ожидаемый Bybit API (например, `base_coin` → `"baseCoin"`, `start_time` → `"startTime"`).
- Не добавлять новые импорты и внешние зависимости, не изменять существующие приватные методы, не рефакторить код вне требуемого метода.
- Возвращать именно `dict` (как у текущих методов), без дополнительных оберток и преобразований.

Шаблон для генерации одного метода:
1) Определи имя метода в `snake_case` на основе назначения эндпоинта.
2) Подбери параметры и их типы по документации. По возможности следуй паттернам из текущего файла (`ping`, `klines`).
3) Собери `url` как `self._BASE_URL + "<точный путь из доков>"`.
4) Сформируй `params` как `dict` с ключами в формате Bybit API (`camelCase`, если так в доках), а значения — из параметров метода в `snake_case`.
5) Вызови `await self._make_request("GET"|"POST", url, params=params, signed=<True|False>)` в зависимости от эндпоинта.
6) Докстринг (публичный метод):
   """
   Краткое описание на русском.

   <docs_url>
   """

Мини‑примеры в стиле проекта:
- Публичный GET без параметров:
  ```python
  async def ping(self) -> dict:
      """Проверка соединения с сервером.

      https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#test-connectivity
      """
      return await self._make_request("GET", "/api/v3/ping")
  ```

- Публичный GET с параметрами:
  ```python
  async def exchange_info(
      self,
      symbol: str | None = None,
      symbols: list[str] | None = None,
  ) -> dict:
      """Получение информации о торговых парах.

      https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#exchange-information
      """
      params = {
          "symbol": symbol,
          "symbols": symbols,
      }
      return await self._make_request("GET", "/api/v3/exchangeInfo", params=params)
  ```

- Приватный POST (пример структуры; путь/поля заменить по докам):
  ```python
  async def create_order(
      self,
      symbol: str,
      side: Literal["BUY", "SELL"],
      type: Literal["LIMIT", "MARKET"],
      quantity: float | None = None,
      quote_order_quantity: float | None = None,
      price: float | None = None,
      new_client_order_id: str | None = None,
      stp_mode: str | None = None,
      client_order_id: str | None = None,
  ) -> dict:
      """Создание нового ордера.

      https://www.mexc.com/api-docs/spot-v3/spot-account-trade#new-order
      """
      params = {
          "symbol": symbol,
          "side": side,
          "type": type,
          "quantity": quantity,
          "quoteOrderQty": quote_order_quantity,
          "price": price,
          "newClientOrderId": new_client_order_id,
          "stpMode": stp_mode,
          "newOrderRespType": client_order_id,
      }
      return await self._make_request("POST", "/api/v3/order", params=params, signed=True)
  ```

Формат ожидаемого ответа от модели:
- Добавь только готовый код методов в класс `Client` в файле `unicex/bybit/client.py`.
- Если предлагается несколько методов — сгруппируй их последовательно, каждый отдельным блоком `python`.

Дополнительные указания и проверки качества:
- Следи, чтобы имена параметров метода были в `snake_case`, а ключи в `params` — в формате, ожидаемом Bybit (чаще `camelCase`).
- Не дублируй логику фильтрации `None` и подписи запроса — это уже реализовано в `_make_request` текущего клиента.
- Для `GET`/`POST` строго следуй документации. Если эндпоинт приватный — обязательно `signed=True`.
- Не меняй существующие импорты и не добавляй новые зависимости.
- Не изменяй другие части файла, кроме добавления требуемых методов.
- Соблюдай формат докстрингов проекта.

Что сделать модели, если данных из `endpoint_html` недостаточно:
- Ясно указать, какого поля/типа/метода HTTP/пути не хватает, и предложить разумное предположение, пометив его комментарием `# NOTE:` внутри кода метода.

Подсказки для нейминга методов:
- Читай заголовок/название эндпоинта и путь: `GET /v5/market/orderbook` → `async def orderbook(...)`.
- Избегай префиксов по секциям, если имя и так уникально (как в существующих методах `ping`, `klines`).

Готово — после вставки в `unicex/bybit/client.py` код должен выглядеть и вести себя идентично существующим методам по стилю и способу вызова `_make_request`.
