# BINANCE

Mark Price
API Description
Mark Price and Funding Rate

HTTP Request
GET /fapi/v1/premiumIndex

Request Weight
1 with symbol, 10 without symbol

Request Parameters
Name	Type	Mandatory	Description
symbol	STRING	NO	
Response Example
Response:

{
	"symbol": "BTCUSDT",
	"markPrice": "11793.63104562",	// mark price
	"indexPrice": "11781.80495970",	// index price
	"estimatedSettlePrice": "11781.16138815", // Estimated Settle Price, only useful in the last hour before the settlement starts.
	"lastFundingRate": "0.00038246",  // This is the Latest funding rate
	"interestRate": "0.00010000",
	"nextFundingTime": 1597392000000,
	"time": 1597370495002
}


OR (when symbol not sent)

[
	{
	    "symbol": "BTCUSDT",
	    "markPrice": "11793.63104562",	// mark price
	    "indexPrice": "11781.80495970",	// index price
	    "estimatedSettlePrice": "11781.16138815", // Estimated Settle Price, only useful in the last hour before the settlement starts.
	    "lastFundingRate": "0.00038246",  // This is the Latest funding rate
	    "interestRate": "0.00010000",
	    "nextFundingTime": 1597392000000,
	    "time": 1597370495002
	}
]

# ASTER

Mark Price
Response:


Copy
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
OR (when symbol not sent)


Copy
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
GET /fapi/v1/premiumIndex

Mark Price and Funding Rate

Weight: 1

Parameters:

Name
Type
Mandatory
Description
symbol

STRING

NO


# BYBIT

Get Tickers
Query for the latest price snapshot, best bid/ask price, and trading volume in the last 24 hours.

Covers: Spot / USDT contract / USDC contract / Inverse contract / Option

info
If category=option, symbol or baseCoin must be passed.

HTTP Request
GET
/v5/market/tickers

Copy
Request Parameters
Parameter	Required	Type	Comments
category	true	string	Product type. spot,linear,inverse,option
symbol	false	string	Symbol name, like BTCUSDT, uppercase only
baseCoin	false	string	Base coin, uppercase only. Apply to option only
expDate	false	string	Expiry date. e.g., 25DEC22. Apply to option only
Response Parameters
Linear/Inverse
Option
Spot
Parameter	Type	Comments
category	string	Product type
list	array	Object
> symbol	string	Symbol name
> lastPrice	string	Last price
> indexPrice	string	Index price
> markPrice	string	Mark price
> prevPrice24h	string	Market price 24 hours ago
> price24hPcnt	string	Percentage change of market price relative to 24h
> highPrice24h	string	The highest price in the last 24 hours
> lowPrice24h	string	The lowest price in the last 24 hours
> prevPrice1h	string	Market price an hour ago
> openInterest	string	Open interest size
> openInterestValue	string	Open interest value
> turnover24h	string	Turnover for 24h
> volume24h	string	Volume for 24h
> fundingRate	string	Funding rate
> nextFundingTime	string	Next funding time (ms)
> predictedDeliveryPrice	string	Predicated delivery price. It has a value 30 mins before delivery
> basisRate	string	Basis rate
> basis	string	Basis
> deliveryFeeRate	string	Delivery fee rate
> deliveryTime	string	Delivery timestamp (ms), applicable to expiry futures only
> ask1Size	string	Best ask size
> bid1Price	string	Best bid price
> ask1Price	string	Best ask price
> bid1Size	string	Best bid size
> preOpenPrice	string	Estimated pre-market contract open price
Meaningless once the market opens
> preQty	string	Estimated pre-market contract open qty
The value is meaningless once the market opens
> curPreListingPhase	string	The current pre-market contract phase
> fundingIntervalHour	string	Funding interval hour
This value currently only supports whole hours
> fundingCap	string	Funding rate upper and lower limits
> basisRateYear	string	Annual basis rate
Only for Futures,For Perpetual,it will return ""
RUN >>
Request Example
Inverse
Option
Spot
HTTP
Python
Go
Java
Node.js
GET /v5/market/tickers?category=inverse&symbol=BTCUSD HTTP/1.1
Host: api-testnet.bybit.com

