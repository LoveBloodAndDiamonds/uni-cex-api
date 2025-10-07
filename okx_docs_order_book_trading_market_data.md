## Market Data {#order-book-trading-market-data}

The API endpoints of `Market Data` do not require authentication.\
There are multiple services for market data, and each service has an
independent cache. A random service will be requested for every request.
So for two requests, it's expected that the data obtained in the second
request is earlier than the first request.

### GET / Tickers {#order-book-trading-market-data-get-tickers}

Retrieve the latest price snapshot, best bid/ask price, and trading
volume in the last 24 hours. Best ask price may be lower than the best
bid price during the pre-open period.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-tickers-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-tickers-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-tickers-http-request}

`GET /api/v5/market/tickers`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/tickers?instType=SWAP
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours
result = marketDataAPI.get_tickers(
    instType="SWAP"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-tickers-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            Yes               Instrument type\
                                                        `SPOT`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
     {
        "instType":"SWAP",
        "instId":"LTC-USD-SWAP",
        "last":"9999.99",
        "lastSz":"1",
        "askPx":"9999.99",
        "askSz":"11",
        "bidPx":"8888.88",
        "bidSz":"5",
        "open24h":"9000",
        "high24h":"10000",
        "low24h":"8888.88",
        "volCcy24h":"2222",
        "vol24h":"2222",
        "sodUtc0":"0.1",
        "sodUtc8":"0.1",
        "ts":"1597026383085"
     },
     {
        "instType":"SWAP",
        "instId":"BTC-USD-SWAP",
        "last":"9999.99",
        "lastSz":"1",
        "askPx":"9999.99",
        "askSz":"11",
        "bidPx":"8888.88",
        "bidSz":"5",
        "open24h":"9000",
        "high24h":"10000",
        "low24h":"8888.88",
        "volCcy24h":"2222",
        "vol24h":"2222",
        "sodUtc0":"0.1",
        "sodUtc8":"0.1",
        "ts":"1597026383085"
    }
  ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-tickers-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  last                    String                  Last traded price

  lastSz                  String                  Last traded size. 0
                                                  represents there is no
                                                  trading volume

  askPx                   String                  Best ask price

  askSz                   String                  Best ask size

  bidPx                   String                  Best bid price

  bidSz                   String                  Best bid size

  open24h                 String                  Open price in the past
                                                  24 hours

  high24h                 String                  Highest price in the
                                                  past 24 hours

  low24h                  String                  Lowest price in the
                                                  past 24 hours

  volCcy24h               String                  24h trading volume,
                                                  with a unit of
                                                  `currency`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of base currency. e.g.
                                                  the unit is BTC for
                                                  BTC-USD-SWAP and
                                                  BTC-USDT-SWAP\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in quote currency.

  vol24h                  String                  24h trading volume,
                                                  with a unit of
                                                  `contract`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of contracts.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in base currency.

  sodUtc0                 String                  Open price in the UTC 0

  sodUtc8                 String                  Open price in the UTC 8

  ts                      String                  Ticker data generation
                                                  time, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`
  -----------------------------------------------------------------------

### GET / Ticker {#order-book-trading-market-data-get-ticker}

Retrieve the latest price snapshot, best bid/ask price, and trading
volume in the last 24 hours. Best ask price may be lower than the best
bid price during the pre-open period.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-ticker-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-ticker-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-ticker-http-request}

`GET /api/v5/market/ticker`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/ticker?instId=BTC-USD-SWAP
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours
result = marketDataAPI.get_ticker(
    instId="BTC-USD-SWAP"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-ticker-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ------------------------------------
  instId      String   Yes        Instrument ID, e.g. `BTC-USD-SWAP`

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
     {
        "instType":"SWAP",
        "instId":"BTC-USD-SWAP",
        "last":"9999.99",
        "lastSz":"0.1",
        "askPx":"9999.99",
        "askSz":"11",
        "bidPx":"8888.88",
        "bidSz":"5",
        "open24h":"9000",
        "high24h":"10000",
        "low24h":"8888.88",
        "volCcy24h":"2222",
        "vol24h":"2222",
        "sodUtc0":"2222",
        "sodUtc8":"2222",
        "ts":"1597026383085"
    }
  ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-ticker-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  last                    String                  Last traded price

  lastSz                  String                  Last traded size. 0
                                                  represents there is no
                                                  trading volume

  askPx                   String                  Best ask price

  askSz                   String                  Best ask size

  bidPx                   String                  Best bid price

  bidSz                   String                  Best bid size

  open24h                 String                  Open price in the past
                                                  24 hours

  high24h                 String                  Highest price in the
                                                  past 24 hours

  low24h                  String                  Lowest price in the
                                                  past 24 hours

  volCcy24h               String                  24h trading volume,
                                                  with a unit of
                                                  `currency`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of base currency.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in quote currency.

  vol24h                  String                  24h trading volume,
                                                  with a unit of
                                                  `contract`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of contracts.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in base currency.

  sodUtc0                 String                  Open price in the UTC 0

  sodUtc8                 String                  Open price in the UTC 8

  ts                      String                  Ticker data generation
                                                  time, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`.
  -----------------------------------------------------------------------

### GET / Order book {#order-book-trading-market-data-get-order-book}

Retrieve order book of the instrument. The data will be updated once
every 50 milliseconds. Best ask price may be lower than the best bid
price during the pre-open period.\
This endpoint does not return data immediately. Instead, it returns the
latest data once the server-side cache has been updated.

#### Rate Limit: 40 requests per 2 seconds {#order-book-trading-market-data-get-order-book-rate-limit-40-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-order-book-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-order-book-http-request}

`GET /api/v5/market/books`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/books?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve order book of the instrument
result = marketDataAPI.get_orderbook(
    instId="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-order-book-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`

  sz                String            No                Order book depth
                                                        per side. Maximum
                                                        400, e.g. 400
                                                        bids + 400 asks\
                                                        Default returns
                                                        to `1` depth data
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "asks": [
                [
                    "41006.8",
                    "0.60038921",
                    "0",
                    "1"
                ]
            ],
            "bids": [
                [
                    "41006.3",
                    "0.30178218",
                    "0",
                    "2"
                ]
            ],
            "ts": "1629966436396"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-order-book-response-parameters}

  **Parameter**   **Type**          **Description**
  --------------- ----------------- ----------------------------
  asks            Array of Arrays   Order book on sell side
  bids            Array of Arrays   Order book on buy side
  ts              String            Order book generation time

An example of the array of asks and bids values: \[\"411.8\", \"10\",
\"0\", \"4\"\]\
- \"411.8\" is the depth price\
- \"10\" is the quantity at the price (number of contracts for
derivatives, quantity in base currency for Spot and Spot Margin)\
- \"0\" is part of a deprecated feature and it is always \"0\"\
- \"4\" is the number of orders at the price.\

The order book data will be updated around once a second during the call
auction.

### GET / Full order book {#order-book-trading-market-data-get-full-order-book}

Retrieve order book of the instrument. The data will be updated once a
second. Best ask price may be lower than the best bid price during the
pre-open period.\
This endpoint does not return data immediately. Instead, it returns the
latest data once the server-side cache has been updated.

#### Rate Limit: 10 requests per 2 seconds {#order-book-trading-market-data-get-full-order-book-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-full-order-book-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-full-order-book-http-request}

`GET /api/v5/market/books-full`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/books-full?instId=BTC-USDT&sz=1
```
:::

#### Request Parameters {#order-book-trading-market-data-get-full-order-book-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`

  sz                String            No                Order book depth
                                                        per side. Maximum
                                                        5000, e.g. 5000
                                                        bids + 5000 asks\
                                                        Default returns
                                                        to `1` depth
                                                        data.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "asks": [
                [
                    "41006.8",
                    "0.60038921",
                    "1"
                ]
            ],
            "bids": [
                [
                    "41006.3",
                    "0.30178218",
                    "2"
                ]
            ],
            "ts": "1629966436396"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-full-order-book-response-parameters}

  **Parameter**   **Type**          **Description**
  --------------- ----------------- ----------------------------
  asks            Array of Arrays   Order book on sell side
  bids            Array of Arrays   Order book on buy side
  ts              String            Order book generation time

