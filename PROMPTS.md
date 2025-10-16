# REST API

Цель: сгенерировать корректную реализацию метода(ов) в `unicex/<exchange>/client.py` строго в стиле проекта и существующих методов файла, на основе ссылки на документацию Bybit и распарсенной HTML‑страницы конкретного эндпоинта.

Что я передаю модели как вход:
- `docs_url`: ссылка на страницу документации Bybit конкретного эндпоинта.
- `endpoint_html`: распарсенная HTML‑страница (текст) этой документации, содержащая описание HTTP‑метода, пути, списка параметров, требований к подписи и формату ответа.
- опционально: целевое имя метода, если оно заранее выбрано.

Контекст кода (важно для стиля):
- Файл: `unicex/<exchange>/client.py`.
- Все публичные методы клиента — асинхронные (`async def`) и возвращают `dict`.
- Параметры метода объявляются в `snake_case`. При формировании `params` ключи приводятся к требуемому API формату (часто `camelCase`). Значения `None` должны отфильтровываться через `filter_params` — это уже реализовано внутри `_make_request` файла, поэтому достаточно передавать словарь `params` с возможными `None`.
- Для публичных эндпоинтов используется `await self._make_request(method, url, params=params)`.
- Для приватных эндпоинтов обязательно `signed=True`: `await self._make_request(method, url, params=params, signed=True)`. Внутри клиента уже реализованы заголовки и подпись (`_get_headers`, `_generate_signature`). Для `POST` параметры уходят в `body`, для `GET` — в `query params` (это также уже реализовано внутри `_make_request`).
- Базовый URL: `self._BASE_URL` (например, `self._BASE_URL + "/v5/market/kline"`).
- Докстринги для публичных методов: краткое русскоязычное описание + пустая строка + ссылка на документацию. Для приватных (`_...`) — однострочный докстринг без ссылки. Пример см. ниже.

Требования к результату (строго):
- Одна или несколько готовых к вставке реализаций методов внутри класса `Client` в `unicex/<exchange>/client.py`.
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
      """Проверка соединения с REST API.

      https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#test-connectivity
      """
      return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ping")
  ```

- Публичный GET с параметрами:
  ```python
  async def exchange_info(
      self,
      symbol: str | None = None,
      symbols: list[str] | None = None,
  ) -> dict:
      """Получение торговых правил биржи и информации о символах.

      https://www.mexc.com/api-docs/spot-v3/market-data-endpoints#exchange-information
      """
      params = {
          "symbol": symbol,
          "symbols": symbols,
      }

      return await self._make_request(
          "GET", self._BASE_SPOT_URL + "/api/v3/exchangeInfo", params=params
      )
  ```

- Приватный POST (пример структуры; путь/поля заменить по докам):
  ```python
  async def create_order(
      self,
      symbol: str,
      side: str,
      type: str,
      quantity: str | None = None,
      quote_order_quantity: str | None = None,
      price: str | None = None,
      new_client_order_id: str | None = None,
      stp_mode: str | None = None,
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
      }

      return await self._make_request(
          "POST", self._BASE_SPOT_URL + "/api/v3/order", params=params, signed=True
      )
  ```

Формат ожидаемого ответа от модели:
- Добавь только готовый код методов в класс `Client` в файле `unicex/<exchange>/client.py`.
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

Готово — после вставки в `unicex/<exchange>/client.py` код должен выглядеть и вести себя идентично существующим методам по стилю и способу вызова `_make_request`.


# WEBSOCKET API

Цель: сгенерировать корректную реализацию метода(ов) в `unicex/<exchange>/websocket_manager.py` строго в стиле проекта и существующих методов файла, на основе ссылки на документацию биржи и распарсенной HTML‑страницы конкретного WebSocket канала.

Что я передаю модели как вход:
- `docs_url`: ссылка на страницу документации биржи конкретного WebSocket канала.
- `endpoint_html`: распарсенная HTML‑страница (текст) этой документации, содержащая описание канала, формата подписки, параметров и формата получаемых сообщений.
- опционально: целевое имя метода, если оно заранее выбрано.

Контекст кода (важно для стиля):
- Файл: `unicex/<exchange>/websocket_manager.py`.
- Класс `WebsocketManager` с методами создания WebSocket подключений.
- Все публичные методы возвращают `Websocket` (объект для управления соединением).
- Параметры метода объявляются в `snake_case`. При формировании subscription messages или URL ключи приводятся к требуемому API формату.
- Первый параметр метода всегда `callback: CallbackType` — асинхронная функция обратного вызова.
- Часто используются параметры `symbol: str | None = None` и `symbols: Sequence[str] | None = None` для подписки на один или несколько символов. Проверка взаимоисключения этих параметров должна быть реализована в методе или в вспомогательной функции.
- Базовые URL определены как константы класса `_BASE_URL`, `_BASE_SPOT_URL`, `_BASE_FUTURES_URL` и т.д.
- Инициализация `__init__(self, client: Client | None = None, **ws_kwargs: Any)` с сохранением клиента и WebSocket параметров.

Архитектурные паттерны (выбрать подходящий на основе документации):

**Паттерн 1: URL-based подписка (как Binance)**
- URL формируется динамически включая параметры подписки
- Подписка происходит автоматически при подключении к URL
- Используется вспомогательный метод `_generate_stream_url`
- Пример: `wss://stream.binance.com:9443/ws/btcusdt@trade`

