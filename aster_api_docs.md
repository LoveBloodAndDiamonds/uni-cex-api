# API documentation

**API documentation for Aster:**\
<https://github.com/asterdex/api-docs/blob/master/README.md>

### General API information

* Some endpoints will require an [API key](https://docs.asterdex.com/product/asterex-pro/api/how-to-create-api).
* The base URL for all requests is: <https://fapi.asterdex.com>
* All endpoints return data in JSON format — either as an object or an array.
* Data is returned in ascending order: oldest first, newest last.
* All time and timestamp fields are represented in milliseconds.
* Data types follow Java definitions.

#### HTTP return codes

* HTTP `4XX` return codes are used for malformed requests; the issue is on the sender's side.
* HTTP `403` return code is used when the WAF Limit (Web Application Firewall) has been violated.
* HTTP `429` return code is used when breaking a request rate limit.
* HTTP `418` return code is used when an IP has been auto-banned for continuing to send requests after receiving `429` codes.
* HTTP `5XX` return codes are used for internal errors; the issue is on Aster's side.
* HTTP `503` return code is used when the API successfully sent the message but not get a response within the timeout period.\
  It is important to **NOT** treat this as a failure operation; the execution status is **UNKNOWN** and could have been a success.

#### Error codes and messages

* Any endpoint can return an ERROR

> ***The error payload is as follows:***

```
{
  "code": -1121,
  "msg": "Invalid symbol."
}
```

* Specific error codes and messages defined [here](https://github.com/asterdex/api-docs/blob/master/aster-finance-api.md#error-codes).

#### General information on endpoints

* For `GET` endpoints, parameters must be sent as a `query string`.
* For `POST`, `PUT`, and `DELETE` endpoints, the parameters may be sent as a `query string` or in the `request body` with content type `application/x-www-form-urlencoded`. You may mix parameters between both the `query string` and `request body` if you wish to do so.
* Parameters may be sent in any order.
* If a parameter sent in both the `query string` and `request body`, the `query string` parameter will be used.

### Limits

* The `/fapi/v1/exchangeInfo` `rateLimits` array contains objects related to the exchange's `RAW_REQUEST`, `REQUEST_WEIGHT`, and `ORDER` rate limits. These are further defined in the `ENUM definitions` section under `Rate limiters (rateLimitType)`.
* A `429` will be returned when either rate limit is violated.

Aster has the right to further tighten the rate limits on users with intent to attack.

#### IP limits

* Every response includes the header `X-MBX-USED-WEIGHT-(intervalNum)(intervalLetter)`, which shows the current request weight used by your IP across all applicable rate limit intervals.
* Each route has a `weight` which determines the number of requests each endpoint counts for. Heavier endpoints and endpoints that do operations on multiple symbols will have a heavier `weight`.
* When a 429 is received, it's your obligation as an API to back off and not spam the API.
* **Repeatedly violating rate limits and/or failing to back off after receiving 429s will result in an automated IP ban (HTTP status 418).**
* IP bans are tracked and **scale in duration** for repeat offenders, **from 2 minutes to 3 days**.
* **The limits on the API are based on the IPs, not the API keys.**

We strongly recommend using WebSocket streams to retrieve data whenever possible. This ensures more timely updates and helps reduce rate limit pressure caused by frequent HTTP requests.

#### Order rate limits

* Every order response will contain a `X-MBX-ORDER-COUNT-(intervalNum)(intervalLetter)` header which has the current order count for the account for all order rate limiters defined.
* Rejected/unsuccessful orders are not guaranteed to have `X-MBX-ORDER-COUNT-**` headers in the response.
* **The order rate limit is counted against each account**.

### Endpoint security type

* Each endpoint has a security type that determines how you will interact with it.
* API keys are passed into the Rest API via the `X-MBX-APIKEY` header.
* API keys and secret keys **are case sensitive**.
* API keys can be configured to only access certain types of secure endpoints. For example, one API-key could be used for TRADE only, while another API-key can access everything except for TRADE routes.
* By default, API keys can access all secure routes.

| Security type | Description                                             |
| ------------- | ------------------------------------------------------- |
| NONE          | Endpoint can be accessed freely                         |
| TRADE         | Endpoint requires sending a valid API key and signature |
| USER\_DATA    | Endpoint requires sending a valid API key and signature |
| USER\_STREAM  | Endpoint requires sending a valid API key.              |
| MARKET\_DATA  | Endpoint requires sending a valid API key               |

* `TRADE` and `USER_DATA` endpoints are `SIGNED` endpoints

### SIGNED (TRADE and USER\_DATA) endpoint security

* `SIGNED` endpoints require an additional parameter, `signature`, to be sent in the `query string` or `request body`.
* Endpoints use `HMAC SHA256` signatures. The `HMAC SHA256 signature` is a keyed `HMAC SHA256` operation. Use your `secretKey` as the key and `totalParams` as the value for the HMAC operation.
* The `signature` is **not case sensitive**.
* Please make sure the `signature` is the end part of your `query string` or `request body`.
* `totalParams` is defined as the `query string` concatenated with the `request body`.

#### Timing security

* A `SIGNED` endpoint also requires a parameter, `timestamp`, to be sent which should be the millisecond timestamp of when the request was created and sent.
* An additional parameter, `recvWindow`, may be sent to specify the number of milliseconds after `timestamp` the request is valid for. If `recvWindow` is not sent, **it defaults to 5000**.

> The logic is as follows:

```
  if (timestamp < (serverTime + 1000) && (serverTime - timestamp) <= recvWindow){
    // process request
  } 
  else {
    // reject request
  }
```

**Serious trading is about timing.** Networks can be unstable and unreliable, which can lead to requests taking varying amounts of time to reach the servers. With `recvWindow`, you can specify that the request must be processed within a certain number of milliseconds or be rejected by the server.

It is recommended to use a small recvWindow of 5000 or less.

#### Signed endpoint examples for POST /fapi/v1/order

Here is a step-by-step example of how to send a vaild signed payload from the Linux command line using `echo`, `openssl`, and `curl`.

| Key       | Value                                                            |
| --------- | ---------------------------------------------------------------- |
| apiKey    | dbefbc809e3e83c283a984c3a1459732ea7db1360ca80c5c2c8867408d28cc83 |
| secretKey | 2b5eb11e18796d12d88f13dc27dbbd02c2cc51ff7059765ed9821957d82bb4d9 |

| Parameter   | Value         |
| ----------- | ------------- |
| symbol      | BTCUSDT       |
| side        | BUY           |
| type        | LIMIT         |
| timeInForce | GTC           |
| quantity    | 1             |
| price       | 9000          |
| recvWindow  | 5000          |
| timestamp   | 1591702613943 |

**Example 1: As a query string**

> **Example 1**

> **HMAC SHA256 signature:**

```
    $ echo -n "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=9000&timeInForce=GTC&recvWindow=5000&timestamp=1591702613943" | openssl dgst -sha256 -hmac "2b5eb11e18796d12d88f13dc27dbbd02c2cc51ff7059765ed9821957d82bb4d9"
    (stdin)= 3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9
```

> **curl command:**

```
    (HMAC SHA256)
    $ curl -H "X-MBX-APIKEY: dbefbc809e3e83c283a984c3a1459732ea7db1360ca80c5c2c8867408d28cc83" -X POST 'https://fapi/asterdex.com/fapi/v1/order?symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=9000&timeInForce=GTC&recvWindow=5000&timestamp=1591702613943&signature= 3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9'
```

* **queryString:**

  symbol=BTCUSDT\
  \&side=BUY\
  \&type=LIMIT\
  \&timeInForce=GTC\
  \&quantity=1\
  \&price=9000\
  \&recvWindow=5000\
  \&timestamp=1591702613943

**Example 2: As a request body**

> **Example 2**

> **HMAC SHA256 signature:**

```
    $ echo -n "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=9000&timeInForce=GTC&recvWindow=5000&timestamp=1591702613943" | openssl dgst -sha256 -hmac "2b5eb11e18796d12d88f13dc27dbbd02c2cc51ff7059765ed9821957d82bb4d9"
    (stdin)= 3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9
```

> **curl command:**

```
    (HMAC SHA256)
    $ curl -H "X-MBX-APIKEY: dbefbc809e3e83c283a984c3a1459732ea7db1360ca80c5c2c8867408d28cc83" -X POST 'https://fapi/asterdex.com/fapi/v1/order' -d 'symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=9000&timeInForce=GTC&recvWindow=5000&timestamp=1591702613943&signature= 3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9'
```

* **requestBody:**

  symbol=BTCUSDT\
  \&side=BUY\
  \&type=LIMIT\
  \&timeInForce=GTC\
  \&quantity=1\
  \&price=9000\
  \&recvWindow=5000\
  \&timestamp=1591702613943

**Example 3: Mixed query string and request body**

> **Example 3**

> **HMAC SHA256 signature:**

```
    $ echo -n "symbol=BTCUSDT&side=BUY&type=LIMIT&quantity=1&price=9000&timeInForce=GTC&recvWindow=5000&timestamp=1591702613943" | openssl dgst -sha256 -hmac "2b5eb11e18796d12d88f13dc27dbbd02c2cc51ff7059765ed9821957d82bb4d9"
    (stdin)= 3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9
```

> **curl command:**

```
    (HMAC SHA256)
    $ curl -H "X-MBX-APIKEY: dbefbc809e3e83c283a984c3a1459732ea7db1360ca80c5c2c8867408d28cc83" -X POST 'https://fapi/asterdex.com/fapi/v1/order?symbol=BTCUSDT&side=BUY&type=LIMIT&timeInForce=GTC' -d 'quantity=1&price=9000&recvWindow=5000&timestamp=1591702613943&signature=3c661234138461fcc7a7d8746c6558c9842d4e10870d2ecbedf7777cad694af9'
```

* **queryString:** symbol=BTCUSDT\&side=BUY\&type=LIMIT\&timeInForce=GTC
* **requestBody:** quantity=1\&price=9000\&recvWindow=5000\&timestamp= 1591702613943

Note that the signature is different in example 3.\
There is no & between "GTC" and "quantity=1".

### Public endpoints info

#### Terminology

* `base asset` refers to the asset that is the `quantity` of a symbol.
* `quote asset` refers to the asset that is the `price` of a symbol.

#### ENUM definitions

**Symbol type:**

* FUTURE

**Contract type (contractType):**

* PERPETUAL

**Contract status (contractStatus, status):**

* PENDING\_TRADING
* TRADING
* PRE\_SETTLE
* SETTLING
* CLOSE

**Order status (status):**

* NEW
* PARTIALLY\_FILLED
* FILLED
* CANCELED
* REJECTED
* EXPIRED

**Order types (orderTypes, type):**

* LIMIT
* MARKET
* STOP
* STOP\_MARKET
* TAKE\_PROFIT
* TAKE\_PROFIT\_MARKET
* TRAILING\_STOP\_MARKET

**Order side (side):**

* BUY
* SELL

**Position side (positionSide):**

* BOTH
* LONG
* SHORT

**Time in force (timeInForce):**

* GTC - Good Till Cancel
* IOC - Immediate or Cancel
* FOK - Fill or Kill
* GTX - Good Till Crossing (Post Only)

**Working Type (workingType)**

* MARK\_PRICE
* CONTRACT\_PRICE

**Response Type (newOrderRespType)**

* ACK
* RESULT

**Kline/Candlestick chart intervals:**

m → minutes; h → hours; d → days; w → weeks; M → months

* 1m
* 3m
* 5m
* 15m
* 30m
* 1h
* 2h
* 4h
* 6h
* 8h
* 12h
* 1d
* 3d
* 1w
* 1M

**Rate limiters (rateLimitType)**

> REQUEST\_WEIGHT

```
  {
  	"rateLimitType": "REQUEST_WEIGHT",
  	"interval": "MINUTE",
  	"intervalNum": 1,
  	"limit": 2400
  }
```

> ORDERS

```
  {
  	"rateLimitType": "ORDERS",
  	"interval": "MINUTE",
  	"intervalNum": 1,
  	"limit": 1200
   }
```

* REQUEST\_WEIGHT
* ORDERS

**Rate limit intervals (interval)**

* MINUTE

### Filters

Filters define trading rules on a symbol or an exchange.

#### Symbol filters

**PRICE\_FILTER**

> **/exchangeInfo format:**

```
  {
    "filterType": "PRICE_FILTER",
    "minPrice": "0.00000100",
    "maxPrice": "100000.00000000",
    "tickSize": "0.00000100"
  }
```

The `PRICE_FILTER` defines the `price` rules for a symbol. There are 3 parts:

* `minPrice` defines the minimum `price`/`stopPrice` allowed; disabled on `minPrice` == 0.
* `maxPrice` defines the maximum `price`/`stopPrice` allowed; disabled on `maxPrice` == 0.
* `tickSize` defines the intervals that a `price`/`stopPrice` can be increased/decreased by; disabled on `tickSize` == 0.

Any of the above variables can be set to 0, which disables that rule in the `price filter`. In order to pass the `price filter`, the following must be true for `price`/`stopPrice` of the enabled rules:

* `price` >= `minPrice`
* `price` <= `maxPrice`
* (`price`-`minPrice`) % `tickSize` == 0

**LOT\_SIZE**

> **/exchangeInfo format:**

```
  {
    "filterType": "LOT_SIZE",
    "minQty": "0.00100000",
    "maxQty": "100000.00000000",
    "stepSize": "0.00100000"
  }
```

The `LOT_SIZE` filter defines the `quantity` (aka "lots" in auction terms) rules for a symbol. There are 3 parts:

* `minQty` defines the minimum `quantity` allowed.
* `maxQty` defines the maximum `quantity` allowed.
* `stepSize` defines the intervals that a `quantity` can be increased/decreased by.

In order to pass the `lot size`, the following must be true for `quantity`:

* `quantity` >= `minQty`
* `quantity` <= `maxQty`
* (`quantity`-`minQty`) % `stepSize` == 0

**MARKET\_LOT\_SIZE**

> **/exchangeInfo format:**

```
  {
    "filterType": "MARKET_LOT_SIZE",
    "minQty": "0.00100000",
    "maxQty": "100000.00000000",
    "stepSize": "0.00100000"
  }
```

The `MARKET_LOT_SIZE` filter defines the `quantity` (aka "lots" in auction terms) rules for `MARKET` orders on a symbol. There are 3 parts:

* `minQty` defines the minimum `quantity` allowed.
* `maxQty` defines the maximum `quantity` allowed.
* `stepSize` defines the intervals that a `quantity` can be increased/decreased by.

In order to pass the `market lot size`, the following must be true for `quantity`:

* `quantity` >= `minQty`
* `quantity` <= `maxQty`
* (`quantity`-`minQty`) % `stepSize` == 0

**MAX\_NUM\_ORDERS**

> **/exchangeInfo format:**

```
  {
    "filterType": "MAX_NUM_ORDERS",
    "limit": 200
  }
```

The `MAX_NUM_ORDERS` filter defines the maximum number of orders an account is allowed to have open on a symbol.

Note that both "algo" orders and normal orders are counted for this filter.

**MAX\_NUM\_ALGO\_ORDERS**

> **/exchangeInfo format:**

```
  {
    "filterType": "MAX_NUM_ALGO_ORDERS",
    "limit": 100
  }
```

The `MAX_NUM_ALGO_ORDERS` filter defines the maximum number of all kinds of algo orders an account is allowed to have open on a symbol.

The algo orders include `STOP`, `STOP_MARKET`, `TAKE_PROFIT`, `TAKE_PROFIT_MARKET`, and `TRAILING_STOP_MARKET` orders.

**PERCENT\_PRICE**

> **/exchangeInfo format:**

```
  {
    "filterType": "PERCENT_PRICE",
    "multiplierUp": "1.1500",
    "multiplierDown": "0.8500",
    "multiplierDecimal": 4
  }
```

The `PERCENT_PRICE` filter defines valid range for a price based on the mark price.

In order to pass the `percent price`, the following must be true for `price`:

* BUY: `price` <= `markPrice` \* `multiplierUp`
* SELL: `price` >= `markPrice` \* `multiplierDown`

**MIN\_NOTIONAL**

> **/exchangeInfo format:**

```
  {
    "filterType": "MIN_NOTIONAL",
    "notional": "1"
  }
```

The `MIN_NOTIONAL` filter defines the minimum notional value allowed for an order on a symbol. An order's notional value is the `price` \* `quantity`. Since `MARKET` orders have no price, the mark price is used.

***

## Market data endpoints

### Test connectivity

> **Response:**

```
{}
```

`GET /fapi/v1/ping`

Test connectivity to the Rest API.

**Weight:** 1

**Parameters:** NONE

###

### Check Server Time

> **Response:**

```
{
  "serverTime": 1499827319559
}
```

`GET /fapi/v1/time`

Test connectivity to the Rest API and get the current server time.

**Weight:** 1

**Parameters:** NONE

###

### Exchange information

> **Response:**

```
{
	"exchangeFilters": [],
 	"rateLimits": [
 		{
 			"interval": "MINUTE",
   			"intervalNum": 1,
   			"limit": 2400,
   			"rateLimitType": "REQUEST_WEIGHT" 
   		},
  		{
  			"interval": "MINUTE",
   			"intervalNum": 1,
   			"limit": 1200,
   			"rateLimitType": "ORDERS"
   		}
   	],
 	"serverTime": 1565613908500,    // Ignore please. If you want to check current server time, please check via "GET /fapi/v1/time"
 	"assets": [ // assets information
 		{
 			"asset": "BUSD",
   			"marginAvailable": true, // whether the asset can be used as margin in Multi-Assets mode
   			"autoAssetExchange": 0 // auto-exchange threshold in Multi-Assets margin mode
   		},
 		{
 			"asset": "USDT",
   			"marginAvailable": true,
   			"autoAssetExchange": 0
   		},
 		{
 			"asset": "BTC",
   			"marginAvailable": false,
   			"autoAssetExchange": null
   		}
   	],
 	"symbols": [
 		{
 			"symbol": "DOGEUSDT",
 			"pair": "DOGEUSDT",
 			"contractType": "PERPETUAL",
 			"deliveryDate": 4133404800000,
 			"onboardDate": 1598252400000,
 			"status": "TRADING",
 			"maintMarginPercent": "2.5000",   // ignore
 			"requiredMarginPercent": "5.0000",  // ignore
 			"baseAsset": "BLZ", 
 			"quoteAsset": "USDT",
 			"marginAsset": "USDT",
 			"pricePrecision": 5,	// please do not use it as tickSize
 			"quantityPrecision": 0, // please do not use it as stepSize
 			"baseAssetPrecision": 8,
 			"quotePrecision": 8, 
 			"underlyingType": "COIN",
 			"underlyingSubType": ["STORAGE"],
 			"settlePlan": 0,
 			"triggerProtect": "0.15", // threshold for algo order with "priceProtect"
 			"filters": [
 				{
 					"filterType": "PRICE_FILTER",
     				"maxPrice": "300",
     				"minPrice": "0.0001", 
     				"tickSize": "0.0001"
     			},
    			{
    				"filterType": "LOT_SIZE", 
     				"maxQty": "10000000",
     				"minQty": "1",
     				"stepSize": "1"
     			},
    			{
    				"filterType": "MARKET_LOT_SIZE",
     				"maxQty": "590119",
     				"minQty": "1",
     				"stepSize": "1"
     			},
     			{
    				"filterType": "MAX_NUM_ORDERS",
    				"limit": 200
  				},
  				{
    				"filterType": "MAX_NUM_ALGO_ORDERS",
    				"limit": 100
  				},
  				{
  					"filterType": "MIN_NOTIONAL",
  					"notional": "1", 
  				},
  				{
    				"filterType": "PERCENT_PRICE",
    				"multiplierUp": "1.1500",
    				"multiplierDown": "0.8500",
    				"multiplierDecimal": 4
    			}
   			],
 			"OrderType": [
   				"LIMIT",
   				"MARKET",
   				"STOP",
   				"STOP_MARKET",
   				"TAKE_PROFIT",
   				"TAKE_PROFIT_MARKET",
   				"TRAILING_STOP_MARKET" 
   			],
   			"timeInForce": [
   				"GTC", 
   				"IOC", 
   				"FOK", 
   				"GTX" 
 			],
 			"liquidationFee": "0.010000",	// liquidation fee rate
   			"marketTakeBound": "0.30",	// the max price difference rate( from mark price) a market order can make
 		}
   	],
	"timezone": "UTC" 
}
```

`GET /fapi/v1/exchangeInfo`

Current exchange trading rules and symbol information.

**Weight:** 1

**Parameters:** NONE

###

### Order book

> **Response:**

```
{
  "lastUpdateId": 1027024,
  "E": 1589436922972,   // Message output time
  "T": 1589436922959,   // Transaction time
  "bids": [
    [
      "4.00000000",     // PRICE
      "431.00000000"    // QTY
    ]
  ],
  "asks": [
    [
      "4.00000200",
      "12.00000000"
    ]
  ]
}
```

`GET /fapi/v1/depth`

**Weight:**

Adjusted based on the limit:

| Limit         | Weight |
| ------------- | ------ |
| 5, 10, 20, 50 | 2      |
| 100           | 5      |
| 500           | 10     |
| 1000          | 20     |

**Parameters:**

| Name   | Type   | Mandatory | Description                                                 |
| ------ | ------ | --------- | ----------------------------------------------------------- |
| symbol | STRING | YES       |                                                             |
| limit  | INT    | NO        | Default 500; Valid limits: \[5, 10, 20, 50, 100, 500, 1000] |

### Recent trades list

> **Response:**

```
[
  {
    "id": 28457,
    "price": "4.00000100",
    "qty": "12.00000000",
    "quoteQty": "48.00",
    "time": 1499865549590,
    "isBuyerMaker": true,
  }
]
```

`GET /fapi/v1/trades`

Get recent market trades

**Weight:** 1

**Parameters:**

| Name   | Type   | Mandatory | Description            |
| ------ | ------ | --------- | ---------------------- |
| symbol | STRING | YES       |                        |
| limit  | INT    | NO        | Default 500; max 1000. |

* Market trades means trades filled in the order book. Only market trades will be returned, which means the insurance fund trades and ADL trades won't be returned.

###

### Old trades lookup (MARKET\_DATA)

> **Response:**

```
[
  {
    "id": 28457,
    "price": "4.00000100",
    "qty": "12.00000000",
    "quoteQty": "8000.00",
    "time": 1499865549590,
    "isBuyerMaker": true,
  }
]
```

`GET /fapi/v1/historicalTrades`

Get older market historical trades.

**Weight:** 20

**Parameters:**

| Name   | Type   | Mandatory | Description                                             |
| ------ | ------ | --------- | ------------------------------------------------------- |
| symbol | STRING | YES       |                                                         |
| limit  | INT    | NO        | Default 500; max 1000.                                  |
| fromId | LONG   | NO        | TradeId to fetch from. Default gets most recent trades. |

* Market trades means trades filled in the order book. Only market trades will be returned, which means the insurance fund trades and ADL trades won't be returned.

###

### Compressed/Aggregate trades list

> **Response:**

```
[
  {
    "a": 26129,         // Aggregate tradeId
    "p": "0.01633102",  // Price
    "q": "4.70443515",  // Quantity
    "f": 27781,         // First tradeId
    "l": 27781,         // Last tradeId
    "T": 1498793709153, // Timestamp
    "m": true,          // Was the buyer the maker?
  }
]
```

`GET /fapi/v1/aggTrades`

Get compressed, aggregate market trades. Market trades that fill at the time, from the same order, with the same price will have the quantity aggregated.

**Weight:** 20

**Parameters:**

| Name      | Type   | Mandatory | Description                                              |
| --------- | ------ | --------- | -------------------------------------------------------- |
| symbol    | STRING | YES       |                                                          |
| fromId    | LONG   | NO        | ID to get aggregate trades from INCLUSIVE.               |
| startTime | LONG   | NO        | Timestamp in ms to get aggregate trades from INCLUSIVE.  |
| endTime   | LONG   | NO        | Timestamp in ms to get aggregate trades until INCLUSIVE. |
| limit     | INT    | NO        | Default 500; max 1000.                                   |

* If both startTime and endTime are sent, time between startTime and endTime must be less than 1 hour.
* If fromId, startTime, and endTime are not sent, the most recent aggregate trades will be returned.
* Only market trades will be aggregated and returned, which means the insurance fund trades and ADL trades won't be aggregated.

### Kline/Candlestick data

> **Response:**

```
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
```

`GET /fapi/v1/klines`

Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

**Weight:** based on parameter `LIMIT`

| LIMIT        | Weight |
| ------------ | ------ |
| \[1,100)     | 1      |
| \[100, 500)  | 2      |
| \[500, 1000] | 5      |

> 1000 | 10

**Parameters:**

| Name      | Type   | Mandatory | Description            |
| --------- | ------ | --------- | ---------------------- |
| symbol    | STRING | YES       |                        |
| interval  | ENUM   | YES       |                        |
| startTime | LONG   | NO        |                        |
| endTime   | LONG   | NO        |                        |
| limit     | INT    | NO        | Default 500; max 1500. |

* If startTime and endTime are not sent, the most recent klines are returned.

### Index price kline/candlestick data

> **Response:**

```
[
  [
    1591256400000,      	// Open time
    "9653.69440000",    	// Open
    "9653.69640000",     	// High
    "9651.38600000",     	// Low
    "9651.55200000",     	// Close (or latest price)
    "0	", 					// Ignore
    1591256459999,      	// Close time
    "0",    				// Ignore
    60,                		// Number of bisic data
    "0",    				// Ignore
    "0",      				// Ignore
    "0" 					// Ignore
  ]
]
```

`GET /fapi/v1/indexPriceKlines`

Kline/candlestick bars for the index price of a pair.

Klines are uniquely identified by their open time.

**Weight:** based on parameter `LIMIT`

| Limit        | Weight |
| ------------ | ------ |
| \[1,100)     | 1      |
| \[100, 500)  | 2      |
| \[500, 1000] | 5      |

> 1000 | 10

**Parameters:**

| Name      | Type   | Mandatory | Description            |
| --------- | ------ | --------- | ---------------------- |
| pair      | STRING | YES       |                        |
| interval  | ENUM   | YES       |                        |
| startTime | LONG   | NO        |                        |
| endTime   | LONG   | NO        |                        |
| limit     | INT    | NO        | Default 500; max 1500. |

* If startTime and endTime are not sent, the most recent klines are returned.

### Mark Price Kline/Candlestick Data

> **Response:**

```
[
  [
    1591256460000,     		// Open time
    "9653.29201333",    	// Open
    "9654.56401333",     	// High
    "9653.07367333",     	// Low
    "9653.07367333",     	// Close (or latest price)
    "0	", 					// Ignore
    1591256519999,      	// Close time
    "0",    				// Ignore
    60,                	 	// Number of bisic data
    "0",    				// Ignore
    "0",      			 	// Ignore
    "0" 					// Ignore
  ]
]
```

`GET /fapi/v1/markPriceKlines`

Kline/candlestick bars for the mark price of a symbol.

Klines are uniquely identified by their open time.

**Weight:** based on parameter `LIMIT`

| Limit        | Weight |
| ------------ | ------ |
| \[1,100)     | 1      |
| \[100, 500)  | 2      |
| \[500, 1000] | 5      |

> 1000 | 10

**Parameters:**

| Name      | Type   | Mandatory | Description            |
| --------- | ------ | --------- | ---------------------- |
| symbol    | STRING | YES       |                        |
| interval  | ENUM   | YES       |                        |
| startTime | LONG   | NO        |                        |
| endTime   | LONG   | NO        |                        |
| limit     | INT    | NO        | Default 500; max 1500. |

* If startTime and endTime are not sent, the most recent klines are returned.

###

### Mark Price

> **Response:**

```
{
	"symbol": "BTCUSDT",
	"markPrice": "11793.63104562",	// mark price
	"indexPrice": "11781.80495970",	// index price
	"estimatedSettlePrice": "11781.16138815", // Estimated Settle Price, only useful in the last hour before the settlement starts.
	"lastFundingRate": "0.00038246",  // This is the lasted funding rate
	"nextFundingTime": 1597392000000,
	"interestRate": "0.00010000",
	"time": 1597370495002
}
```

> **OR (when symbol not sent)**

```
[
	{
	    "symbol": "BTCUSDT",
	    "markPrice": "11793.63104562",	// mark price
	    "indexPrice": "11781.80495970",	// index price
	    "estimatedSettlePrice": "11781.16138815", // Estimated Settle Price, only useful in the last hour before the settlement starts.
	    "lastFundingRate": "0.00038246",  // This is the lasted funding rate
	    "nextFundingTime": 1597392000000,
	    "interestRate": "0.00010000",	
	    "time": 1597370495002
	}
]
```

`GET /fapi/v1/premiumIndex`

Mark Price and Funding Rate

**Weight:** 1

**Parameters:**

| Name   | Type   | Mandatory | Description |
| ------ | ------ | --------- | ----------- |
| symbol | STRING | NO        |             |

### Get funding rate history

> **Response:**

```
[
	{
    	"symbol": "BTCUSDT",
    	"fundingRate": "-0.03750000",
    	"fundingTime": 1570608000000,
	},
	{
   		"symbol": "BTCUSDT",
    	"fundingRate": "0.00010000",
    	"fundingTime": 1570636800000,
	}
]
```

`GET /fapi/v1/fundingRate`

**Weight:** 1

**Parameters:**

| Name      | Type   | Mandatory | Description                                          |
| --------- | ------ | --------- | ---------------------------------------------------- |
| symbol    | STRING | NO        |                                                      |
| startTime | LONG   | NO        | Timestamp in ms to get funding rate from INCLUSIVE.  |
| endTime   | LONG   | NO        | Timestamp in ms to get funding rate until INCLUSIVE. |
| limit     | INT    | NO        | Default 100; max 1000                                |

* If `startTime` and `endTime` are not sent, the most recent `limit` datas are returned.
* If the number of data between `startTime` and `endTime` is larger than `limit`, return as `startTime` + `limit`.
* In ascending order.

###

### 24hr ticker price change statistics

> **Response:**

```
{
  "symbol": "BTCUSDT",
  "priceChange": "-94.99999800",
  "priceChangePercent": "-95.960",
  "weightedAvgPrice": "0.29628482",
  "prevClosePrice": "0.10002000",
  "lastPrice": "4.00000200",
  "lastQty": "200.00000000",
  "openPrice": "99.00000000",
  "highPrice": "100.00000000",
  "lowPrice": "0.10000000",
  "volume": "8913.30000000",
  "quoteVolume": "15.30000000",
  "openTime": 1499783499040,
  "closeTime": 1499869899040,
  "firstId": 28385,   // First tradeId
  "lastId": 28460,    // Last tradeId
  "count": 76         // Trade count
}
```

> OR

```
[
	{
  		"symbol": "BTCUSDT",
  		"priceChange": "-94.99999800",
  		"priceChangePercent": "-95.960",
  		"weightedAvgPrice": "0.29628482",
  		"prevClosePrice": "0.10002000",
  		"lastPrice": "4.00000200",
  		"lastQty": "200.00000000",
  		"openPrice": "99.00000000",
  		"highPrice": "100.00000000",
  		"lowPrice": "0.10000000",
  		"volume": "8913.30000000",
  		"quoteVolume": "15.30000000",
  		"openTime": 1499783499040,
  		"closeTime": 1499869899040,
  		"firstId": 28385,   // First tradeId
  		"lastId": 28460,    // Last tradeId
  		"count": 76         // Trade count
	}
]
```

`GET /fapi/v1/ticker/24hr`

24 hour rolling window price change statistics.\
**Careful** when accessing this with no symbol.

**Weight:**\
1 for a single symbol;\
**40** when the symbol parameter is omitted

**Parameters:**

| Name   | Type   | Mandatory | Description |
| ------ | ------ | --------- | ----------- |
| symbol | STRING | NO        |             |

* If the symbol is not sent, tickers for all symbols will be returned in an array.

### Symbol price ticker

> **Response:**

```
{
  "symbol": "BTCUSDT",
  "price": "6000.01",
  "time": 1589437530011   // Transaction time
}
```

> OR

```
[
	{
  		"symbol": "BTCUSDT",
  		"price": "6000.01",
  		"time": 1589437530011
	}
]
```

`GET /fapi/v1/ticker/price`

Latest price for a symbol or symbols.

**Weight:**\
**1** for a single symbol;\
**2** when the symbol parameter is omitted

**Parameters:**

| Name   | Type   | Mandatory | Description |
| ------ | ------ | --------- | ----------- |
| symbol | STRING | NO        |             |

* If the symbol is not sent, prices for all symbols will be returned in an array.

### Symbol order book ticker

> **Response:**

```
{
  "symbol": "BTCUSDT",
  "bidPrice": "4.00000000",
  "bidQty": "431.00000000",
  "askPrice": "4.00000200",
  "askQty": "9.00000000",
  "time": 1589437530011   // Transaction time
}
```

> OR

```
[
	{
  		"symbol": "BTCUSDT",
  		"bidPrice": "4.00000000",
  		"bidQty": "431.00000000",
  		"askPrice": "4.00000200",
  		"askQty": "9.00000000",
  		"time": 1589437530011
	}
]
```

`GET /fapi/v1/ticker/bookTicker`

Best price/qty on the order book for a symbol or symbols.

**Weight:**\
**1** for a single symbol;\
**2** when the symbol parameter is omitted

**Parameters:**

| Name   | Type   | Mandatory | Description |
| ------ | ------ | --------- | ----------- |
| symbol | STRING | NO        |             |

* If the symbol is not sent, bookTickers for all symbols will be returned in an array.

## WebSocket market streams

#### WebSocket access

* The base URL for WebSocket connections is: **wss\://fstream.asterdex.com**
* Streams can be accessed in two ways:
  * Raw stream: **/ws/\<streamName>**
  * Combined stream: **/stream?streams=\<streamName1>/\<streamName2>/\<streamName3>**
* In combined streams, each event is wrapped in the following format:

  **{"stream": "\<streamName>", "data": \<rawPayload>}**
* All stream names (including symbols) must be **lowercase**.

#### Connection rules and limits

* A single WebSocket connection is valid for 24 hours. Connections will be disconnected automatically at the 24-hour mark.
* The server sends a ping frame every 5 minutes. If no pong frame is received within 15 minutes, the connection will be closed.
  * Unsolicited pong frames (sent without receiving a ping) are allowed.
* WebSocket connections are limited to 10 incoming messages per second.
  * Connections exceeding this limit will be disconnected.
  * IP addresses that are repeatedly disconnected may be banned.
* A single connection can subscribe to a maximum of 200 streams.

#### Recommendation

Due to potential delays in RESTful responses during periods of extreme market volatility, it is strongly recommended to retrieve order status, position updates, and related information via the WebSocket user data stream instead of relying on REST endpoints.

### Live subscribing/Unsubscribing to streams

* The following data can be sent through the WebSocket instance in order to subscribe/unsubscribe from streams. Examples can be seen below.
* The `id` used in the JSON payloads is an unsigned INT used as an identifier to uniquely identify the messages going back and forth.

#### Subscribe to a stream

> **Response**

```
{
  "result": null,
  "id": 1
}
```

* **Request**

  {\
  "method": "SUBSCRIBE",\
  "params":\
  \[\
  "btcusdt\@aggTrade",\
  "btcusdt\@depth"\
  ],\
  "id": 1\
  }

#### Unsubscribe to a stream

> **Response**

```
{
  "result": null,
  "id": 312
}
```

* **Request**

  {\
  "method": "UNSUBSCRIBE",\
  "params":\
  \[\
  "btcusdt\@depth"\
  ],\
  "id": 312\
  }

#### Listing subscriptions

> **Response**

```
{
  "result": [
    "btcusdt@aggTrade"
  ],
  "id": 3
}
```

* **Request**

  {\
  "method": "LIST\_SUBSCRIPTIONS",\
  "id": 3\
  }

#### Setting properties

Currently, the only property can be set is to set whether `combined` stream payloads are enabled are not. The combined property is set to `false` when connecting using `/ws/` ("raw streams") and `true` when connecting using `/stream/`.

> **Response**

```
{
  "result": null,
  "id": 5
}
```

* **Request**

  {\
  "method": "SET\_PROPERTY",\
  "params":\
  \[\
  "combined",\
  true\
  ],\
  "id": 5\
  }

#### Retrieving properties

> **Response**

```
{
  "result": true, // Indicates that combined is set to true.
  "id": 2
}
```

* **Request**

  {\
  "method": "GET\_PROPERTY",\
  "params":\
  \[\
  "combined"\
  ],\
  "id": 2\
  }

#### Error messages

| Error Message                                                                                                                                                                   | Description                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| {"code": 0, "msg": "Unknown property"}                                                                                                                                          | Parameter used in the `SET_PROPERTY` or `GET_PROPERTY` was invalid                                   |
| {"code": 1, "msg": "Invalid value type: expected Boolean"}                                                                                                                      | Value should only be `true` or `false`                                                               |
| {"code": 2, "msg": "Invalid request: property name must be a string"}                                                                                                           | Property name provided was invalid                                                                   |
| {"code": 2, "msg": "Invalid request: request ID must be an unsigned integer"}                                                                                                   | Parameter `id` had to be provided or the value provided in the `id` parameter is an unsupported type |
| {"code": 2, "msg": "Invalid request: unknown variant %s, expected one of `SUBSCRIBE`, `UNSUBSCRIBE`, `LIST_SUBSCRIPTIONS`, `SET_PROPERTY`, `GET_PROPERTY` at line 1 column 28"} | Possible typo in the provided method or provided method was neither of the expected values           |
| {"code": 2, "msg": "Invalid request: too many parameters"}                                                                                                                      | Unnecessary parameters provided in the data                                                          |
| {"code": 2, "msg": "Invalid request: property name must be a string"}                                                                                                           | Property name was not provided                                                                       |
| {"code": 2, "msg": "Invalid request: missing field `method` at line 1 column 73"}                                                                                               | `method` was not provided in the data                                                                |
| {"code":3,"msg":"Invalid JSON: expected value at line %s column %s"}                                                                                                            | JSON data sent has incorrect syntax.                                                                 |

### Aggregate trade streams

> **Payload:**

```
{
  "e": "aggTrade",  // Event type
  "E": 123456789,   // Event time
  "s": "BTCUSDT",    // Symbol
  "a": 5933014,		// Aggregate trade ID
  "p": "0.001",     // Price
  "q": "100",       // Quantity
  "f": 100,         // First trade ID
  "l": 105,         // Last trade ID
  "T": 123456785,   // Trade time
  "m": true,        // Is the buyer the market maker?
}
```

The aggregate trade streams push market trade information that is aggregated for a single taker order every 100 milliseconds.

**Stream name:**\
`<symbol>@aggTrade`

**Update speed:** 100ms

* Only market trades will be aggregated, which means the insurance fund trades and ADL trades won't be aggregated.

### Mark price stream

> **Payload:**

```
  {
    "e": "markPriceUpdate",  	// Event type
    "E": 1562305380000,      	// Event time
    "s": "BTCUSDT",          	// Symbol
    "p": "11794.15000000",   	// Mark price
    "i": "11784.62659091",		// Index price
    "P": "11784.25641265",		// Estimated Settle Price, only useful in the last hour before the settlement starts
    "r": "0.00038167",       	// Funding rate
    "T": 1562306400000       	// Next funding time
  }
```

Mark price and funding rate for a single symbol pushed every 3 seconds or every second.

**Stream name:**\
`<symbol>@markPrice` or `<symbol>@markPrice@1s`

**Update speed:** 3000ms or 1000ms

### Mark price stream for all markets

> **Payload:**

```
[ 
  {
    "e": "markPriceUpdate",  	// Event type
    "E": 1562305380000,      	// Event time
    "s": "BTCUSDT",          	// Symbol
    "p": "11185.87786614",   	// Mark price
    "i": "11784.62659091"		// Index price
    "P": "11784.25641265",		// Estimated Settle Price, only useful in the last hour before the settlement starts
    "r": "0.00030000",       	// Funding rate
    "T": 1562306400000       	// Next funding time
  }
]
```

Mark price and funding rate for all symbols pushed every 3 seconds or every second.

**Stream name:**\
`!markPrice@arr` or `!markPrice@arr@1s`

**Update speed:** 3000ms or 1000ms

### Kline/candlestick streams

> **Payload:**

```
{
  "e": "kline",     // Event type
  "E": 123456789,   // Event time
  "s": "BTCUSDT",    // Symbol
  "k": {
    "t": 123400000, // Kline start time
    "T": 123460000, // Kline close time
    "s": "BTCUSDT",  // Symbol
    "i": "1m",      // Interval
    "f": 100,       // First trade ID
    "L": 200,       // Last trade ID
    "o": "0.0010",  // Open price
    "c": "0.0020",  // Close price
    "h": "0.0025",  // High price
    "l": "0.0015",  // Low price
    "v": "1000",    // Base asset volume
    "n": 100,       // Number of trades
    "x": false,     // Is this kline closed?
    "q": "1.0000",  // Quote asset volume
    "V": "500",     // Taker buy base asset volume
    "Q": "0.500",   // Taker buy quote asset volume
    "B": "123456"   // Ignore
  }
}
```

The kline/candlestick stream push updates to the current klines/candlestick every 250 milliseconds (if existing).

**Kline/candlestick chart intervals:**

m → minutes; h → hours; d → days; w → weeks; M → months

* 1m
* 3m
* 5m
* 15m
* 30m
* 1h
* 2h
* 4h
* 6h
* 8h
* 12h
* 1d
* 3d
* 1w
* 1M

**Stream name:**\
`<symbol>@kline_<interval>`

**Update speed:** 250ms

### Individual symbol mini ticker stream

> **Payload:**

```
  {
    "e": "24hrMiniTicker",  // Event type
    "E": 123456789,         // Event time
    "s": "BTCUSDT",         // Symbol
    "c": "0.0025",          // Close price
    "o": "0.0010",          // Open price
    "h": "0.0025",          // High price
    "l": "0.0010",          // Low price
    "v": "10000",           // Total traded base asset volume
    "q": "18"               // Total traded quote asset volume
  }
```

24hr rolling window mini-ticker statistics for a single symbol. These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before.

**Stream name:**\
`<symbol>@miniTicker`

**Update speed:** 500ms

### All market mini tickers stream

> **Payload:**

```
[  
  {
    "e": "24hrMiniTicker",  // Event type
    "E": 123456789,         // Event time
    "s": "BTCUSDT",         // Symbol
    "c": "0.0025",          // Close price
    "o": "0.0010",          // Open price
    "h": "0.0025",          // High price
    "l": "0.0010",          // Low price
    "v": "10000",           // Total traded base asset volume
    "q": "18"               // Total traded quote asset volume
  }
]
```

24hr rolling window mini-ticker statistics for all symbols. These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before. Note that only tickers that have changed will be present in the array.

**Stream name:**\
`!miniTicker@arr`

**Update speed:** 1000ms

### Individual symbol ticker streams

> **Payload:**

```
{
  "e": "24hrTicker",  // Event type
  "E": 123456789,     // Event time
  "s": "BTCUSDT",     // Symbol
  "p": "0.0015",      // Price change
  "P": "250.00",      // Price change percent
  "w": "0.0018",      // Weighted average price
  "c": "0.0025",      // Last price
  "Q": "10",          // Last quantity
  "o": "0.0010",      // Open price
  "h": "0.0025",      // High price
  "l": "0.0010",      // Low price
  "v": "10000",       // Total traded base asset volume
  "q": "18",          // Total traded quote asset volume
  "O": 0,             // Statistics open time
  "C": 86400000,      // Statistics close time
  "F": 0,             // First trade ID
  "L": 18150,         // Last trade Id
  "n": 18151          // Total number of trades
}
```

24hr rolling window ticker statistics for a single symbol. These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before.

**Stream name:**\
`<symbol>@ticker`

**Update speed:** 500ms

### All market tickers streams

> **Payload:**

```
[
	{
	  "e": "24hrTicker",  // Event type
	  "E": 123456789,     // Event time
	  "s": "BTCUSDT",     // Symbol
	  "p": "0.0015",      // Price change
	  "P": "250.00",      // Price change percent
	  "w": "0.0018",      // Weighted average price
	  "c": "0.0025",      // Last price
	  "Q": "10",          // Last quantity
	  "o": "0.0010",      // Open price
	  "h": "0.0025",      // High price
	  "l": "0.0010",      // Low price
	  "v": "10000",       // Total traded base asset volume
	  "q": "18",          // Total traded quote asset volume
	  "O": 0,             // Statistics open time
	  "C": 86400000,      // Statistics close time
	  "F": 0,             // First trade ID
	  "L": 18150,         // Last trade Id
	  "n": 18151          // Total number of trades
	}
]
```

24hr rolling window ticker statistics for all symbols. These are NOT the statistics of the UTC day, but a 24hr rolling window from requestTime to 24hrs before. Note that only tickers that have changed will be present in the array.

**Stream name:**\
`!ticker@arr`

**Update speed:** 1000ms

### Individual symbol book ticker streams

> **Payload:**

```
{
  "e":"bookTicker",			// event type
  "u":400900217,     		// order book updateId
  "E": 1568014460893,  		// event time
  "T": 1568014460891,  		// transaction time
  "s":"BNBUSDT",     		// symbol
  "b":"25.35190000", 		// best bid price
  "B":"31.21000000", 		// best bid qty
  "a":"25.36520000", 		// best ask price
  "A":"40.66000000"  		// best ask qty
}
```

Pushes any update to the best bid or ask's price or quantity in real-time for a specified symbol.

**Stream name:** `<symbol>@bookTicker`

**Update speed:** Real-time

### All book tickers stream

> **Payload:**

```
{
  // Same as <symbol>@bookTicker payload
}
```

Pushes any update to the best bid or ask's price or quantity in real-time for all symbols.

**Stream name:** `!bookTicker`

**Update speed:** Real-time

### Liquidation order streams

> **Payload:**

```
{

	"e":"forceOrder",                   // Event Type
	"E":1568014460893,                  // Event Time
	"o":{
	
		"s":"BTCUSDT",                   // Symbol
		"S":"SELL",                      // Side
		"o":"LIMIT",                     // Order Type
		"f":"IOC",                       // Time in Force
		"q":"0.014",                     // Original Quantity
		"p":"9910",                      // Price
		"ap":"9910",                     // Average Price
		"X":"FILLED",                    // Order Status
		"l":"0.014",                     // Order Last Filled Quantity
		"z":"0.014",                     // Order Filled Accumulated Quantity
		"T":1568014460893,          	 // Order Trade Time
	
	}

}
```

The liquidation order snapshot streams push force liquidation order information for specific symbol.

For each symbol, only the latest one liquidation order within 1000ms will be pushed as the snapshot. If no liquidation happens in the interval of 1000ms, no stream will be pushed.

**Stream name:**  `<symbol>@forceOrder`

**Update speed:** 1000ms

### All market liquidation order streams

> **Payload:**

```
{

	"e":"forceOrder",                   // Event Type
	"E":1568014460893,                  // Event Time
	"o":{
	
		"s":"BTCUSDT",                   // Symbol
		"S":"SELL",                      // Side
		"o":"LIMIT",                     // Order Type
		"f":"IOC",                       // Time in Force
		"q":"0.014",                     // Original Quantity
		"p":"9910",                      // Price
		"ap":"9910",                     // Average Price
		"X":"FILLED",                    // Order Status
		"l":"0.014",                     // Order Last Filled Quantity
		"z":"0.014",                     // Order Filled Accumulated Quantity
		"T":1568014460893,          	 // Order Trade Time
	
	}

}
```

The all liquidation order snapshot streams push force liquidation order information for all symbols in the market.

For each symbol, only the latest liquidation order within 1000ms will be pushed as the snapshot. If no liquidation happens in the interval of 1000ms, no stream will be pushed.

**Stream name:** `!forceOrder@arr`

**Update speed:** 1000ms

### Partial book depth streams

> **Payload:**

```
{
  "e": "depthUpdate", // Event type
  "E": 1571889248277, // Event time
  "T": 1571889248276, // Transaction time
  "s": "BTCUSDT",
  "U": 390497796,
  "u": 390497878,
  "pu": 390497794,
  "b": [          // Bids to be updated
    [
      "7403.89",  // Price Level to be
      "0.002"     // Quantity
    ],
    [
      "7403.90",
      "3.906"
    ],
    [
      "7404.00",
      "1.428"
    ],
    [
      "7404.85",
      "5.239"
    ],
    [
      "7405.43",
      "2.562"
    ]
  ],
  "a": [          // Asks to be updated
    [
      "7405.96",  // Price level to be
      "3.340"     // Quantity
    ],
    [
      "7406.63",
      "4.525"
    ],
    [
      "7407.08",
      "2.475"
    ],
    [
      "7407.15",
      "4.800"
    ],
    [
      "7407.20",
      "0.175"
    ]
  ]
}
```

Top **\<levels>** bids and asks, valid **\<levels>** are 5, 10, or 20.

**Stream names:** `<symbol>@depth<levels>` OR `<symbol>@depth<levels>@500ms` OR `<symbol>@depth<levels>@100ms`.

**Update speed:** 250ms, 500ms or 100ms

### Diff. book depth streams

> **Payload:**

```
{
  "e": "depthUpdate", // Event type
  "E": 123456789,     // Event time
  "T": 123456788,     // Transaction time 
  "s": "BTCUSDT",     // Symbol
  "U": 157,           // First update ID in event
  "u": 160,           // Final update ID in event
  "pu": 149,          // Final update Id in last stream(ie `u` in last stream)
  "b": [              // Bids to be updated
    [
      "0.0024",       // Price level to be updated
      "10"            // Quantity
    ]
  ],
  "a": [              // Asks to be updated
    [
      "0.0026",       // Price level to be updated
      "100"          // Quantity
    ]
  ]
}
```

Bids and asks, pushed every 250 milliseconds, 500 milliseconds, 100 milliseconds (if existing)

**Stream name:**\
`<symbol>@depth` OR `<symbol>@depth@500ms` OR `<symbol>@depth@100ms`

**Update speed:** 250ms, 500ms, 100ms

### How to manage a local order book correctly

1. Open a stream to **wss\://fstream.asterdex.com/stream?streams=btcusdt\@depth**.
2. Buffer the events you receive from the stream. For same price, latest received update covers the previous one.
3. Get a depth snapshot from [**https://fapi.asterdex.com/fapi/v1/depth?symbol=BTCUSDT\&limit=1000**](https://fapi.asterdex.com/fapi/v1/depth?symbol=BTCUSDT\&limit=1000) .
4. Drop any event where `u` is < `lastUpdateId` in the snapshot.
5. The first processed event should have `U` <= `lastUpdateId` **AND** `u` >= `lastUpdateId`
6. While listening to the stream, each new event's `pu` should be equal to the previous event's `u`, otherwise initialize the process from step 3.
7. The data in each event is the **absolute** quantity for a price level.
8. If the quantity is 0, **remove** the price level.
9. Receiving an event that removes a price level that is not in your local order book can happen and is normal.

## Account/Trades endpoints

Considering the possible data latency from RESTful endpoints during an extremely volatile market, it is highly recommended to get the order status, position, etc. from the WebSocket user data stream.

### Change position mode (TRADE)

> **Response:**

```
{
	"code": 200,
	"msg": "success"
}
```

`POST /fapi/v1/positionSide/dual (HMAC SHA256)`

Change user's position mode (Hedge Mode or One-way Mode) on **every symbol**

**Weight:** 1

**Parameters:**

| Name             | Type   | Mandatory | Description                               |
| ---------------- | ------ | --------- | ----------------------------------------- |
| dualSidePosition | STRING | YES       | "true": Hedge Mode; "false": One-way Mode |
| recvWindow       | LONG   | NO        |                                           |
| timestamp        | LONG   | YES       |                                           |

###

### Get current position mode (USER\_DATA)

> **Response:**

```
{
	"dualSidePosition": true // "true": Hedge Mode; "false": One-way Mode
}
```

`GET /fapi/v1/positionSide/dual (HMAC SHA256)`

Get user's position mode (Hedge Mode or One-way Mode) on **every symbol**

**Weight:** 30

**Parameters:**

| Name       | Type | Mandatory | Description |
| ---------- | ---- | --------- | ----------- |
| recvWindow | LONG | NO        |             |
| timestamp  | LONG | YES       |             |

###

### Change Multi-Assets Mode (TRADE)

> **Response:**

```
{
	"code": 200,
	"msg": "success"
}
```

`POST /fapi/v1/multiAssetsMargin (HMAC SHA256)`

Change user's Multi-Asset Mode (Multi-Asset Mode or Single-Asset Mode) on **every symbol**

**Weight:** 1

**Parameters:**

| Name              | Type   | Mandatory | Description                                           |
| ----------------- | ------ | --------- | ----------------------------------------------------- |
| multiAssetsMargin | STRING | YES       | "true": Multi-Assets Mode; "false": Single-Asset Mode |
| recvWindow        | LONG   | NO        |                                                       |
| timestamp         | LONG   | YES       |                                                       |

###

### Get Current Multi-Assets Mode (USER\_DATA)

> **Response:**

```
{
	"multiAssetsMargin": true // "true": Multi-Assets Mode; "false": Single-Asset Mode
}
```

`GET /fapi/v1/multiAssetsMargin (HMAC SHA256)`

Get user's Multi-Asset Mode (Multi-Assets Mode or Single-Asset Mode) on **every symbol**

**Weight:** 30

**Parameters:**

| Name       | Type | Mandatory | Description |
| ---------- | ---- | --------- | ----------- |
| recvWindow | LONG | NO        |             |
| timestamp  | LONG | YES       |             |

###

### New order (TRADE)

> **Response:**

```
{
 	"clientOrderId": "testOrder",
 	"cumQty": "0",
 	"cumQuote": "0",
 	"executedQty": "0",
 	"orderId": 22542179,
 	"avgPrice": "0.00000",
 	"origQty": "10",
 	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "NEW",
  	"stopPrice": "9300",		// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   // if Close-All
  	"symbol": "BTCUSDT",
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"origType": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",	// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",			// callback rate, only return with TRAILING_STOP_MARKET order
 	"updateTime": 1566818724722,
 	"workingType": "CONTRACT_PRICE",
 	"priceProtect": false            // if conditional order trigger is protected	
}
```

`POST /fapi/v1/order (HMAC SHA256)`

Send in a new order.

**Weight:** 1

**Parameters:**

| Name             | Type    | Mandatory | Description                                                                                                                             |
| ---------------- | ------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| symbol           | STRING  | YES       |                                                                                                                                         |
| side             | ENUM    | YES       |                                                                                                                                         |
| positionSide     | ENUM    | NO        | Default `BOTH` for One-way Mode ; `LONG` or `SHORT` for Hedge Mode. It must be sent in Hedge Mode.                                      |
| type             | ENUM    | YES       |                                                                                                                                         |
| timeInForce      | ENUM    | NO        |                                                                                                                                         |
| quantity         | DECIMAL | NO        | Cannot be sent with `closePosition`=`true`(Close-All)                                                                                   |
| reduceOnly       | STRING  | NO        | "true" or "false". default "false". Cannot be sent in Hedge Mode; cannot be sent with `closePosition`=`true`                            |
| price            | DECIMAL | NO        |                                                                                                                                         |
| newClientOrderId | STRING  | NO        | A unique ID among open orders. Automatically generated if not sent. Can only be string following the rule: `^[\.A-Z\:/a-z0-9_-]{1,36}$` |
| stopPrice        | DECIMAL | NO        | Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders.                                                                |
| closePosition    | STRING  | NO        | `true`, `false`；Close-All, used with `STOP_MARKET` or `TAKE_PROFIT_MARKET`.                                                             |
| activationPrice  | DECIMAL | NO        | Used with `TRAILING_STOP_MARKET` orders, default as the latest price (supporting different `workingType`)                               |
| callbackRate     | DECIMAL | NO        | Used with `TRAILING_STOP_MARKET` orders, min 0.1, max 5 where 1 for 1%                                                                  |
| workingType      | ENUM    | NO        | stopPrice triggered by: "MARK\_PRICE", "CONTRACT\_PRICE". Default "CONTRACT\_PRICE"                                                     |
| priceProtect     | STRING  | NO        | "TRUE" or "FALSE", default "FALSE". Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders.                            |
| newOrderRespType | ENUM    | NO        | "ACK", "RESULT", default "ACK"                                                                                                          |
| recvWindow       | LONG    | NO        |                                                                                                                                         |
| timestamp        | LONG    | YES       |                                                                                                                                         |

Additional mandatory parameters based on `type`:

| Type                             | Additional mandatory parameters    |
| -------------------------------- | ---------------------------------- |
| `LIMIT`                          | `timeInForce`, `quantity`, `price` |
| `MARKET`                         | `quantity`                         |
| `STOP/TAKE_PROFIT`               | `quantity`, `price`, `stopPrice`   |
| `STOP_MARKET/TAKE_PROFIT_MARKET` | `stopPrice`                        |
| `TRAILING_STOP_MARKET`           | `callbackRate`                     |

* Order with type `STOP`, parameter `timeInForce` can be sent (default `GTC`).
* Order with type `TAKE_PROFIT`, parameter `timeInForce` can be sent (default `GTC`).
* Condition orders will be triggered when:
  * If parameter`priceProtect`is sent as true:
    * when price reaches the `stopPrice` ，the difference rate between "MARK\_PRICE" and "CONTRACT\_PRICE" cannot be larger than the "triggerProtect" of the symbol
    * "triggerProtect" of a symbol can be got from `GET /fapi/v1/exchangeInfo`
  * `STOP`, `STOP_MARKET`:
    * BUY: latest price ("MARK\_PRICE" or "CONTRACT\_PRICE") >= `stopPrice`
    * SELL: latest price ("MARK\_PRICE" or "CONTRACT\_PRICE") <= `stopPrice`
  * `TAKE_PROFIT`, `TAKE_PROFIT_MARKET`:
    * BUY: latest price ("MARK\_PRICE" or "CONTRACT\_PRICE") <= `stopPrice`
    * SELL: latest price ("MARK\_PRICE" or "CONTRACT\_PRICE") >= `stopPrice`
  * `TRAILING_STOP_MARKET`:
    * BUY: the lowest price after order placed <= `activationPrice`, and the latest price >= the lowest price \* (1 + `callbackRate`)
    * SELL: the highest price after order placed >= `activationPrice`, and the latest price <= the highest price \* (1 - `callbackRate`)
* For `TRAILING_STOP_MARKET`, if you got such error code.\
  `{"code": -2021, "msg": "Order would immediately trigger."}`\
  means that the parameters you send do not meet the following requirements:
  * BUY: `activationPrice` should be smaller than latest price.
  * SELL: `activationPrice` should be larger than latest price.
* If `newOrderRespType` is sent as `RESULT`:
  * `MARKET` order: the final FILLED result of the order will be return directly.
  * `LIMIT` order with special `timeInForce`: the final status result of the order(FILLED or EXPIRED) will be returned directly.
* `STOP_MARKET`, `TAKE_PROFIT_MARKET` with `closePosition`=`true`:
  * Follow the same rules for condition orders.
  * If triggered，**close all** current long position( if `SELL`) or current short position( if `BUY`).
  * Cannot be used with `quantity` paremeter
  * Cannot be used with `reduceOnly` parameter
  * In Hedge Mode,cannot be used with `BUY` orders in `LONG` position side. and cannot be used with `SELL` orders in `SHORT` position side

### Place Multiple Orders (TRADE)

> **Response:**

```
[
	{
	 	"clientOrderId": "testOrder",
	 	"cumQty": "0",
	 	"cumQuote": "0",
	 	"executedQty": "0",
	 	"orderId": 22542179,
	 	"avgPrice": "0.00000",
	 	"origQty": "10",
	 	"price": "0",
	  	"reduceOnly": false,
	  	"side": "BUY",
	  	"positionSide": "SHORT",
	  	"status": "NEW",
	  	"stopPrice": "9300",		// please ignore when order type is TRAILING_STOP_MARKET
	  	"symbol": "BTCUSDT",
	  	"timeInForce": "GTC",
	  	"type": "TRAILING_STOP_MARKET",
	  	"origType": "TRAILING_STOP_MARKET",
	  	"activatePrice": "9020",	// activation price, only return with TRAILING_STOP_MARKET order
	  	"priceRate": "0.3",			// callback rate, only return with TRAILING_STOP_MARKET order
	 	"updateTime": 1566818724722,
	 	"workingType": "CONTRACT_PRICE",
	 	"priceProtect": false            // if conditional order trigger is protected	
	},
	{
		"code": -2022, 
		"msg": "ReduceOnly Order is rejected."
	}
]
```

`POST /fapi/v1/batchOrders (HMAC SHA256)`

**Weight:** 5

**Parameters:**

| Name        | Type | Mandatory | Description              |
| ----------- | ---- | --------- | ------------------------ |
| batchOrders | LIST | YES       | order list. Max 5 orders |
| recvWindow  | LONG | NO        |                          |
| timestamp   | LONG | YES       |                          |

**Where `batchOrders` is the list of order parameters in JSON**

| Name             | Type    | Mandatory | Description                                                                                                                             |
| ---------------- | ------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| symbol           | STRING  | YES       |                                                                                                                                         |
| side             | ENUM    | YES       |                                                                                                                                         |
| positionSide     | ENUM    | NO        | Default `BOTH` for One-way Mode ; `LONG` or `SHORT` for Hedge Mode. It must be sent with Hedge Mode.                                    |
| type             | ENUM    | YES       |                                                                                                                                         |
| timeInForce      | ENUM    | NO        |                                                                                                                                         |
| quantity         | DECIMAL | YES       |                                                                                                                                         |
| reduceOnly       | STRING  | NO        | "true" or "false". default "false".                                                                                                     |
| price            | DECIMAL | NO        |                                                                                                                                         |
| newClientOrderId | STRING  | NO        | A unique id among open orders. Automatically generated if not sent. Can only be string following the rule: `^[\.A-Z\:/a-z0-9_-]{1,36}$` |
| stopPrice        | DECIMAL | NO        | Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders.                                                                |
| activationPrice  | DECIMAL | NO        | Used with `TRAILING_STOP_MARKET` orders, default as the latest price(supporting different `workingType`)                                |
| callbackRate     | DECIMAL | NO        | Used with `TRAILING_STOP_MARKET` orders, min 0.1, max 4 where 1 for 1%                                                                  |
| workingType      | ENUM    | NO        | stopPrice triggered by: "MARK\_PRICE", "CONTRACT\_PRICE". Default "CONTRACT\_PRICE"                                                     |
| priceProtect     | STRING  | NO        | "TRUE" or "FALSE", default "FALSE". Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders.                            |
| newOrderRespType | ENUM    | NO        | "ACK", "RESULT", default "ACK"                                                                                                          |

* Paremeter rules are same with `New Order`
* Batch orders are processed concurrently, and the order of matching is not guaranteed.
* The order of returned contents for batch orders is the same as the order of the order list.

### Query Order (USER\_DATA)

> **Response:**

```
{
  	"avgPrice": "0.00000",
  	"clientOrderId": "abc",
  	"cumQuote": "0",
  	"executedQty": "0",
  	"orderId": 1917641,
  	"origQty": "0.40",
  	"origType": "TRAILING_STOP_MARKET",
  	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "NEW",
  	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   // if Close-All
  	"symbol": "BTCUSDT",
  	"time": 1579276756075,				// order time
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
  	"updateTime": 1579276756075,		// update time
  	"workingType": "CONTRACT_PRICE",
  	"priceProtect": false            // if conditional order trigger is protected	
}
```

`GET /fapi/v1/order (HMAC SHA256)`

Check an order's status.

**Weight:** 1

* These orders will not be found:
  * order status is `CANCELED` or `EXPIRED`, **AND**
  * order has NO filled trade, **AND**
  * created time + 7 days < current time

**Parameters:**

| Name              | Type   | Mandatory | Description |
| ----------------- | ------ | --------- | ----------- |
| symbol            | STRING | YES       |             |
| orderId           | LONG   | NO        |             |
| origClientOrderId | STRING | NO        |             |
| recvWindow        | LONG   | NO        |             |
| timestamp         | LONG   | YES       |             |

Notes:

* Either `orderId` or `origClientOrderId` must be sent.

### Cancel Order (TRADE)

> **Response:**

```
{
 	"clientOrderId": "myOrder1",
 	"cumQty": "0",
 	"cumQuote": "0",
 	"executedQty": "0",
 	"orderId": 283194212,
 	"origQty": "11",
 	"origType": "TRAILING_STOP_MARKET",
  	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "CANCELED",
  	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   // if Close-All
  	"symbol": "BTCUSDT",
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
 	"updateTime": 1571110484038,
 	"workingType": "CONTRACT_PRICE",
 	"priceProtect": false            // if conditional order trigger is protected	
}
```

`DELETE /fapi/v1/order (HMAC SHA256)`

Cancel an active order.

**Weight:** 1

**Parameters:**

| Name              | Type   | Mandatory | Description |
| ----------------- | ------ | --------- | ----------- |
| symbol            | STRING | YES       |             |
| orderId           | LONG   | NO        |             |
| origClientOrderId | STRING | NO        |             |
| recvWindow        | LONG   | NO        |             |
| timestamp         | LONG   | YES       |             |

Either `orderId` or `origClientOrderId` must be sent.

### Cancel All Open Orders (TRADE)

> **Response:**

```
{
	"code": "200", 
	"msg": "The operation of cancel all open order is done."
}
```

`DELETE /fapi/v1/allOpenOrders (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | YES       |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

### Cancel Multiple Orders (TRADE)

> **Response:**

```
[
	{
	 	"clientOrderId": "myOrder1",
	 	"cumQty": "0",
	 	"cumQuote": "0",
	 	"executedQty": "0",
	 	"orderId": 283194212,
	 	"origQty": "11",
	 	"origType": "TRAILING_STOP_MARKET",
  		"price": "0",
  		"reduceOnly": false,
  		"side": "BUY",
  		"positionSide": "SHORT",
  		"status": "CANCELED",
  		"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  		"closePosition": false,   // if Close-All
  		"symbol": "BTCUSDT",
  		"timeInForce": "GTC",
  		"type": "TRAILING_STOP_MARKET",
  		"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  		"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
	 	"updateTime": 1571110484038,
	 	"workingType": "CONTRACT_PRICE",
	 	"priceProtect": false            // if conditional order trigger is protected	
	},
	{
		"code": -2011,
		"msg": "Unknown order sent."
	}
]
```

`DELETE /fapi/v1/batchOrders (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name                  | Type          | Mandatory | Description                                                                                              |
| --------------------- | ------------- | --------- | -------------------------------------------------------------------------------------------------------- |
| symbol                | STRING        | YES       |                                                                                                          |
| orderIdList           | LIST\<LONG>   | NO        | <p>max length 10<br>e.g. \[1234567,2345678]</p>                                                          |
| origClientOrderIdList | LIST\<STRING> | NO        | <p>max length 10<br>e.g. \["my\_id\_1","my\_id\_2"], encode the double quotes. No space after comma.</p> |
| recvWindow            | LONG          | NO        |                                                                                                          |
| timestamp             | LONG          | YES       |                                                                                                          |

Either `orderIdList` or `origClientOrderIdList` must be sent.

### Auto-Cancel All Open Orders (TRADE)

> **Response:**

```
{
	"symbol": "BTCUSDT", 
	"countdownTime": "100000"
}
```

Cancel all open orders of the specified symbol at the end of the specified countdown.

`POST /fapi/v1/countdownCancelAll (HMAC SHA256)`

**Weight:** 10

**Parameters:**

| Name          | Type   | Mandatory | Description                                              |
| ------------- | ------ | --------- | -------------------------------------------------------- |
| symbol        | STRING | YES       |                                                          |
| countdownTime | LONG   | YES       | countdown time, 1000 for 1 second. 0 to cancel the timer |
| recvWindow    | LONG   | NO        |                                                          |
| timestamp     | LONG   | YES       |                                                          |

* The endpoint should be called repeatedly as heartbeats so that the existing countdown time can be canceled and replaced by a new one.
* Example usage:\
  Call this endpoint at 30s intervals with an countdownTime of 120000 (120s).\
  If this endpoint is not called within 120 seconds, all your orders of the specified symbol will be automatically canceled.\
  If this endpoint is called with an countdownTime of 0, the countdown timer will be stopped.
* The system will check all countdowns **approximately every 10 milliseconds**, so please note that sufficient redundancy should be considered when using this function. We do not recommend setting the countdown time to be too precise or too small.

### Query Current Open Order (USER\_DATA)

> **Response:**

```
{
  	"avgPrice": "0.00000",				
  	"clientOrderId": "abc",				
  	"cumQuote": "0",						
  	"executedQty": "0",					
  	"orderId": 1917641,					
  	"origQty": "0.40",						
  	"origType": "TRAILING_STOP_MARKET",
  	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "NEW",
  	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   			// if Close-All
  	"symbol": "BTCUSDT",
  	"time": 1579276756075,				// order time
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order						
  	"updateTime": 1579276756075,		
  	"workingType": "CONTRACT_PRICE",
  	"priceProtect": false            // if conditional order trigger is protected			
}
```

`GET /fapi/v1/openOrder (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name              | Type   | Mandatory | Description |
| ----------------- | ------ | --------- | ----------- |
| symbol            | STRING | YES       |             |
| orderId           | LONG   | NO        |             |
| origClientOrderId | STRING | NO        |             |
| recvWindow        | LONG   | NO        |             |
| timestamp         | LONG   | YES       |             |

* Either`orderId` or `origClientOrderId` must be sent
* If the queried order has been filled or cancelled, the error message "Order does not exist" will be returned.

### Current All Open Orders (USER\_DATA)

> **Response:**

```
[
  {
  	"avgPrice": "0.00000",
  	"clientOrderId": "abc",
  	"cumQuote": "0",
  	"executedQty": "0",
  	"orderId": 1917641,
  	"origQty": "0.40",
  	"origType": "TRAILING_STOP_MARKET",
  	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "NEW",
  	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   // if Close-All
  	"symbol": "BTCUSDT",
  	"time": 1579276756075,				// order time
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
  	"updateTime": 1579276756075,		// update time
  	"workingType": "CONTRACT_PRICE",
  	"priceProtect": false            // if conditional order trigger is protected	
  }
]
```

`GET /fapi/v1/openOrders (HMAC SHA256)`

Get all open orders on a symbol. **Careful** when accessing this with no symbol.

**Weight:** 1 for a single symbol; **40** when the symbol parameter is omitted

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | NO        |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

* If the symbol is not sent, orders for all symbols will be returned in an array.

### All Orders (USER\_DATA)

> **Response:**

```
[
  {
   	"avgPrice": "0.00000",
  	"clientOrderId": "abc",
  	"cumQuote": "0",
  	"executedQty": "0",
  	"orderId": 1917641,
  	"origQty": "0.40",
  	"origType": "TRAILING_STOP_MARKET",
  	"price": "0",
  	"reduceOnly": false,
  	"side": "BUY",
  	"positionSide": "SHORT",
  	"status": "NEW",
  	"stopPrice": "9300",				// please ignore when order type is TRAILING_STOP_MARKET
  	"closePosition": false,   // if Close-All
  	"symbol": "BTCUSDT",
  	"time": 1579276756075,				// order time
  	"timeInForce": "GTC",
  	"type": "TRAILING_STOP_MARKET",
  	"activatePrice": "9020",			// activation price, only return with TRAILING_STOP_MARKET order
  	"priceRate": "0.3",					// callback rate, only return with TRAILING_STOP_MARKET order
  	"updateTime": 1579276756075,		// update time
  	"workingType": "CONTRACT_PRICE",
  	"priceProtect": false            // if conditional order trigger is protected	
  }
]
```

`GET /fapi/v1/allOrders (HMAC SHA256)`

Get all account orders; active, canceled, or filled.

* These orders will not be found:
  * order status is `CANCELED` or `EXPIRED`, **AND**
  * order has NO filled trade, **AND**
  * created time + 7 days < current time

**Weight:** 5

**Parameters:**

| Name       | Type   | Mandatory | Description            |
| ---------- | ------ | --------- | ---------------------- |
| symbol     | STRING | YES       |                        |
| orderId    | LONG   | NO        |                        |
| startTime  | LONG   | NO        |                        |
| endTime    | LONG   | NO        |                        |
| limit      | INT    | NO        | Default 500; max 1000. |
| recvWindow | LONG   | NO        |                        |
| timestamp  | LONG   | YES       |                        |

**Notes:**

* If `orderId` is set, it will get orders >= that `orderId`. Otherwise most recent orders are returned.
* The query time period must be less then 7 days( default as the recent 7 days).

### Futures Account Balance V2 (USER\_DATA)

> **Response:**

```
[
 	{
 		"accountAlias": "SgsR",    // unique account code
 		"asset": "USDT",  	// asset name
 		"balance": "122607.35137903", // wallet balance
 		"crossWalletBalance": "23.72469206", // crossed wallet balance
  		"crossUnPnl": "0.00000000"  // unrealized profit of crossed positions
  		"availableBalance": "23.72469206",       // available balance
  		"maxWithdrawAmount": "23.72469206",     // maximum amount for transfer out
  		"marginAvailable": true,    // whether the asset can be used as margin in Multi-Assets mode
  		"updateTime": 1617939110373
	}
]
```

`GET /fapi/v2/balance (HMAC SHA256)`

**Weight:** 5

**Parameters:**

| Name       | Type | Mandatory | Description |
| ---------- | ---- | --------- | ----------- |
| recvWindow | LONG | NO        |             |
| timestamp  | LONG | YES       |             |

### Account Information V4 (USER\_DATA)

> **Response:**

```
{
   "feeTier": 0, // account commisssion tier
   "canTrade": true, // if can trade
   "canDeposit": true, // if can transfer in asset
   "canWithdraw": true, // if can transfer out asset
   "updateTime": 0,
   "totalInitialMargin": "0.00000000", // total initial margin required with current mark price (useless with isolated positions), only for USDT asset
   "totalMaintMargin": "0.00000000", // total maintenance margin required, only for USDT asset
   "totalWalletBalance": "23.72469206", // total wallet balance, using BidRate/AskRate for value caculation under multi-asset mode
   "totalUnrealizedProfit": "0.00000000", // total unrealized profit in USDT
   "totalMarginBalance": "23.72469206", // total margin balance, using BidRate/AskRate for value caculation under multi-asset mode
   "totalPositionInitialMargin": "0.00000000", // initial margin required for positions with current mark price, only for USDT asset
   "totalOpenOrderInitialMargin": "0.00000000", // initial margin required for open orders with current mark price, only for USDT asset
   "totalCrossWalletBalance": "23.72469206", // crossed wallet balance, using BidRate/AskRate for value caculation under multi-asset mode
   "totalCrossUnPnl": "0.00000000", // unrealized profit of crossed positions in USDT
   "availableBalance": "23.72469206", // available balance, only for USDT asset
   "maxWithdrawAmount": "23.72469206" // maximum amount for transfer out, using BidRate for value caculation under multi-asset mode
   "assets": [
       {
           "asset": "USDT", // asset name
           "walletBalance": "23.72469206", // wallet balance
           "unrealizedProfit": "0.00000000", // unrealized profit
           "marginBalance": "23.72469206", // margin balance
           "maintMargin": "0.00000000", // maintenance margin required
           "initialMargin": "0.00000000", // total initial margin required with current mark price
           "positionInitialMargin": "0.00000000", //initial margin required for positions with current mark price
           "openOrderInitialMargin": "0.00000000", // initial margin required for open orders with current mark price
           "crossWalletBalance": "23.72469206", // crossed wallet balance
           "crossUnPnl": "0.00000000" // unrealized profit of crossed positions
           "availableBalance": "23.72469206", // available balance
           "maxWithdrawAmount": "23.72469206", // maximum amount for transfer out
           "marginAvailable": true, // whether the asset can be used as margin in Multi-Assets mode
           "updateTime": 1625474304765 // last update time
       },
       {
           "asset": "BUSD", // asset name
           "walletBalance": "103.12345678", // wallet balance
           "unrealizedProfit": "0.00000000", // unrealized profit
           "marginBalance": "103.12345678", // margin balance
           "maintMargin": "0.00000000", // maintenance margin required
           "initialMargin": "0.00000000", // total initial margin required with current mark price
           "positionInitialMargin": "0.00000000", //initial margin required for positions with current mark price
           "openOrderInitialMargin": "0.00000000", // initial margin required for open orders with current mark price
           "crossWalletBalance": "103.12345678", // crossed wallet balance
           "crossUnPnl": "0.00000000" // unrealized profit of crossed positions
           "availableBalance": "103.12345678", // available balance
           "maxWithdrawAmount": "103.12345678", // maximum amount for transfer out
           "marginAvailable": true, // whether the asset can be used as margin in Multi-Assets mode
           "updateTime": 1625474304765 // last update time
       }
   ],
   "positions": [ // positions of all symbols in the market are returned
       // only "BOTH" positions will be returned with One-way mode
       // only "LONG" and "SHORT" positions will be returned with Hedge mode
       {
           "symbol": "BTCUSDT", // symbol name
           "initialMargin": "0", // initial margin required with current mark price
           "maintMargin": "0", // maintenance margin required
           "unrealizedProfit": "0.00000000", // unrealized profit
           "positionInitialMargin": "0", // initial margin required for positions with current mark price
           "openOrderInitialMargin": "0", // initial margin required for open orders with current mark price
           "leverage": "100", // current initial leverage
           "isolated": true, // if the position is isolated
           "entryPrice": "0.00000", // average entry price
           "maxNotional": "250000", // maximum available notional with current leverage
           "positionSide": "BOTH", // position side
           "positionAmt": "0", // position amount
           "updateTime": 0 // last update time
       }
   ]
}
```

`GET /fapi/v4/account (HMAC SHA256)`

Get current account information.

**Weight:** 5

**Parameters:**

| Name       | Type | Mandatory | Description |
| ---------- | ---- | --------- | ----------- |
| recvWindow | LONG | NO        |             |
| timestamp  | LONG | YES       |             |

### Change Initial Leverage (TRADE)

> **Response:**

```
{
 	"leverage": 21,
 	"maxNotionalValue": "1000000",
 	"symbol": "BTCUSDT"
}
```

`POST /fapi/v1/leverage (HMAC SHA256)`

Change user's initial leverage of specific symbol market.

**Weight:** 1

**Parameters:**

| Name       | Type   | Mandatory | Description                                |
| ---------- | ------ | --------- | ------------------------------------------ |
| symbol     | STRING | YES       |                                            |
| leverage   | INT    | YES       | target initial leverage: int from 1 to 125 |
| recvWindow | LONG   | NO        |                                            |
| timestamp  | LONG   | YES       |                                            |

### Change Margin Type (TRADE)

> **Response:**

```
{
	"code": 200,
	"msg": "success"
}
```

`POST /fapi/v1/marginType (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name       | Type   | Mandatory | Description       |
| ---------- | ------ | --------- | ----------------- |
| symbol     | STRING | YES       |                   |
| marginType | ENUM   | YES       | ISOLATED, CROSSED |
| recvWindow | LONG   | NO        |                   |
| timestamp  | LONG   | YES       |                   |

### Modify Isolated Position Margin (TRADE)

> **Response:**

```
{
	"amount": 100.0,
  	"code": 200,
  	"msg": "Successfully modify position margin.",
  	"type": 1
}
```

`POST /fapi/v1/positionMargin (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name         | Type    | Mandatory | Description                                                                                          |
| ------------ | ------- | --------- | ---------------------------------------------------------------------------------------------------- |
| symbol       | STRING  | YES       |                                                                                                      |
| positionSide | ENUM    | NO        | Default `BOTH` for One-way Mode ; `LONG` or `SHORT` for Hedge Mode. It must be sent with Hedge Mode. |
| amount       | DECIMAL | YES       |                                                                                                      |
| type         | INT     | YES       | 1: Add position margin，2: Reduce position margin                                                     |
| recvWindow   | LONG    | NO        |                                                                                                      |
| timestamp    | LONG    | YES       |                                                                                                      |

* Only for isolated symbol

### Get Position Margin Change History (TRADE)

> **Response:**

```
[
	{
		"amount": "23.36332311",
	  	"asset": "USDT",
	  	"symbol": "BTCUSDT",
	  	"time": 1578047897183,
	  	"type": 1,
	  	"positionSide": "BOTH"
	},
	{
		"amount": "100",
	  	"asset": "USDT",
	  	"symbol": "BTCUSDT",
	  	"time": 1578047900425,
	  	"type": 1,
	  	"positionSide": "LONG"
	}
]
```

`GET /fapi/v1/positionMargin/history (HMAC SHA256)`

**Weight:** 1

**Parameters:**

| Name       | Type   | Mandatory | Description                                      |
| ---------- | ------ | --------- | ------------------------------------------------ |
| symbol     | STRING | YES       |                                                  |
| type       | INT    | NO        | 1: Add position margin，2: Reduce position margin |
| startTime  | LONG   | NO        |                                                  |
| endTime    | LONG   | NO        |                                                  |
| limit      | INT    | NO        | Default: 500                                     |
| recvWindow | LONG   | NO        |                                                  |
| timestamp  | LONG   | YES       |                                                  |

### Position Information V2 (USER\_DATA)

> **Response:**

> For One-way position mode:

```
[
  	{
  		"entryPrice": "0.00000",
  		"marginType": "isolated", 
  		"isAutoAddMargin": "false",
  		"isolatedMargin": "0.00000000",	
  		"leverage": "10", 
  		"liquidationPrice": "0", 
  		"markPrice": "6679.50671178",	
  		"maxNotionalValue": "20000000", 
  		"positionAmt": "0.000", 
  		"symbol": "BTCUSDT", 
  		"unRealizedProfit": "0.00000000", 
  		"positionSide": "BOTH",
  		"updateTime": 0
  	}
]
```

> For Hedge position mode:

```
[
  	{
  		"entryPrice": "6563.66500", 
  		"marginType": "isolated", 
  		"isAutoAddMargin": "false",
  		"isolatedMargin": "15517.54150468",
  		"leverage": "10",
  		"liquidationPrice": "5930.78",
  		"markPrice": "6679.50671178",	
  		"maxNotionalValue": "20000000", 
  		"positionAmt": "20.000", 
  		"symbol": "BTCUSDT", 
  		"unRealizedProfit": "2316.83423560"
  		"positionSide": "LONG", 
  		"updateTime": 1625474304765
  	},
  	{
  		"entryPrice": "0.00000",
  		"marginType": "isolated", 
  		"isAutoAddMargin": "false",
  		"isolatedMargin": "5413.95799991", 
  		"leverage": "10", 
  		"liquidationPrice": "7189.95", 
  		"markPrice": "6679.50671178",	
  		"maxNotionalValue": "20000000", 
  		"positionAmt": "-10.000", 
  		"symbol": "BTCUSDT",
  		"unRealizedProfit": "-1156.46711780" 
  		"positionSide": "SHORT",
  		"updateTime": 0
  	}
]
```

`GET /fapi/v2/positionRisk (HMAC SHA256)`

Get current position information.

**Weight:** 5

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | NO        |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

**Note**\
Please use with user data stream `ACCOUNT_UPDATE` to meet your timeliness and accuracy needs.

### Account Trade List (USER\_DATA)

> **Response:**

```
[
  {
  	"buyer": false,
  	"commission": "-0.07819010",
  	"commissionAsset": "USDT",
  	"id": 698759,
  	"maker": false,
  	"orderId": 25851813,
  	"price": "7819.01",
  	"qty": "0.002",
  	"quoteQty": "15.63802",
  	"realizedPnl": "-0.91539999",
  	"side": "SELL",
  	"positionSide": "SHORT",
  	"symbol": "BTCUSDT",
  	"time": 1569514978020
  }
]
```

`GET /fapi/v1/userTrades (HMAC SHA256)`

Get trades for a specific account and symbol.

**Weight:** 5

**Parameters:**

| Name       | Type   | Mandatory | Description                                              |
| ---------- | ------ | --------- | -------------------------------------------------------- |
| symbol     | STRING | YES       |                                                          |
| startTime  | LONG   | NO        |                                                          |
| endTime    | LONG   | NO        |                                                          |
| fromId     | LONG   | NO        | Trade id to fetch from. Default gets most recent trades. |
| limit      | INT    | NO        | Default 500; max 1000.                                   |
| recvWindow | LONG   | NO        |                                                          |
| timestamp  | LONG   | YES       |                                                          |

* If `startTime` and `endTime` are both not sent, then the last 7 days' data will be returned.
* The time between `startTime` and `endTime` cannot be longer than 7 days.
* The parameter `fromId` cannot be sent with `startTime` or `endTime`.

### Get Income History(USER\_DATA)

> **Response:**

```
[
	{
    	"symbol": "",					// trade symbol, if existing
    	"incomeType": "TRANSFER",	// income type
    	"income": "-0.37500000",  // income amount
    	"asset": "USDT",				// income asset
    	"info":"TRANSFER",			// extra information
    	"time": 1570608000000,		
    	"tranId":"9689322392",		// transaction id
    	"tradeId":""					// trade id, if existing
	},
	{
   		"symbol": "BTCUSDT",
    	"incomeType": "COMMISSION", 
    	"income": "-0.01000000",
    	"asset": "USDT",
    	"info":"COMMISSION",
    	"time": 1570636800000,
    	"tranId":"9689322392",
    	"tradeId":"2059192"
	}
]
```

`GET /fapi/v1/income (HMAC SHA256)`

**Weight:** 30

**Parameters:**

| Name       | Type   | Mandatory | Description                                                                                                                           |
| ---------- | ------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| symbol     | STRING | NO        |                                                                                                                                       |
| incomeType | STRING | NO        | "TRANSFER"，"WELCOME\_BONUS", "REALIZED\_PNL"，"FUNDING\_FEE", "COMMISSION", "INSURANCE\_CLEAR", and "MARKET\_MERCHANT\_RETURN\_REWARD" |
| startTime  | LONG   | NO        | Timestamp in ms to get funding from INCLUSIVE.                                                                                        |
| endTime    | LONG   | NO        | Timestamp in ms to get funding until INCLUSIVE.                                                                                       |
| limit      | INT    | NO        | Default 100; max 1000                                                                                                                 |
| recvWindow | LONG   | NO        |                                                                                                                                       |
| timestamp  | LONG   | YES       |                                                                                                                                       |

* If neither `startTime` nor `endTime` is sent, the recent 7-day data will be returned.
* If `incomeType` is not sent, all kinds of flow will be returned
* "trandId" is unique in the same incomeType for a user

### Notional and Leverage Brackets (USER\_DATA)

> **Response:**

```
[
    {
        "symbol": "ETHUSDT",
        "brackets": [
            {
                "bracket": 1,   // Notional bracket
                "initialLeverage": 75,  // Max initial leverage for this bracket
                "notionalCap": 10000,  // Cap notional of this bracket
                "notionalFloor": 0,  // Notional threshold of this bracket 
                "maintMarginRatio": 0.0065, // Maintenance ratio for this bracket
                "cum":0 // Auxiliary number for quick calculation 
               
            },
        ]
    }
]
```

> **OR** (if symbol sent)

```
{
    "symbol": "ETHUSDT",
    "brackets": [
        {
            "bracket": 1,
            "initialLeverage": 75,
            "notionalCap": 10000,
            "notionalFloor": 0,
            "maintMarginRatio": 0.0065,
            "cum":0
        },
    ]
}
```

`GET /fapi/v1/leverageBracket`

**Weight:** 1

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | NO        |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

### Position ADL Quantile Estimation (USER\_DATA)

> **Response:**

```
[
	{
		"symbol": "ETHUSDT", 
		"adlQuantile": 
			{
				// if the positions of the symbol are crossed margined in Hedge Mode, "LONG" and "SHORT" will be returned a same quantile value, and "HEDGE" will be returned instead of "BOTH".
				"LONG": 3,  
				"SHORT": 3, 
				"HEDGE": 0   // only a sign, ignore the value
			}
		},
 	{
 		"symbol": "BTCUSDT", 
 		"adlQuantile": 
 			{
 				// for positions of the symbol are in One-way Mode or isolated margined in Hedge Mode
 				"LONG": 1, 	// adl quantile for "LONG" position in hedge mode
 				"SHORT": 2, 	// adl qauntile for "SHORT" position in hedge mode
 				"BOTH": 0		// adl qunatile for position in one-way mode
 			}
 	}
 ]
```

`GET /fapi/v1/adlQuantile`

**Weight:** 5

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | NO        |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

* Values update every 30s.
* Values 0, 1, 2, 3, 4 shows the queue position and possibility of ADL from low to high.
* For positions of the symbol are in One-way Mode or isolated margined in Hedge Mode, "LONG", "SHORT", and "BOTH" will be returned to show the positions' adl quantiles of different position sides.
* If the positions of the symbol are crossed margined in Hedge Mode:
  * "HEDGE" as a sign will be returned instead of "BOTH";
  * A same value caculated on unrealized pnls on long and short sides' positions will be shown for "LONG" and "SHORT" when there are positions in both of long and short sides.

### User's Force Orders (USER\_DATA)

> **Response:**

```
[
  {
  	"orderId": 6071832819, 
  	"symbol": "BTCUSDT", 
  	"status": "FILLED", 
  	"clientOrderId": "autoclose-1596107620040000020", 
  	"price": "10871.09", 
  	"avgPrice": "10913.21000", 
  	"origQty": "0.001", 
  	"executedQty": "0.001", 
  	"cumQuote": "10.91321", 
  	"timeInForce": "IOC", 
  	"type": "LIMIT", 
  	"reduceOnly": false, 
  	"closePosition": false, 
  	"side": "SELL", 
  	"positionSide": "BOTH", 
  	"stopPrice": "0", 
  	"workingType": "CONTRACT_PRICE", 
  	"origType": "LIMIT", 
  	"time": 1596107620044, 
  	"updateTime": 1596107620087
  }
  {
   	"orderId": 6072734303, 
   	"symbol": "BTCUSDT", 
   	"status": "FILLED", 
   	"clientOrderId": "adl_autoclose", 
   	"price": "11023.14", 
   	"avgPrice": "10979.82000", 
   	"origQty": "0.001", 
   	"executedQty": "0.001", 
   	"cumQuote": "10.97982", 
   	"timeInForce": "GTC", 
   	"type": "LIMIT", 
   	"reduceOnly": false, 
   	"closePosition": false, 
   	"side": "BUY", 
   	"positionSide": "SHORT", 
   	"stopPrice": "0", 
   	"workingType": "CONTRACT_PRICE", 
   	"origType": "LIMIT", 
   	"time": 1596110725059, 
   	"updateTime": 1596110725071
  }
]
```

`GET /fapi/v1/forceOrders`

**Weight:** 20 with symbol, 50 without symbol

**Parameters:**

| Name          | Type   | Mandatory | Description                                                 |
| ------------- | ------ | --------- | ----------------------------------------------------------- |
| symbol        | STRING | NO        |                                                             |
| autoCloseType | ENUM   | NO        | "LIQUIDATION" for liquidation orders, "ADL" for ADL orders. |
| startTime     | LONG   | NO        |                                                             |
| endTime       | LONG   | NO        |                                                             |
| limit         | INT    | NO        | Default 50; max 100.                                        |
| recvWindow    | LONG   | NO        |                                                             |
| timestamp     | LONG   | YES       |                                                             |

* If "autoCloseType" is not sent, orders with both of the types will be returned
* If "startTime" is not sent, data within 7 days before "endTime" can be queried

### User Commission Rate (USER\_DATA)

> **Response:**

```
{
	"symbol": "BTCUSDT",
  	"makerCommissionRate": "0.0002",  // 0.02%
  	"takerCommissionRate": "0.0004"   // 0.04%
}
```

`GET /fapi/v1/commissionRate (HMAC SHA256)`

**Weight:** 20

**Parameters:**

| Name       | Type   | Mandatory | Description |
| ---------- | ------ | --------- | ----------- |
| symbol     | STRING | YES       |             |
| recvWindow | LONG   | NO        |             |
| timestamp  | LONG   | YES       |             |

## User Data Streams

* The base API endpoint is: [**https://fapi.asterdex.com**](https://fapi.asterdex.com/)
* A User Data Stream `listenKey` is valid for 60 minutes after creation.
* Doing a `PUT` on a `listenKey` will extend its validity for 60 minutes.
* Doing a `DELETE` on a `listenKey` will close the stream and invalidate the `listenKey`.
* Doing a `POST` on an account with an active `listenKey` will return the currently active `listenKey` and extend its validity for 60 minutes.
* The baseurl for websocket is **wss\://fstream.asterdex.com**
* User Data Streams are accessed at **/ws/\<listenKey>**
* User data stream payloads are **not guaranteed** to be in order during heavy periods; **make sure to order your updates using E**
* A single connection to **fstream.asterdex.com** is only valid for 24 hours; expect to be disconnected at the 24 hour mark

### Start User Data Stream (USER\_STREAM)

> **Response:**

```
{
  "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
}
```

`POST /fapi/v1/listenKey`

Start a new user data stream. The stream will close after 60 minutes unless a keepalive is sent. If the account has an active `listenKey`, that `listenKey` will be returned and its validity will be extended for 60 minutes.

**Weight:** 1

**Parameters:**

None

### Keepalive User Data Stream (USER\_STREAM)

> **Response:**

```
{}
```

`PUT /fapi/v1/listenKey`

Keepalive a user data stream to prevent a time out. User data streams will close after 60 minutes. It's recommended to send a ping about every 60 minutes.

**Weight:** 1

**Parameters:**

None

### Close User Data Stream (USER\_STREAM)

> **Response:**

```
{}
```

`DELETE /fapi/v1/listenKey`

Close out a user data stream.

**Weight:** 1

**Parameters:**

None

### Event: User Data Stream Expired

> **Payload:**

```
{
	'e': 'listenKeyExpired',      // event type
	'E': 1576653824250				// event time
}
```

When the `listenKey` used for the user data stream turns expired, this event will be pushed.

**Notice:**

* This event is not related to the websocket disconnection.
* This event will be received only when a valid `listenKey` in connection got expired.
* No more user data event will be updated after this event received until a new valid `listenKey` used.

### Event: Margin Call

> **Payload:**

```
{
    "e":"MARGIN_CALL",    	// Event Type
    "E":1587727187525,		// Event Time
    "cw":"3.16812045",		// Cross Wallet Balance. Only pushed with crossed position margin call
    "p":[					// Position(s) of Margin Call
      {
        "s":"ETHUSDT",		// Symbol
        "ps":"LONG",		// Position Side
        "pa":"1.327",		// Position Amount
        "mt":"CROSSED",		// Margin Type
        "iw":"0",			// Isolated Wallet (if isolated position)
        "mp":"187.17127",	// Mark Price
        "up":"-1.166074",	// Unrealized PnL
        "mm":"1.614445"		// Maintenance Margin Required
      }
    ]
}  
 
```

* When the user's position risk ratio is too high, this stream will be pushed.
* This message is only used as risk guidance information and is not recommended for investment strategies.
* In the case of a highly volatile market, there may be the possibility that the user's position has been liquidated at the same time when this stream is pushed out.

### Event: Balance and Position Update

> **Payload:**

```
{
  "e": "ACCOUNT_UPDATE",				// Event Type
  "E": 1564745798939,            		// Event Time
  "T": 1564745798938 ,           		// Transaction
  "a":                          		// Update Data
    {
      "m":"ORDER",						// Event reason type
      "B":[                     		// Balances
        {
          "a":"USDT",           		// Asset
          "wb":"122624.12345678",    	// Wallet Balance
          "cw":"100.12345678",			// Cross Wallet Balance
          "bc":"50.12345678"			// Balance Change except PnL and Commission
        },
        {
          "a":"BUSD",           
          "wb":"1.00000000",
          "cw":"0.00000000",         
          "bc":"-49.12345678"
        }
      ],
      "P":[
        {
          "s":"BTCUSDT",          	// Symbol
          "pa":"0",               	// Position Amount
          "ep":"0.00000",            // Entry Price
          "cr":"200",             	// (Pre-fee) Accumulated Realized
          "up":"0",						// Unrealized PnL
          "mt":"isolated",				// Margin Type
          "iw":"0.00000000",			// Isolated Wallet (if isolated position)
          "ps":"BOTH"					// Position Side
        }，
        {
        	"s":"BTCUSDT",
        	"pa":"20",
        	"ep":"6563.66500",
        	"cr":"0",
        	"up":"2850.21200",
        	"mt":"isolated",
        	"iw":"13200.70726908",
        	"ps":"LONG"
      	 },
        {
        	"s":"BTCUSDT",
        	"pa":"-10",
        	"ep":"6563.86000",
        	"cr":"-45.04000000",
        	"up":"-1423.15600",
        	"mt":"isolated",
        	"iw":"6570.42511771",
        	"ps":"SHORT"
        }
      ]
    }
}
```

Event type is `ACCOUNT_UPDATE`.

* When balance or position get updated, this event will be pushed.
  * `ACCOUNT_UPDATE` will be pushed only when update happens on user's account, including changes on balances, positions, or margin type.
  * Unfilled orders or cancelled orders will not make the event `ACCOUNT_UPDATE` pushed, since there's no change on positions.
  * Only positions of symbols with non-zero isolatd wallet or non-zero position amount will be pushed in the "position" part of the event `ACCOUNT_UPDATE` when any position changes.
* When "FUNDING FEE" changes to the user's balance, the event will be pushed with the brief message:
  * When "FUNDING FEE" occurs in a **crossed position**, `ACCOUNT_UPDATE` will be pushed with only the balance `B`(including the "FUNDING FEE" asset only), without any position `P` message.
  * When "FUNDING FEE" occurs in an **isolated position**, `ACCOUNT_UPDATE` will be pushed with only the balance `B`(including the "FUNDING FEE" asset only) and the relative position message `P`( including the isolated position on which the "FUNDING FEE" occurs only, without any other position message).
* The field "m" represents the reason type for the event and may shows the following possible types:
  * DEPOSIT
  * WITHDRAW
  * ORDER
  * FUNDING\_FEE
  * WITHDRAW\_REJECT
  * ADJUSTMENT
  * INSURANCE\_CLEAR
  * ADMIN\_DEPOSIT
  * ADMIN\_WITHDRAW
  * MARGIN\_TRANSFER
  * MARGIN\_TYPE\_CHANGE
  * ASSET\_TRANSFER
  * OPTIONS\_PREMIUM\_FEE
  * OPTIONS\_SETTLE\_PROFIT
  * AUTO\_EXCHANGE
* The field "bc" represents the balance change except for PnL and commission.

### Event: Order Update

> **Payload:**

```
{
  
  "e":"ORDER_TRADE_UPDATE",		// Event Type
  "E":1568879465651,			// Event Time
  "T":1568879465650,			// Transaction Time
  "o":{								
    "s":"BTCUSDT",				// Symbol
    "c":"TEST",					// Client Order Id
      // special client order id:
      // starts with "autoclose-": liquidation order
      // "adl_autoclose": ADL auto close order
    "S":"SELL",					// Side
    "o":"TRAILING_STOP_MARKET",	// Order Type
    "f":"GTC",					// Time in Force
    "q":"0.001",				// Original Quantity
    "p":"0",					// Original Price
    "ap":"0",					// Average Price
    "sp":"7103.04",				// Stop Price. Please ignore with TRAILING_STOP_MARKET order
    "x":"NEW",					// Execution Type
    "X":"NEW",					// Order Status
    "i":8886774,				// Order Id
    "l":"0",					// Order Last Filled Quantity
    "z":"0",					// Order Filled Accumulated Quantity
    "L":"0",					// Last Filled Price
    "N":"USDT",            	// Commission Asset, will not push if no commission
    "n":"0",               	// Commission, will not push if no commission
    "T":1568879465651,			// Order Trade Time
    "t":0,			        	// Trade Id
    "b":"0",			    	// Bids Notional
    "a":"9.91",					// Ask Notional
    "m":false,					// Is this trade the maker side?
    "R":false,					// Is this reduce only
    "wt":"CONTRACT_PRICE", 		// Stop Price Working Type
    "ot":"TRAILING_STOP_MARKET",	// Original Order Type
    "ps":"LONG",						// Position Side
    "cp":false,						// If Close-All, pushed with conditional order
    "AP":"7476.89",				// Activation Price, only puhed with TRAILING_STOP_MARKET order
    "cr":"5.0",					// Callback Rate, only puhed with TRAILING_STOP_MARKET order
    "rp":"0"							// Realized Profit of the trade
  }
  
}
```

When new order created, order status changed will push such event. event type is `ORDER_TRADE_UPDATE`.

**Side**

* BUY
* SELL

**Order Type**

* MARKET
* LIMIT
* STOP
* TAKE\_PROFIT
* LIQUIDATION

**Execution Type**

* NEW
* CANCELED
* CALCULATED - Liquidation Execution
* EXPIRED
* TRADE

**Order Status**

* NEW
* PARTIALLY\_FILLED
* FILLED
* CANCELED
* EXPIRED
* NEW\_INSURANCE - Liquidation with Insurance Fund
* NEW\_ADL - Counterparty Liquidation\`

**Time in force**

* GTC
* IOC
* FOK
* GTX

**Working Type**

* MARK\_PRICE
* CONTRACT\_PRICE

### Event: Account Configuration Update previous Leverage Update

> **Payload:**

```
{
    "e":"ACCOUNT_CONFIG_UPDATE",       // Event Type
    "E":1611646737479,		           // Event Time
    "T":1611646737476,		           // Transaction Time
    "ac":{								
    "s":"BTCUSDT",					   // symbol
    "l":25						       // leverage
     
    }
}  
 
```

> **Or**

```
{
    "e":"ACCOUNT_CONFIG_UPDATE",       // Event Type
    "E":1611646737479,		           // Event Time
    "T":1611646737476,		           // Transaction Time
    "ai":{							   // User's Account Configuration
    "j":true						   // Multi-Assets Mode
    }
}  
```

When the account configuration is changed, the event type will be pushed as `ACCOUNT_CONFIG_UPDATE`

When the leverage of a trade pair changes, the payload will contain the object `ac` to represent the account configuration of the trade pair, where `s` represents the specific trade pair and `l` represents the leverage

When the user Multi-Assets margin mode changes the payload will contain the object `ai` representing the user account configuration, where `j` represents the user Multi-Assets margin mode

## Error Codes

> Here is the error JSON payload:

```
{
  "code":-1121,
  "msg":"Invalid symbol."
}
```

Errors consist of two parts: an error code and a message.\
Codes are universal,but messages can vary.

### 10xx - General Server or Network issues

> -1000 UNKNOWN

* An unknown error occured while processing the request.

> -1001 DISCONNECTED

* Internal error; unable to process your request. Please try again.

> -1002 UNAUTHORIZED

* You are not authorized to execute this request.

> -1003 TOO\_MANY\_REQUESTS

* Too many requests queued.
* Too many requests; please use the websocket for live updates.
* Too many requests; current limit is %s requests per minute. Please use the websocket for live updates to avoid polling the API.
* Way too many requests; IP banned until %s. Please use the websocket for live updates to avoid bans.

> -1004 DUPLICATE\_IP

* This IP is already on the white list

> -1005 NO\_SUCH\_IP

* No such IP has been white listed

> -1006 UNEXPECTED\_RESP

* An unexpected response was received from the message bus. Execution status unknown.

> -1007 TIMEOUT

* Timeout waiting for response from backend server. Send status unknown; execution status unknown.

> -1010 ERROR\_MSG\_RECEIVED

* ERROR\_MSG\_RECEIVED.

> -1011 NON\_WHITE\_LIST

* This IP cannot access this route.

> -1013 INVALID\_MESSAGE

* INVALID\_MESSAGE.

> -1014 UNKNOWN\_ORDER\_COMPOSITION

* Unsupported order combination.

> -1015 TOO\_MANY\_ORDERS

* Too many new orders.
* Too many new orders; current limit is %s orders per %s.

> -1016 SERVICE\_SHUTTING\_DOWN

* This service is no longer available.

> -1020 UNSUPPORTED\_OPERATION

* This operation is not supported.

> -1021 INVALID\_TIMESTAMP

* Timestamp for this request is outside of the recvWindow.
* Timestamp for this request was 1000ms ahead of the server's time.

> -1022 INVALID\_SIGNATURE

* Signature for this request is not valid.

> -1023 START\_TIME\_GREATER\_THAN\_END\_TIME

* Start time is greater than end time.

### 11xx - Request issues

> -1100 ILLEGAL\_CHARS

* Illegal characters found in a parameter.
* Illegal characters found in parameter '%s'; legal range is '%s'.

> -1101 TOO\_MANY\_PARAMETERS

* Too many parameters sent for this endpoint.
* Too many parameters; expected '%s' and received '%s'.
* Duplicate values for a parameter detected.

> -1102 MANDATORY\_PARAM\_EMPTY\_OR\_MALFORMED

* A mandatory parameter was not sent, was empty/null, or malformed.
* Mandatory parameter '%s' was not sent, was empty/null, or malformed.
* Param '%s' or '%s' must be sent, but both were empty/null!

> -1103 UNKNOWN\_PARAM

* An unknown parameter was sent.

> -1104 UNREAD\_PARAMETERS

* Not all sent parameters were read.
* Not all sent parameters were read; read '%s' parameter(s) but was sent '%s'.

> -1105 PARAM\_EMPTY

* A parameter was empty.
* Parameter '%s' was empty.

> -1106 PARAM\_NOT\_REQUIRED

* A parameter was sent when not required.
* Parameter '%s' sent when not required.

> -1108 BAD\_ASSET

* Invalid asset.

> -1109 BAD\_ACCOUNT

* Invalid account.

> -1110 BAD\_INSTRUMENT\_TYPE

* Invalid symbolType.

> -1111 BAD\_PRECISION

* Precision is over the maximum defined for this asset.

> -1112 NO\_DEPTH

* No orders on book for symbol.

> -1113 WITHDRAW\_NOT\_NEGATIVE

* Withdrawal amount must be negative.

> -1114 TIF\_NOT\_REQUIRED

* TimeInForce parameter sent when not required.

> -1115 INVALID\_TIF

* Invalid timeInForce.

> -1116 INVALID\_ORDER\_TYPE

* Invalid orderType.

> -1117 INVALID\_SIDE

* Invalid side.

> -1118 EMPTY\_NEW\_CL\_ORD\_ID

* New client order ID was empty.

> -1119 EMPTY\_ORG\_CL\_ORD\_ID

* Original client order ID was empty.

> -1120 BAD\_INTERVAL

* Invalid interval.

> -1121 BAD\_SYMBOL

* Invalid symbol.

> -1125 INVALID\_LISTEN\_KEY

* This listenKey does not exist.

> -1127 MORE\_THAN\_XX\_HOURS

* Lookup interval is too big.
* More than %s hours between startTime and endTime.

> -1128 OPTIONAL\_PARAMS\_BAD\_COMBO

* Combination of optional parameters invalid.

> -1130 INVALID\_PARAMETER

* Invalid data sent for a parameter.
* Data sent for parameter '%s' is not valid.

> -1136 INVALID\_NEW\_ORDER\_RESP\_TYPE

* Invalid newOrderRespType.

### 20xx - Processing Issues

> -2010 NEW\_ORDER\_REJECTED

* NEW\_ORDER\_REJECTED

> -2011 CANCEL\_REJECTED

* CANCEL\_REJECTED

> -2013 NO\_SUCH\_ORDER

* Order does not exist.

> -2014 BAD\_API\_KEY\_FMT

* API-key format invalid.

> -2015 REJECTED\_MBX\_KEY

* Invalid API-key, IP, or permissions for action.

> -2016 NO\_TRADING\_WINDOW

* No trading window could be found for the symbol. Try ticker/24hrs instead.

> -2018 BALANCE\_NOT\_SUFFICIENT

* Balance is insufficient.

> -2019 MARGIN\_NOT\_SUFFICIEN

* Margin is insufficient.

> -2020 UNABLE\_TO\_FILL

* Unable to fill.

> -2021 ORDER\_WOULD\_IMMEDIATELY\_TRIGGER

* Order would immediately trigger.

> -2022 REDUCE\_ONLY\_REJECT

* ReduceOnly Order is rejected.

> -2023 USER\_IN\_LIQUIDATION

* User in liquidation mode now.

> -2024 POSITION\_NOT\_SUFFICIENT

* Position is not sufficient.

> -2025 MAX\_OPEN\_ORDER\_EXCEEDED

* Reach max open order limit.

> -2026 REDUCE\_ONLY\_ORDER\_TYPE\_NOT\_SUPPORTED

* This OrderType is not supported when reduceOnly.

> -2027 MAX\_LEVERAGE\_RATIO

* Exceeded the maximum allowable position at current leverage.

> -2028 MIN\_LEVERAGE\_RATIO

* Leverage is smaller than permitted: insufficient margin balance.

### 40xx - Filters and other Issues

> -4000 INVALID\_ORDER\_STATUS

* Invalid order status.

> -4001 PRICE\_LESS\_THAN\_ZERO

* Price less than 0.

> -4002 PRICE\_GREATER\_THAN\_MAX\_PRICE

* Price greater than max price.

> -4003 QTY\_LESS\_THAN\_ZERO

* Quantity less than zero.

> -4004 QTY\_LESS\_THAN\_MIN\_QTY

* Quantity less than min quantity.

> -4005 QTY\_GREATER\_THAN\_MAX\_QTY

* Quantity greater than max quantity.

> -4006 STOP\_PRICE\_LESS\_THAN\_ZERO

* Stop price less than zero.

> -4007 STOP\_PRICE\_GREATER\_THAN\_MAX\_PRICE

* Stop price greater than max price.

> -4008 TICK\_SIZE\_LESS\_THAN\_ZERO

* Tick size less than zero.

> -4009 MAX\_PRICE\_LESS\_THAN\_MIN\_PRICE

* Max price less than min price.

> -4010 MAX\_QTY\_LESS\_THAN\_MIN\_QTY

* Max qty less than min qty.

> -4011 STEP\_SIZE\_LESS\_THAN\_ZERO

* Step size less than zero.

> -4012 MAX\_NUM\_ORDERS\_LESS\_THAN\_ZERO

* Max mum orders less than zero.

> -4013 PRICE\_LESS\_THAN\_MIN\_PRICE

* Price less than min price.

> -4014 PRICE\_NOT\_INCREASED\_BY\_TICK\_SIZE

* Price not increased by tick size.

> -4015 INVALID\_CL\_ORD\_ID\_LEN

* Client order id is not valid.
* Client order id length should not be more than 36 chars

> -4016 PRICE\_HIGHTER\_THAN\_MULTIPLIER\_UP

* Price is higher than mark price multiplier cap.

> -4017 MULTIPLIER\_UP\_LESS\_THAN\_ZERO

* Multiplier up less than zero.

> -4018 MULTIPLIER\_DOWN\_LESS\_THAN\_ZERO

* Multiplier down less than zero.

> -4019 COMPOSITE\_SCALE\_OVERFLOW

* Composite scale too large.

> -4020 TARGET\_STRATEGY\_INVALID

* Target strategy invalid for orderType '%s',reduceOnly '%b'.

> -4021 INVALID\_DEPTH\_LIMIT

* Invalid depth limit.
* '%s' is not valid depth limit.

> -4022 WRONG\_MARKET\_STATUS

* market status sent is not valid.

> -4023 QTY\_NOT\_INCREASED\_BY\_STEP\_SIZE

* Qty not increased by step size.

> -4024 PRICE\_LOWER\_THAN\_MULTIPLIER\_DOWN

* Price is lower than mark price multiplier floor.

> -4025 MULTIPLIER\_DECIMAL\_LESS\_THAN\_ZERO

* Multiplier decimal less than zero.

> -4026 COMMISSION\_INVALID

* Commission invalid.
* `%s` less than zero.
* `%s` absolute value greater than `%s`

> -4027 INVALID\_ACCOUNT\_TYPE

* Invalid account type.

> -4028 INVALID\_LEVERAGE

* Invalid leverage
* Leverage `%s` is not valid
* Leverage `%s` already exist with `%s`

> -4029 INVALID\_TICK\_SIZE\_PRECISION

* Tick size precision is invalid.

> -4030 INVALID\_STEP\_SIZE\_PRECISION

* Step size precision is invalid.

> -4031 INVALID\_WORKING\_TYPE

* Invalid parameter working type
* Invalid parameter working type: `%s`

> -4032 EXCEED\_MAX\_CANCEL\_ORDER\_SIZE

* Exceed maximum cancel order size.
* Invalid parameter working type: `%s`

> -4033 INSURANCE\_ACCOUNT\_NOT\_FOUND

* Insurance account not found.

> -4044 INVALID\_BALANCE\_TYPE

* Balance Type is invalid.

> -4045 MAX\_STOP\_ORDER\_EXCEEDED

* Reach max stop order limit.

> -4046 NO\_NEED\_TO\_CHANGE\_MARGIN\_TYPE

* No need to change margin type.

> -4047 THERE\_EXISTS\_OPEN\_ORDERS

* Margin type cannot be changed if there exists open orders.

> -4048 THERE\_EXISTS\_QUANTITY

* Margin type cannot be changed if there exists position.

> -4049 ADD\_ISOLATED\_MARGIN\_REJECT

* Add margin only support for isolated position.

> -4050 CROSS\_BALANCE\_INSUFFICIENT

* Cross balance insufficient.

> -4051 ISOLATED\_BALANCE\_INSUFFICIENT

* Isolated balance insufficient.

> -4052 NO\_NEED\_TO\_CHANGE\_AUTO\_ADD\_MARGIN

* No need to change auto add margin.

> -4053 AUTO\_ADD\_CROSSED\_MARGIN\_REJECT

* Auto add margin only support for isolated position.

> -4054 ADD\_ISOLATED\_MARGIN\_NO\_POSITION\_REJECT

* Cannot add position margin: position is 0.

> -4055 AMOUNT\_MUST\_BE\_POSITIVE

* Amount must be positive.

> -4056 INVALID\_API\_KEY\_TYPE

* Invalid api key type.

> -4057 INVALID\_RSA\_PUBLIC\_KEY

* Invalid api public key

> -4058 MAX\_PRICE\_TOO\_LARGE

* maxPrice and priceDecimal too large,please check.

> -4059 NO\_NEED\_TO\_CHANGE\_POSITION\_SIDE

* No need to change position side.

> -4060 INVALID\_POSITION\_SIDE

* Invalid position side.

> -4061 POSITION\_SIDE\_NOT\_MATCH

* Order's position side does not match user's setting.

> -4062 REDUCE\_ONLY\_CONFLICT

* Invalid or improper reduceOnly value.

> -4063 INVALID\_OPTIONS\_REQUEST\_TYPE

* Invalid options request type

> -4064 INVALID\_OPTIONS\_TIME\_FRAME

* Invalid options time frame

> -4065 INVALID\_OPTIONS\_AMOUNT

* Invalid options amount

> -4066 INVALID\_OPTIONS\_EVENT\_TYPE

* Invalid options event type

> -4067 POSITION\_SIDE\_CHANGE\_EXISTS\_OPEN\_ORDERS

* Position side cannot be changed if there exists open orders.

> -4068 POSITION\_SIDE\_CHANGE\_EXISTS\_QUANTITY

* Position side cannot be changed if there exists position.

> -4069 INVALID\_OPTIONS\_PREMIUM\_FEE

* Invalid options premium fee

> -4070 INVALID\_CL\_OPTIONS\_ID\_LEN

* Client options id is not valid.
* Client options id length should be less than 32 chars

> -4071 INVALID\_OPTIONS\_DIRECTION

* Invalid options direction

> -4072 OPTIONS\_PREMIUM\_NOT\_UPDATE

* premium fee is not updated, reject order

> -4073 OPTIONS\_PREMIUM\_INPUT\_LESS\_THAN\_ZERO

* input premium fee is less than 0, reject order

> -4074 OPTIONS\_AMOUNT\_BIGGER\_THAN\_UPPER

* Order amount is bigger than upper boundary or less than 0, reject order

> -4075 OPTIONS\_PREMIUM\_OUTPUT\_ZERO

* output premium fee is less than 0, reject order

> -4076 OPTIONS\_PREMIUM\_TOO\_DIFF

* original fee is too much higher than last fee

> -4077 OPTIONS\_PREMIUM\_REACH\_LIMIT

* place order amount has reached to limit, reject order

> -4078 OPTIONS\_COMMON\_ERROR

* options internal error

> -4079 INVALID\_OPTIONS\_ID

* invalid options id
* invalid options id: %s
* duplicate options id %d for user %d

> -4080 OPTIONS\_USER\_NOT\_FOUND

* user not found
* user not found with id: %s

> -4081 OPTIONS\_NOT\_FOUND

* options not found
* options not found with id: %s

> -4082 INVALID\_BATCH\_PLACE\_ORDER\_SIZE

* Invalid number of batch place orders.
* Invalid number of batch place orders: %s

> -4083 PLACE\_BATCH\_ORDERS\_FAIL

* Fail to place batch orders.

> -4084 UPCOMING\_METHOD

* Method is not allowed currently. Upcoming soon.

> -4085 INVALID\_NOTIONAL\_LIMIT\_COEF

* Invalid notional limit coefficient

> -4086 INVALID\_PRICE\_SPREAD\_THRESHOLD

* Invalid price spread threshold

> -4087 REDUCE\_ONLY\_ORDER\_PERMISSION

* User can only place reduce only order

> -4088 NO\_PLACE\_ORDER\_PERMISSION

* User can not place order currently

> -4104 INVALID\_CONTRACT\_TYPE

* Invalid contract type

> -4114 INVALID\_CLIENT\_TRAN\_ID\_LEN

* clientTranId is not valid
* Client tran id length should be less than 64 chars

> -4115 DUPLICATED\_CLIENT\_TRAN\_ID

* clientTranId is duplicated
* Client tran id should be unique within 7 days

> -4118 REDUCE\_ONLY\_MARGIN\_CHECK\_FAILED

* ReduceOnly Order Failed. Please check your existing position and open orders

> -4131 MARKET\_ORDER\_REJECT

* The counterparty's best price does not meet the PERCENT\_PRICE filter limit

> -4135 INVALID\_ACTIVATION\_PRICE

* Invalid activation price

> -4137 QUANTITY\_EXISTS\_WITH\_CLOSE\_POSITION

* Quantity must be zero with closePosition equals true

> -4138 REDUCE\_ONLY\_MUST\_BE\_TRUE

* Reduce only must be true with closePosition equals true

> -4139 ORDER\_TYPE\_CANNOT\_BE\_MKT

* Order type can not be market if it's unable to cancel

> -4140 INVALID\_OPENING\_POSITION\_STATUS

* Invalid symbol status for opening position

> -4141 SYMBOL\_ALREADY\_CLOSED

* Symbol is closed

> -4142 STRATEGY\_INVALID\_TRIGGER\_PRICE

* REJECT: take profit or stop order will be triggered immediately

> -4144 INVALID\_PAIR

* Invalid pair

> -4161 ISOLATED\_LEVERAGE\_REJECT\_WITH\_POSITION

* Leverage reduction is not supported in Isolated Margin Mode with open positions

> -4164 MIN\_NOTIONAL

* Order's notional must be no smaller than 5.0 (unless you choose reduce only)
* Order's notional must be no smaller than %s (unless you choose reduce only)

> -4165 INVALID\_TIME\_INTERVAL

* Invalid time interval
* Maximum time interval is %s days

> -4183 PRICE\_HIGHTER\_THAN\_STOP\_MULTIPLIER\_UP

* Price is higher than stop price multiplier cap.
* Limit price can't be higher than %s.

> -4184 PRICE\_LOWER\_THAN\_STOP\_MULTIPLIER\_DOWN

* Price is lower than stop price multiplier floor.
* Limit price can't be lower than %s.