An example of the array of asks and bids values: \[\"411.8\", \"10\",
\"4\"\]\
- \"411.8\" is the depth price\
- \"10\" is the quantity at the price (number of contracts for
derivatives, quantity in base currency for Spot and Spot Margin)\
- \"4\" is the number of orders at the price.\

The order book data will be updated around once a second during the call
auction.

### GET / Candlesticks {#order-book-trading-market-data-get-candlesticks}

Retrieve the candlestick charts. This endpoint can retrieve the latest
1,440 data entries. Charts are returned in groups based on the requested
bar.

#### Rate Limit: 40 requests per 2 seconds {#order-book-trading-market-data-get-candlesticks-rate-limit-40-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-candlesticks-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-candlesticks-http-request}

`GET /api/v5/market/candles`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/candles?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the candlestick charts
result = marketDataAPI.get_candlesticks(
    instId="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-candlesticks-request-parameters}

  ------------------------------------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ------------------------------------------------------
  instId            String            Yes               Instrument ID, e.g. `BTC-USDT`

  bar               String            No                Bar size, the default is `1m`\
                                                        e.g. \[1m/3m/5m/15m/30m/1H/2H/4H\]\
                                                        UTC+8 opening price k-line:
                                                        \[6H/12H/1D/2D/3D/1W/1M/3M\]\
                                                        UTC+0 opening price k-line:
                                                        \[6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc\]

  after             String            No                Pagination of data to return records earlier than the
                                                        requested `ts`

  before            String            No                Pagination of data to return records newer than the
                                                        requested `ts`. The latest data will be returned when
                                                        using `before` individually

  limit             String            No                Number of results per request. The maximum is `300`.
                                                        The default is `100`.
  ------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
     [
        "1597026383085",
        "3.721",
        "3.743",
        "3.677",
        "3.708",
        "8422410",
        "22698348.04828491",
        "12698348.04828491",
        "0"
    ],
    [
        "1597026383085",
        "3.731",
        "3.799",
        "3.494",
        "3.72",
        "24912403",
        "67632347.24399722",
        "37632347.24399722",
        "1"
    ]
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-candlesticks-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  ts                      String                  Opening time of the
                                                  candlestick, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  o                       String                  Open price

  h                       String                  highest price

  l                       String                  Lowest price

  c                       String                  Close price

  vol                     String                  Trading volume, with a
                                                  unit of `contract`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of contracts.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in base currency.

  volCcy                  String                  Trading volume, with a
                                                  unit of `currency`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of base currency.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in quote currency.

  volCcyQuote             String                  Trading volume, the
                                                  value is the quantity
                                                  in quote currency\
                                                  e.g. The unit is USDT
                                                  for BTC-USDT and
                                                  BTC-USDT-SWAP;\
                                                  The unit is USD for
                                                  BTC-USD-SWAP

  confirm                 String                  The state of
                                                  candlesticks.\
                                                  `0`: K line is
                                                  uncompleted\
                                                  `1`: K line is
                                                  completed
  -----------------------------------------------------------------------

The first candlestick data may be incomplete, and should not be polled
repeatedly.

The data returned will be arranged in an array like this:
\[ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm\].

For the current cycle of k-line data, when there is no transaction, the
opening high and closing low default take the closing price of the
previous cycle.

### GET / Candlesticks history {#order-book-trading-market-data-get-candlesticks-history}

Retrieve history candlestick charts from recent years(It is last 3
months supported for 1s candlestick).

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-candlesticks-history-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-candlesticks-history-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-candlesticks-history-http-request}