**Паттерн 2: Message-based подписка (как Bitget)**
- Базовый URL статичный
- Подписка через отправку JSON сообщений после подключения
- Используется вспомогательный метод `_generate_subscription_message`
- Передача `subscription_messages` в конструктор `Websocket`
- Пример: `{"op": "subscribe", "args": [{"instType": "SPOT", "channel": "trade", "instId": "BTCUSDT"}]}`

Требования к структуре файла:
- Обязательные импорты:
  ```python
  __all__ = ["WebsocketManager"]

  # Для message-based: import json
  from collections.abc import Awaitable, Callable, Sequence
  from typing import Any, Literal  # Literal только если нужен

  from unicex._base import Websocket

  from .client import Client

  type CallbackType = Callable[[Any], Awaitable[None]]
  ```

- Докстринг класса: `"""Менеджер асинхронных вебсокетов для <Exchange>."""`

- Константы базовых URL как class attributes

- Метод `__init__`:
  ```python
  def __init__(self, client: Client | None = None, **ws_kwargs: Any) -> None:
      """Инициализирует менеджер вебсокетов для <Exchange>.

      Параметры:
          client (`Client | None`): Клиент для выполнения запросов. Нужен, чтобы открыть приватные вебсокеты.
          ws_kwargs (`dict[str, Any]`): Дополнительные аргументы, которые прокидываются в `Websocket`.
      """
      self.client = client
      # Для message-based может быть: self._ws_kwargs = {"ping_message": "ping", **ws_kwargs}
      # Для URL-based: self._ws_kwargs = ws_kwargs
  ```

Требования к методам WebSocket подписок:
- Имена методов в `snake_case` по назначению канала (например: `trade`, `ticker`, `klines`, `depth`, `book_ticker`).
- Возвращаемый тип: `-> Websocket`.
- Стандартные параметры:
  - `callback: CallbackType` — всегда первый параметр
  - `symbol: str | None = None` — для подписки на один символ
  - `symbols: Sequence[str] | None = None` — для подписки на несколько символов
  - дополнительные параметры специфичные для канала (интервалы, глубина и т.д.)

- Докстринг для публичных методов:
  ```python
  """Создает вебсокет для получения <описание канала>.

  <docs_url>

  Параметры:
      callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
      <дополнительные параметры>

  Возвращает:
      `Websocket`: Объект для управления вебсокет соединением.
  """
  ```

- Валидация параметров `symbol` и `symbols`:
  ```python
  if symbol and symbols:
      raise ValueError("Parameters symbol and symbols cannot be used together")
  # Дополнительно при необходимости:
  if not (symbol or symbols):
      raise ValueError("Either symbol or symbols must be provided")
  ```