Response Example
Inverse
Option
Spot
{
    "retCode": 0,
    "retMsg": "OK",
    "result": {
        "category": "inverse",
        "list": [
            {
                "symbol": "BTCUSD",
                "lastPrice": "120635.50",
                "indexPrice": "114890.92",
                "markPrice": "114898.43",
                "prevPrice24h": "105595.90",
                "price24hPcnt": "0.142425",
                "highPrice24h": "131309.30",
                "lowPrice24h": "102007.60",
                "prevPrice1h": "119806.10",
                "openInterest": "240113967",
                "openInterestValue": "2089.79",
                "turnover24h": "115.6907",
                "volume24h": "13713832.0000",
                "fundingRate": "0.0001",
                "nextFundingTime": "1760371200000",
                "predictedDeliveryPrice": "",
                "basisRate": "",
                "deliveryFeeRate": "",
                "deliveryTime": "0",
                "ask1Size": "9854",
                "bid1Price": "103401.00",
                "ask1Price": "109152.80",
                "bid1Size": "1063",
                "basis": "",
                "preOpenPrice": "",
                "preQty": "",
                "curPreListingPhase": "",
                "fundingIntervalHour": "8",
                "basisRateYear": "",
                "fundingCap": "0.005"
            }
        ]
    },
    "retExtInfo": {},
    "time": 1760352369814
}

# BITGET
HTTP Request
GET /api/v2/mix/market/funding-time
Request Example
curl "https://api.bitget.com/api/v2/mix/market/funding-time?symbol=BTCUSDT&productType=usdt-futures"


Request Parameters
Parameter	Type	Required	Description
symbol	String	Yes	Trading pair
productType	String	Yes	Product type
USDT-FUTURES USDT-M Futures
COIN-FUTURES Coin-M Futures
USDC-FUTURES USDC-M Futures
Response Example
{
    "code": "00000",
    "msg": "success",
    "requestTime": 1695796425096,
    "data": [
        {
            "symbol": "BTCUSDT",
            "nextFundingTime": "1695801600000",
            "ratePeriod": "8"
        }
    ]
}

Response Parameters
Parameter	Type	Description
> symbol	String	Trading pair name
> nextFundingTime	String	Next settlement time(ms)
> ratePeriod	String	Rate settlement cycle
The unit is hour.


# GATE
Futures
Perpetual futures

#Query all futures contracts

GET /futures/{settle}/contracts

Query all futures contracts

Parameters
Name	In	Type	Required	Description
settle	path	string	true	Settle currency
limit	query	integer	false	Maximum number of records returned in a single list
offset	query	integer	false	List offset, starting from 0
#Enumerated Values
Parameter	Value
settle	btc
settle	usdt
Responses
Status	Meaning	Description	Schema
200	OK(opens new window)	List retrieved successfully	[Contract]
This operation does not require authentication
Code samples

# coding: utf-8
import requests

host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/futures/usdt/contracts'
query_param = ''
r = requests.request('GET', host + prefix + url, headers=headers)
print(r.json())

Example responses

200 Response

[
  {
    "name": "BTC_USDT",
    "type": "direct",
    "quanto_multiplier": "0.0001",
    "ref_discount_rate": "0",
    "order_price_deviate": "0.5",
    "maintenance_rate": "0.005",
    "mark_type": "index",
    "last_price": "38026",
    "mark_price": "37985.6",
    "index_price": "37954.92",
    "funding_rate_indicative": "0.000219",
    "mark_price_round": "0.01",
    "funding_offset": 0,
    "in_delisting": false,
    "risk_limit_base": "1000000",
    "interest_rate": "0.0003",
    "order_price_round": "0.1",
    "order_size_min": "1",
    "enable_decimal": false,
    "ref_rebate_rate": "0.2",
    "funding_interval": 28800,
    "risk_limit_step": "1000000",
    "leverage_min": "1",
    "leverage_max": "100",
    "risk_limit_max": "8000000",
    "maker_fee_rate": "-0.00025",
    "taker_fee_rate": "0.00075",
    "funding_rate": "0.002053",
    "order_size_max": "1000000",
    "funding_next_apply": 1610035200,
    "short_users": 977,
    "config_change_time": 1609899548,
    "trade_size": "28530850594",
    "position_size": "5223816",
    "long_users": 455,
    "funding_impact_value": "60000",
    "orders_limit": 50,
    "trade_id": 10851092,
    "orderbook_id": 2129638396,
    "enable_bonus": true,
    "enable_credit": true,
    "create_time": 1669688556,
    "funding_cap_ratio": "0.75",
    "status": "trading",
    "launch_time": 1609899548,
    "delisting_time": 1609899548,
    "delisted_time": 1609899548,
    "market_order_slip_ratio": "0.05",
    "market_order_size_max": "0",
    "funding_rate_limit": "0.003"
  }
]