`GET /api/v5/market/history-candles`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/history-candles?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve history candlestick charts from recent years
result = marketDataAPI.get_history_candlesticks(
    instId="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-candlesticks-history-request-parameters}

  ------------------------------------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ------------------------------------------------------
  instId            String            Yes               Instrument ID, e.g. `BTC-USDT`

  after             String            No                Pagination of data to return records earlier than the
                                                        requested `ts`

  before            String            No                Pagination of data to return records newer than the
                                                        requested `ts`. The latest data will be returned when
                                                        using `before` individually

  bar               String            No                Bar size, the default is `1m`\
                                                        e.g. \[1s/1m/3m/5m/15m/30m/1H/2H/4H\]\
                                                        UTC+8 opening price k-line:
                                                        \[6H/12H/1D/2D/3D/1W/1M/3M\]\
                                                        UTC+0 opening price k-line:
                                                        \[6Hutc/12Hutc/1Dutc/2Dutc/3Dutc/1Wutc/1Mutc/3Mutc\]

  limit             String            No                Number of results per request. The maximum is `300`.
                                                        The default is `100`.
  ------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
     [
        "1597026383085",
        "3.721",
        "3.743",
        "3.677",
        "3.708",
        "8422410",
        "22698348.04828491",
        "12698348.04828491",
        "1"
    ],
    [
        "1597026383085",
        "3.731",
        "3.799",
        "3.494",
        "3.72",
        "24912403",
        "67632347.24399722",
        "37632347.24399722",
        "1"
    ]
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-candlesticks-history-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  ts                      String                  Opening time of the
                                                  candlestick, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  o                       String                  Open price

  h                       String                  Highest price

  l                       String                  Lowest price

  c                       String                  Close price

  vol                     String                  Trading volume, with a
                                                  unit of `contract`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of contracts.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in base currency.

  volCcy                  String                  Trading volume, with a
                                                  unit of `currency`.\
                                                  If it is a
                                                  `derivatives` contract,
                                                  the value is the number
                                                  of base currency.\
                                                  If it is
                                                  `SPOT`/`MARGIN`, the
                                                  value is the quantity
                                                  in quote currency.

  volCcyQuote             String                  Trading volume, the
                                                  value is the quantity
                                                  in quote currency\
                                                  e.g. The unit is USDT
                                                  for BTC-USDT and
                                                  BTC-USDT-SWAP;\
                                                  The unit is USD for
                                                  BTC-USD-SWAP

  confirm                 String                  The state of
                                                  candlesticks\
                                                  `0`: K line is
                                                  uncompleted\
                                                  `1`: K line is
                                                  completed
  -----------------------------------------------------------------------

The data returned will be arranged in an array like this:
\[ts,o,h,l,c,vol,volCcy,volCcyQuote,confirm\]

1s candle is not supported by OPTION, but it is supported by other
business lines (SPOT, MARGIN, FUTURES and SWAP)

### GET / Trades {#order-book-trading-market-data-get-trades}

Retrieve the recent transactions of an instrument.

#### Rate Limit: 100 requests per 2 seconds {#order-book-trading-market-data-get-trades-rate-limit-100-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-trades-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-trades-http-request}

`GET /api/v5/market/trades`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/trades?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the recent transactions of an instrument
result = marketDataAPI.get_trades(
    instId="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-trades-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ---------------------------------------------------------------------------
  instId      String   Yes        Instrument ID, e.g. `BTC-USDT`
  limit       String   No         Number of results per request. The maximum is `500`; The default is `100`

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "source": "0",
            "px": "29963.2",
            "tradeId": "242720720",
            "ts": "1654161646974"
        },
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "source": "0",
            "px": "29964.1",
            "tradeId": "242720719",
            "ts": "1654161641568"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-trades-response-parameters}

  ----------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ----------------------------
  instId                  String                  Instrument ID

  tradeId                 String                  Trade ID

  px                      String                  Trade price

  sz                      String                  Trade quantity\
                                                  For spot trading, the unit
                                                  is base currency\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  the unit is contract.

  side                    String                  Trade side of taker\
                                                  `buy`\
                                                  `sell`

  source                  String                  Order source\
                                                  `0`: normal

  ts                      String                  Trade time, Unix timestamp
                                                  format in milliseconds, e.g.
                                                  `1597026383085`.
  ----------------------------------------------------------------------------