**Шаблоны реализации методов:**

URL-based подписка:
```python
def trade(
    self,
    callback: CallbackType,
    symbol: str | None = None,
    symbols: Sequence[str] | None = None,
) -> Websocket:
    """Создает вебсокет для получения сделок.

    https://example.com/docs/websocket/trade

    Параметры:
        callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
        symbol (`str | None`): Один символ для подписки.
        symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

    Возвращает:
        `Websocket`: Объект для управления вебсокет соединением.
    """
    url = self._generate_stream_url(
        type="trade",  # или другой параметр канала
        url=self._BASE_URL,
        symbol=symbol,
        symbols=symbols,
        require_symbol=True,  # если символ обязателен
    )
    return Websocket(callback=callback, url=url, **self._ws_kwargs)
```

Message-based подписка:
```python
def trade(
    self,
    callback: CallbackType,
    symbol: str | None = None,
    symbols: Sequence[str] | None = None,
) -> Websocket:
    """Создает вебсокет для получения сделок.

    https://example.com/docs/websocket/trade

    Параметры:
        callback (`CallbackType`): Асинхронная функция обратного вызова для обработки сообщений.
        symbol (`str | None`): Один символ для подписки.
        symbols (`Sequence[str] | None`): Список символов для мультиплекс‑подключения.

    Возвращает:
        `Websocket`: Объект для управления вебсокет соединением.
    """
    subscription_messages = self._generate_subscription_message(
        topic="trade",  # или channel/event название
        symbol=symbol,
        symbols=symbols,
    )
    return Websocket(
        callback=callback,
        url=self._BASE_URL,
        subscription_messages=subscription_messages,
        **self._ws_kwargs,
    )
```

**Вспомогательные методы (генерируются по необходимости):**

URL-based `_generate_stream_url`:
```python
def _generate_stream_url(
    self,
    type: str,
    url: str,
    symbol: str | None = None,
    symbols: Sequence[str] | None = None,
    require_symbol: bool = False,
) -> str:
    """Генерирует URL для вебсокета. Параметры symbol и symbols не могут быть использованы вместе.

    Параметры:
        type (`str`): Тип вебсокета/канала.
        url (`str`): Базовый URL для вебсокета.
        symbol (`str | None`): Символ для подписки.
        symbols (`Sequence[str] | None`): Список символов для подписки.
        require_symbol (`bool`): Требуется ли символ для подписки.

    Возвращает:
        str: URL для вебсокета.
    """
    if symbol and symbols:
        raise ValueError("Parameters symbol and symbols cannot be used together")
    if require_symbol and not (symbol or symbols):
        raise ValueError("Either symbol or symbols must be provided")

    # Логика генерации URL по документации биржи
```

Message-based `_generate_subscription_message`:
```python
def _generate_subscription_message(
    self,
    topic: str,
    symbol: str | None = None,
    symbols: Sequence[str] | None = None,
    # дополнительные параметры специфичные для биржи
) -> list[str]:
    """Сформировать сообщение для подписки на вебсокет."""
    if symbol and symbols:
        raise ValueError("Parameters symbol and symbols cannot be used together")
    if not (symbol or symbols):
        raise ValueError("Either symbol or symbols must be provided")

    # Логика генерации subscription messages по документации биржи
    # Возвращает список JSON строк для отправки
```

Требования к результату (строго):
- Одна или несколько готовых к вставке реализаций методов внутри класса `WebsocketManager` в `unicex/<exchange>/websocket_manager.py`.
- Если нужны вспомогательные методы — добавить их тоже.
- Код должен полностью соответствовать стилю существующих методов файла и архитектурным паттернам проекта.
- Имена методов — осмысленные `snake_case`, соответствующие назначению канала.
- Аннотации типов параметров подбирать по документации:
  - символы: `str | None`
  - интервалы времени: `str` (например: "1m", "1h")
  - списки символов: `Sequence[str] | None`
  - перечислимые значения: `Literal[...]` если есть ограниченный набор