Up to 500 most recent historical public transaction data can be
retrieved.

### GET / Trades history {#order-book-trading-market-data-get-trades-history}

Retrieve the recent transactions of an instrument from the last 3 months
with pagination.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-trades-history-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-trades-history-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-trades-history-http-request}

`GET /api/v5/market/history-trades`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/history-trades?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve the recent transactions of an instrument from the last 3 months with pagination
result = marketDataAPI.get_history_trades(
    instId="BTC-USD-SWAP"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-market-data-get-trades-history-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`

  type              String            No                Pagination Type\
                                                        `1`: tradeId `2`:
                                                        timestamp\
                                                        The default is
                                                        `1`

  after             String            No                Pagination of
                                                        data to return
                                                        records earlier
                                                        than the
                                                        requested tradeId
                                                        or ts.

  before            String            No                Pagination of
                                                        data to return
                                                        records newer
                                                        than the
                                                        requested
                                                        tradeId.\
                                                        Do not support
                                                        timestamp for
                                                        pagination. The
                                                        latest data will
                                                        be returned when
                                                        using `before`
                                                        individually

  limit             String            No                Number of results
                                                        per request. The
                                                        maximum and
                                                        default both are
                                                        `100`
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "source": "0",
            "px": "29963.2",
            "tradeId": "242720720",
            "ts": "1654161646974"
        },
        {
            "instId": "BTC-USDT",
            "side": "sell",
            "sz": "0.00001",
            "source": "0",
            "px": "29964.1",
            "tradeId": "242720719",
            "ts": "1654161641568"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-trades-history-response-parameters}

  ----------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ----------------------------
  instId                  String                  Instrument ID

  tradeId                 String                  Trade ID

  px                      String                  Trade price

  sz                      String                  Trade quantity\
                                                  For spot trading, the unit
                                                  is base currency\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  the unit is contract.

  side                    String                  Trade side of taker\
                                                  `buy`\
                                                  `sell`

  source                  String                  Order source\
                                                  `0`: normal

  ts                      String                  Trade time, Unix timestamp
                                                  format in milliseconds, e.g.
                                                  `1597026383085`.
  ----------------------------------------------------------------------------

### GET / Option trades by instrument family {#order-book-trading-market-data-get-option-trades-by-instrument-family}

Retrieve the recent transactions of an instrument under same instFamily.
The maximum is 100.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-option-trades-by-instrument-family-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-option-trades-by-instrument-family-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-option-trades-by-instrument-family-http-request}

`GET /api/v5/market/option/instrument-family-trades`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/option/instrument-family-trades?instFamily=BTC-USD
```
:::

#### Request Parameters {#order-book-trading-market-data-get-option-trades-by-instrument-family-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instFamily        String            Yes               Instrument
                                                        family, e.g.
                                                        BTC-USD\
                                                        Applicable to
                                                        `OPTION`

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "vol24h": "103381",
            "tradeInfo": [
                {
                    "instId": "BTC-USD-221111-17750-C",
                    "side": "sell",
                    "sz": "1",
                    "px": "0.0075",
                    "tradeId": "20",
                    "ts": "1668090715058"
                },
                {
                    "instId": "BTC-USD-221111-17750-C",
                    "side": "sell",
                    "sz": "91",
                    "px": "0.01",
                    "tradeId": "19",
                    "ts": "1668090421062"
                }
            ],
            "optType": "C"
        },
        {
            "vol24h": "144499",
            "tradeInfo": [
                {
                    "instId": "BTC-USD-230127-10000-P",
                    "side": "sell",
                    "sz": "82",
                    "px": "0.019",
                    "tradeId": "23",
                    "ts": "1668090967057"
                },
                {
                    "instId": "BTC-USD-221111-16250-P",
                    "side": "sell",
                    "sz": "102",
                    "px": "0.0045",
                    "tradeId": "24",
                    "ts": "1668090885050"
                }
            ],
            "optType": "P"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-option-trades-by-instrument-family-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  vol24h                  String                  24h trading volume,
                                                  with a unit of
                                                  contract.

  optType                 String                  Option type, C: Call P:
                                                  Put

  tradeInfo               Array of objects        The list trade data

  \> instId               String                  The Instrument ID

  \> tradeId              String                  Trade ID

  \> px                   String                  Trade price

  \> sz                   String                  Trade quantity. The
                                                  unit is contract.

  \> side                 String                  Trade side\
                                                  `buy`\
                                                  `sell`

  \> ts                   String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  1597026383085.
  -----------------------------------------------------------------------

### GET / Option trades {#order-book-trading-market-data-get-option-trades}

The maximum is 100.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-option-trades-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-option-trades-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-option-trades-http-request}

`GET /api/v5/public/option-trades`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/public/option-trades?instFamily=BTC-USD
```
:::

#### Request Parameters {#order-book-trading-market-data-get-option-trades-request-parameters}

  Parameter    Type     Required      Description
  ------------ -------- ------------- ------------------------------------------------------------------------------------------------------------------------------------
  instId       String   Conditional   Instrument ID, e.g. BTC-USD-221230-4000-C, Either `instId` or `instFamily` is required. If both are passed, `instId` will be used.
  instFamily   String   Conditional   Instrument family, e.g. BTC-USD
  optType      String   No            Option type, `C`: Call `P`: put

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "fillVol": "0.24415013671875",
            "fwdPx": "16676.907614127158",
            "idxPx": "16667",
            "instFamily": "BTC-USD",
            "instId": "BTC-USD-221230-16600-P",
            "markPx": "0.006308943261227884",
            "optType": "P",
            "px": "0.005",
            "side": "sell",
            "sz": "30",
            "tradeId": "65",
            "ts": "1672225112048"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-option-trades-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instId                  String                  Instrument ID

  instFamily              String                  Instrument family

  tradeId                 String                  Trade ID

  px                      String                  Trade price

  \> sz                   String                  Trade quantity. The
                                                  unit is contract.

  side                    String                  Trade side\
                                                  `buy`\
                                                  `sell`

  optType                 String                  Option type, C: Call P:
                                                  Put

  fillVol                 String                  Implied volatility
                                                  while trading
                                                  (Correspond to trade
                                                  price)

  fwdPx                   String                  Forward price while
                                                  trading

  idxPx                   String                  Index price while
                                                  trading

  markPx                  String                  Mark price while
                                                  trading

  ts                      String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`.
  -----------------------------------------------------------------------