- Не добавлять новые импорты сверх необходимого, не изменять существующие приватные методы, не рефакторить код вне требуемого метода.
- Возвращать именно `Websocket` объект.

Дополнительные указания и проверки качества:
- Следи, чтобы имена параметров метода были в `snake_case`, а ключи в subscription messages или URL — в формате, ожидаемом биржей.
- Реализуй проверки взаимоисключения `symbol` и `symbols` параметров.
- Для каналов требующих символ — добавь соответствующую валидацию.
- Не меняй существующие импорты без крайней необходимости.
- Не изменяй другие части файла, кроме добавления требуемых методов.
- Соблюдай формат докстрингов проекта.

Что сделать модели, если данных из `endpoint_html` недостаточно:
- Ясно указать, какого поля/параметра/формата не хватает, и предложить разумное предположение, пометив его комментарием `# NOTE:` внутри кода метода.

Подсказки для нейминга методов:
- Читай название канала из документации: "Trade Channel" → `def trade(...)`, "Candlestick Channel" → `def candlestick(...)` или `def klines(...)`.
- Избегай префиксов по секциям, если имя и так уникально (как в существующих методах `trade`, `ticker`, `depth`).
- Для каналов с вариантами используй понятные суффиксы: `book_ticker`, `mini_ticker`, `partial_book_depth`.

Формат ожидаемого ответа от модели:
- Добавь только готовый код методов (и вспомогательных методов при необходимости) в класс `WebsocketManager` в файле `unicex/<exchange>/websocket_manager.py`.
- Если предлагается несколько методов — сгруппируй их последовательно, каждый отдельным блоком кода.