### GET / 24H total volume {#order-book-trading-market-data-get-24h-total-volume}

The 24-hour trading volume is calculated on a rolling basis.

#### Rate Limit: 2 requests per 2 seconds {#order-book-trading-market-data-get-24h-total-volume-rate-limit-2-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-24h-total-volume-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-24h-total-volume-http-request}

`GET /api/v5/market/platform-24-volume`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/platform-24-volume
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.MarketData as MarketData

flag = "0"  # Production trading:0 , demo trading:1

marketDataAPI =  MarketData.MarketAPI(flag=flag)

# Retrieve 24 total volume
result = marketDataAPI.get_volume()
print(result)
```
:::

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
     {
         "volCny": "230900886396766",
         "volUsd": "34462818865189",
         "ts": "1657856040389"
     }
  ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-24h-total-volume-response-parameters}

  **Parameter**   **Type**   **Description**
  --------------- ---------- -------------------------------------------------------------------------------
  volUsd          String     24-hour total trading volume from the order book trading in \"USD\"
  volCny          String     24-hour total trading volume from the order book trading in \"CNY\"
  ts              String     Data return time, Unix timestamp format in milliseconds, e.g. `1597026383085`

### GET / Call auction details {#order-book-trading-market-data-get-call-auction-details}

Retrieve call auction details.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-market-data-get-call-auction-details-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: IP {#order-book-trading-market-data-get-call-auction-details-rate-limit-rule-ip}

#### HTTP Request {#order-book-trading-market-data-get-call-auction-details-http-request}

`GET /api/v5/market/call-auction-details`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/market/call-auction-details?instId=ONDO-USDC
```
:::

#### Request Parameters {#order-book-trading-market-data-get-call-auction-details-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- --------------------------------
  instId      String   Yes        Instrument ID, e.g. `BTC-USDT`

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "instId": "ONDO-USDC",
            "unmatchedSz": "9988764",
            "eqPx": "0.6",
            "matchedSz": "44978",
            "state": "continuous_trading",
            "auctionEndTime": "1726542000000",
            "ts": "1726542000007"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-market-data-get-call-auction-details-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  instId                  String                  Instrument ID

  eqPx                    String                  Equilibrium price

  matchedSz               String                  Matched size for both
                                                  buy and sell\
                                                  The unit is in base
                                                  currency

  unmatchedSz             String                  Unmatched size

  auctionEndTime          String                  Call auction end time.
                                                  Unix timestamp in
                                                  milliseconds.

  state                   String                  Trading state of the
                                                  symbol\
                                                  `call_auction`\
                                                  `continuous_trading`

  ts                      String                  Data generation time.
                                                  Unix timestamp in
                                                  millieseconds.
  -----------------------------------------------------------------------

During call auction, users can get the updates of equilibrium price,
matched size, unmatched size, and auction end time. The data will be
updated around once a second. The endpoint returns the actual open
price, matched size, and unmatched size when the call auction ends.\
For symbols that never go through call auction, the endpoint will also
return results but with state always as \`continuous_trading\` and other
fields as 0 or empty.