Готово — после вставки в `unicex/<exchange>/websocket_manager.py` код должен выглядеть и вести себя идентично существующим методам по стилю и способу создания `Websocket` соединений.

  # EXCHANGE INFO

  Цель: сгенерировать реализацию класса `ExchangeInfo` в `unicex/<exchange>/exchange_info.py`, которая подготавливает данные о тикерах (spot и, при наличии, futures) на основе распарсенной
  документации биржи.

  Что я передаю модели как вход:
  - `exchange_name`: название биржи (`str`), используется в логировании и строках.
  - `docs_url`: ссылка на раздел документации, откуда получены данные.
  - `exchange_docs`: структурированные данные из документации (JSON/словарь). Внутри указываю списки инструментов и их поля. Пример структуры:
    ```json
    {
      "spot": [
        {
          "symbol": "BTCUSDT",
          "price_tick": "0.1",
          "quantity_step": "0.0001",
          "contract_size": null,
          "extra": { ... }  // любые дополнительные поля, которые помогут понять формат
        }
      ],
      "futures": [
        {
          "symbol": "BTCUSDT",
          "price_tick": "0.5",
          "quantity_step": "0.001",
          "contract_size": "0.01",
          "delivery_type": "perpetual"
        }
      ]
    }

  - опционально: словарь с описанием необходимых HTTP‑эндпоинтов, если нужно обращаться к живому API (api_endpoints.spot, api_endpoints.futures и т.п.).

  Контекст кода (важно для стиля):

  - Файл: unicex/<exchange>/exchange_info.py.
  - Класс наследует IExchangeInfo и реализует _load_exchange_info.
  - Используем aiohttp.ClientSession для HTTP‑запросов, как в unicex/okx/exchange_info.py.
  - Вспомогательные методы и свойства (_tickers_info, _futures_tickers_info, _logger, _step_size_to_precision) уже реализованы в базовом классе.
  - Типы данных берём из unicex.types.

  Требования к результату (строго):

  - Вернуть полный контент файла unicex/<exchange>/exchange_info.py с готовой реализацией.
  - Объявить __all__, импорты и класс ExchangeInfo в точности как в проекте.
  - Реализовать _load_exchange_info как асинхронный метод, использующий aiohttp для получения информации из API или подготовленных данных, и заполняющий cls._tickers_info и при наличии
    cls._futures_tickers_info.
  - Для каждой записи создавать TickerInfoItem с полями:
      - tick_precision: вычисляется через cls._step_size_to_precision, если шаг — степень 10; иначе явно рассчитать количество знаков после запятой или пометить допущение # NOTE:.
      - size_precision: то же правило для шага объёма.
      - contract_size: float(...), 1, либо None, если поле отсутствует.
  - Если futures/деривативные данные не требуются или отсутствуют в документации — оставить cls._futures_tickers_info = {} и добавить понятный комментарий/лог.
  - Добавить cls._logger.debug(...) после загрузки каждого набора данных (spot/futures) с информативными сообщениями.
  - Обрабатывать сетевые ошибки: использовать response.raise_for_status() или проверку status, выбрасывая понятный RuntimeError с описанием запроса/статуса.
  - Не менять другие части проекта и не добавлять лишние зависимости.
  - Докстринги соблюдать в стиле проекта:

    """Предзагружает информацию о тикерах для биржи <Exchange>."""
    """
    """Загружает информацию о бирже."""

  Шаблон реализации (адаптируй под документацию):

  __all__ = ["ExchangeInfo"]

  import aiohttp

  from unicex._abc import IExchangeInfo
  from unicex.types import TickerInfoItem


  class ExchangeInfo(IExchangeInfo):
      """Предзагружает информацию о тикерах для биржи {exchange_name}."""

      @classmethod
      async def _load_exchange_info(cls) -> None:
          """Загружает информацию о бирже."""
          async with aiohttp.ClientSession() as session:
              tickers_info: dict[str, TickerInfoItem] = {}
              spot_url = "<spot endpoint>"
              async with session.get(spot_url) as response:
                  response.raise_for_status()
                  data = await response.json()
                  for item in <извлечение списка инструментов>:
                      price_tick = <доступ к шагу цены>
                      quantity_step = <доступ к шагу объёма>
                      tickers_info[item["symbol"]] = TickerInfoItem(
                          tick_precision=cls._step_size_to_precision(price_tick),
                          size_precision=cls._step_size_to_precision(quantity_step),
                          contract_size=None,
                      )

              cls._tickers_info = tickers_info
              cls._logger.debug("{exchange_name} spot exchange info loaded")

              futures_url = "<futures endpoint>"  # если есть
              futures_tickers_info: dict[str, TickerInfoItem] = {}
              async with session.get(futures_url) as response:
                  response.raise_for_status()
                  data = await response.json()
                  for item in <извлечение списка деривативов>:
                      futures_tickers_info[item["symbol"]] = TickerInfoItem(
                          tick_precision=cls._step_size_to_precision(<price_tick>),
                          size_precision=cls._step_size_to_precision(<quantity_step>),
                          contract_size=float(item["contractSize"]),
                      )

              cls._futures_tickers_info = futures_tickers_info
              cls._logger.debug("{exchange_name} futures exchange info loaded")

  Дополнительные указания:

  - Если документация уже содержит готовые значения precision (например, "pricePrecision": 5) — используем их напрямую вместо _step_size_to_precision.
  - При необходимости преобразовать символы (например, baseAsset + quoteAsset) — строим строку в соответствии с биржей.
  - Если найденные шаги не являются степенью десяти, попытаться вычислить precision через Decimal; при сомнениях добавить комментарий # NOTE: и чётко описать предположение.
  - Чётко отразить в коде структуру ответа, используя говорящие имена переменных.
  - Не допускать "магических" строк без пояснений — если шаги берутся из вложенных полей, оставь короткий комментарий.
  - Если документация описывает несколько типов рынков (spot, futures, options) — реализуй только те, которые присутствуют во входных данных; остальные явно проигнорируй или пометь
    комментариями.
  - В случае отсутствия данных по какой-либо секции (например, futures), не оставляй старые данные: явно присвой пустой словарь и залогируй, что данные не загружены.

  Формат ожидаемого ответа от модели:

  - Один блок кода с полным содержимым файла unicex/<exchange>/exchange_info.py.
  - Блок должен сразу быть пригоден для вставки в проект без дополнительных правок.
