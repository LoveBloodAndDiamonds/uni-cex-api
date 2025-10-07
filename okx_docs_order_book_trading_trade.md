# Order Book Trading

## Trade {#order-book-trading-trade}

All `Trade` API endpoints require authentication.

### POST / Place order {#order-book-trading-trade-post-place-order}

You can place an order only if you have sufficient funds.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-post-place-order-rate-limit-60-requests-per-2-seconds}

#### Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds {#order-book-trading-trade-post-place-order-rate-limit-of-lead-trader-lead-instruments-for-copy-trading-4-requests-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-place-order-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-place-order-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-place-order-permission-trade}

Rate limit of this endpoint will also be affected by the rules
[Sub-account rate
limit](/docs-v5/en/#overview-rate-limits-sub-account-rate-limit) and
[Fill ratio based sub-account rate
limit](/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit).

#### HTTP Request {#order-book-trading-trade-post-place-order-http-request}

`POST /api/v5/trade/order`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
 place order for SPOT
 POST /api/v5/trade/order
 body
 {
    "instId":"BTC-USDT",
    "tdMode":"cash",
    "clOrdId":"b15",
    "side":"buy",
    "ordType":"limit",
    "px":"2.15",
    "sz":"2"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Spot mode, limit order
result = tradeAPI.place_order(
    instId="BTC-USDT",
    tdMode="cash",
    clOrdId="b15",
    side="buy",
    ordType="limit",
    px="2.15",
    sz="2"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-place-order-request-parameters}

  ----------------------------------------------------------------------------------------------------------------------
  Parameter              Type              Required          Description
  ---------------------- ----------------- ----------------- -----------------------------------------------------------
  instId                 String            Yes               Instrument ID, e.g. `BTC-USDT`

  tdMode                 String            Yes               Trade mode\
                                                             Margin mode `cross` `isolated`\
                                                             Non-Margin mode `cash`\
                                                             `spot_isolated` (only applicable to SPOT lead trading,
                                                             `tdMode` should be `spot_isolated` for `SPOT` lead
                                                             trading.)\
                                                             Note: `isolated` is not available in multi-currency margin
                                                             mode and portfolio margin mode.

  ccy                    String            No                Margin currency\
                                                             Applicable to all `isolated` `MARGIN` orders and `cross`
                                                             `MARGIN` orders in `Futures mode`.

  clOrdId                String            No                Client Order ID as assigned by the client\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 32 characters.\
                                                             Only applicable to general order. It will not be posted to
                                                             algoId when placing TP/SL order after the general order is
                                                             filled completely.

  tag                    String            No                Order tag\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 16 characters.

  side                   String            Yes               Order side, `buy` `sell`

  posSide                String            Conditional       Position side\
                                                             The default is `net` in the `net` mode\
                                                             It is required in the `long/short` mode, and can only be
                                                             `long` or `short`.\
                                                             Only applicable to `FUTURES`/`SWAP`.

  ordType                String            Yes               Order type\
                                                             `market`: Market order, only applicable to
                                                             `SPOT/MARGIN/FUTURES/SWAP`\
                                                             `limit`: Limit order\
                                                             `post_only`: Post-only order\
                                                             `fok`: Fill-or-kill order\
                                                             `ioc`: Immediate-or-cancel order\
                                                             `optimal_limit_ioc`: Market order with immediate-or-cancel
                                                             order (applicable only to Expiry Futures and Perpetual
                                                             Futures).\
                                                             `mmp`: Market Maker Protection (only applicable to Option
                                                             in Portfolio Margin mode)\
                                                             `mmp_and_post_only`: Market Maker Protection and Post-only
                                                             order(only applicable to Option in Portfolio Margin mode)

  sz                     String            Yes               Quantity to buy or sell

  px                     String            Conditional       Order price. Only applicable to
                                                             `limit`,`post_only`,`fok`,`ioc`,`mmp`,`mmp_and_post_only`
                                                             order.\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  pxUsd                  String            Conditional       Place options orders in `USD`\
                                                             Only applicable to options\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  pxVol                  String            Conditional       Place options orders based on implied volatility, where 1
                                                             represents 100%\
                                                             Only applicable to options\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  reduceOnly             Boolean           No                Whether orders can only reduce in position size.\
                                                             Valid options: `true` or `false`. The default value is
                                                             `false`.\
                                                             Only applicable to `MARGIN` orders, and `FUTURES`/`SWAP`
                                                             orders in `net` mode\
                                                             Only applicable to `Futures mode` and
                                                             `Multi-currency margin`

  tgtCcy                 String            No                Whether the target currency uses the quote or base
                                                             currency.\
                                                             `base_ccy`: Base currency ,`quote_ccy`: Quote currency\
                                                             Only applicable to `SPOT` Market Orders\
                                                             Default is `quote_ccy` for buy, `base_ccy` for sell

  banAmend               Boolean           No                Whether to disallow the system from amending the size of
                                                             the SPOT Market Order.\
                                                             Valid options: `true` or `false`. The default value is
                                                             `false`.\
                                                             If `true`, system will not amend and reject the market
                                                             order if user does not have sufficient funds.\
                                                             Only applicable to SPOT Market Orders

  pxAmendType            String            No                The price amendment type for orders\
                                                             `0`: Do not allow the system to amend to order price if
                                                             `px` exceeds the price limit\
                                                             `1`: Allow the system to amend the price to the best
                                                             available value within the price limit if `px` exceeds the
                                                             price limit\
                                                             The default value is `0`

  tradeQuoteCcy          String            No                The quote currency used for trading. Only applicable to
                                                             `SPOT`.\
                                                             The default value is the quote currency of the `instId`,
                                                             for example: for `BTC-USD`, the default is `USD`.

  stpMode                String            No                Self trade prevention mode.\
                                                             `cancel_maker`,`cancel_taker`, `cancel_both`\
                                                             Cancel both does not support FOK\
                                                             \
                                                             The account-level acctStpMode will be used to place orders
                                                             by default. The default value of this field is
                                                             `cancel_maker`. Users can log in to the webpage through the
                                                             master account to modify this configuration. Users can also
                                                             utilize the stpMode request parameter of the placing order
                                                             endpoint to determine the stpMode of a certain order.

  attachAlgoOrds         Array of objects  No                TP/SL information attached when placing order

  \> attachAlgoClOrdId   String            No                Client-supplied Algo ID when placing order attaching TP/SL\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 32 characters.\
                                                             It will be posted to `algoClOrdId` when placing TP/SL order
                                                             once the general order is filled completely.

  \> tpTriggerPx         String            Conditional       Take-profit trigger price\
                                                             For condition TP order, if you fill in this parameter, you
                                                             should fill in the take-profit order price as well.

  \> tpOrdPx             String            Conditional       Take-profit order price\
                                                             \
                                                             For condition TP order, if you fill in this parameter, you
                                                             should fill in the take-profit trigger price as well.\
                                                             For limit TP order, you need to fill in this parameter, but
                                                             the take-profit trigger price doesn't need to be filled.\
                                                             If the price is -1, take-profit will be executed at the
                                                             market price.

  \> tpOrdKind           String            No                TP order kind\
                                                             `condition`\
                                                             `limit`\
                                                             The default is `condition`

  \> slTriggerPx         String            Conditional       Stop-loss trigger price\
                                                             If you fill in this parameter, you should fill in the
                                                             stop-loss order price.

  \> slOrdPx             String            Conditional       Stop-loss order price\
                                                             If you fill in this parameter, you should fill in the
                                                             stop-loss trigger price.\
                                                             If the price is -1, stop-loss will be executed at the
                                                             market price.

  \> tpTriggerPxType     String            No                Take-profit trigger price type\
                                                             `last`: last price\
                                                             `index`: index price\
                                                             `mark`: mark price\
                                                             The default is last

  \> slTriggerPxType     String            No                Stop-loss trigger price type\
                                                             `last`: last price\
                                                             `index`: index price\
                                                             `mark`: mark price\
                                                             The default is last

  \> sz                  String            Conditional       Size. Only applicable to TP order of split TPs, and it is
                                                             required for TP order of split TPs

  \>                     String            No                Whether to enable Cost-price SL. Only applicable to SL
  amendPxOnTriggerType                                       order of split TPs. Whether `slTriggerPx` will move to
                                                             `avgPx` when the first TP order is triggered\
                                                             `0`: disable, the default value\
                                                             `1`: Enable
  ----------------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "clOrdId": "oktswap6",
      "ordId": "312269865356374016",
      "tag": "",
      "ts":"1695190491421",
      "sCode": "0",
      "sMsg": ""
    }
  ],
  "inTime": "1695190491421339",
  "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-place-order-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> tag                  String                  Order tag

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection or success
                                                  message of event
                                                  execution.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

tdMode\
Trade Mode, when placing an order, you need to specify the trade mode.\
**Spot mode:**\
- SPOT and OPTION buyer: cash\
**Futures mode:**\
- Isolated MARGIN: isolated\
- Cross MARGIN: cross\
- SPOT: cash\
- Cross FUTURES/SWAP/OPTION: cross\
- Isolated FUTURES/SWAP/OPTION: isolated\
**Multi-currency margin mode:**\
- Cross SPOT: cross\
- Cross FUTURES/SWAP/OPTION: cross\
**Portfolio margin:**\
- Cross SPOT: cross\
- Cross FUTURES/SWAP/OPTION: cross\

clOrdId\
clOrdId is a user-defined unique ID used to identify the order. It will
be included in the response parameters if you have specified during
order submission, and can be used as a request parameter to the
endpoints to query, cancel and amend orders.\
clOrdId must be unique among the clOrdIds of all pending orders.

posSide\
Position side, this parameter is not mandatory in **net** mode. If you
pass it through, the only valid value is **net**.\
In **long/short** mode, it is mandatory. Valid values are **long** or
**short**.\
In **long/short** mode, **side** and **posSide** need to be specified in
the combinations below:\
Open long: buy and open long (side: fill in buy; posSide: fill in long)\
Open short: sell and open short (side: fill in sell; posSide: fill in
short)\
Close long: sell and close long (side: fill in sell; posSide: fill in
long)\
Close short: buy and close short (side: fill in buy; posSide: fill in
short)\
Portfolio margin mode: Expiry Futures and Perpetual Futures only support
net mode

ordType\
Order type. When creating a new order, you must specify the order type.
The order type you specify will affect: 1) what order parameters are
required, and 2) how the matching system executes your order. The
following are valid order types:\
limit: Limit order, which requires specified sz and px.\
market: Market order. For SPOT and MARGIN, market order will be filled
with market price (by swiping opposite order book). For Expiry Futures
and Perpetual Futures, market order will be placed to order book with
most aggressive price allowed by Price Limit Mechanism. For OPTION,
market order is not supported yet. As the filled price for market orders
cannot be determined in advance, OKX reserves/freezes your quote
currency by an additional 5% for risk check.\
post_only: Post-only order, which the order can only provide liquidity
to the market and be a maker. If the order would have executed on
placement, it will be canceled instead.\
fok: Fill or kill order. If the order cannot be fully filled, the order
will be canceled. The order would not be partially filled.\
ioc: Immediate or cancel order. Immediately execute the transaction at
the order price, cancel the remaining unfilled quantity of the order,
and the order quantity will not be displayed in the order book.\
optimal_limit_ioc: Market order with ioc (immediate or cancel).
Immediately execute the transaction of this market order, cancel the
remaining unfilled quantity of the order, and the order quantity will
not be displayed in the order book. Only applicable to Expiry Futures
and Perpetual Futures.

sz\
Quantity to buy or sell.\
For SPOT/MARGIN Buy and Sell Limit Orders, it refers to the quantity in
base currency.\
For MARGIN Buy Market Orders, it refers to the quantity in quote
currency.\
For MARGIN Sell Market Orders, it refers to the quantity in base
currency.\
For SPOT Market Orders, it is set by tgtCcy.\
For FUTURES/SWAP/OPTION orders, it refers to the number of contracts.

reduceOnly\
When placing an order with this parameter set to true, it means that the
order will reduce the size of the position only\
For the same MARGIN instrument, the coin quantity of all reverse
direction pending orders adds \`sz\` of new \`reduceOnly\` order cannot
exceed the position assets. After the debt is paid off, if there is a
remaining size of orders, the position will not be opened in reverse,
but will be traded in SPOT.\
For the same FUTURES/SWAP instrument, the sum of the current order size
and all reverse direction reduce-only pending orders which's price-time
priority is higher than the current order, cannot exceed the contract
quantity of position.\
Only applicable to \`Futures mode\` and \`Multi-currency margin\`\
Only applicable to \`MARGIN\` orders, and \`FUTURES\`/\`SWAP\` orders in
\`net\` mode\
Notice: Under long/short mode of Expiry Futures and Perpetual Futures,
all closing orders apply the reduce-only feature which is not affected
by this parameter.

tgtCcy\
This parameter is used to specify the order quantity in the order
request is denominated in the quantity of base or quote currency. This
is applicable to SPOT Market Orders only.\
Base currency: base_ccy\
Quote currency: quote_ccy\
If you use the Base Currency quantity for buy market orders or the Quote
Currency for sell market orders, please note:\
1. If the quantity you enter is greater than what you can buy or sell,
the system will execute the order according to your maximum buyable or
sellable quantity. If you want to trade according to the specified
quantity, you should use Limit orders.\
2. When the market price is too volatile, the locked balance may not be
sufficient to buy the Base Currency quantity or sell to receive the
Quote Currency that you specified. We will change the quantity of the
order to execute the order based on best effort principle based on your
account balance. In addition, we will try to over lock a fraction of
your balance to avoid changing the order quantity.\
2.1 Example of base currency buy market order:\
Taking the market order to buy 10 LTCs as an example, and the user can
buy 11 LTC. At this time, if 10 \< 11, the order is accepted. When the
LTC-USDT market price is 200, and the locked balance of the user is
3,000 USDT, as 200\*10 \< 3,000, the market order of 10 LTC is fully
executed; If the market is too volatile and the LTC-USDT market price
becomes 400, 400\*10 \> 3,000, the user\'s locked balance is not
sufficient to buy using the specified amount of base currency, the
user\'s maximum locked balance of 3,000 USDT will be used to settle the
trade. Final transaction quantity becomes 3,000/400 = 7.5 LTC.\
2.2 Example of quote currency sell market order:\
Taking the market order to sell 1,000 USDT as an example, and the user
can sell 1,200 USDT, 1,000 \< 1,200, the order is accepted. When the
LTC-USDT market price is 200, and the locked balance of the user is 6
LTC, as 1,000/200 \< 6, the market order of 1,000 USDT is fully
executed; If the market is too volatile and the LTC-USDT market price
becomes 100, 100\*6 \< 1,000, the user\'s locked balance is not
sufficient to sell using the specified amount of quote currency, the
user\'s maximum locked balance of 6 LTC will be used to settle the
trade. Final transaction quantity becomes 6 \* 100 = 600 USDT.

px\
The value for px must be a multiple of tickSz for OPTION orders.\
If not, the system will apply the rounding rules below. Using tickSz
0.0005 as an example:\
The px will be rounded up to the nearest 0.0005 when the remainder of px
to 0.0005 is more than 0.00025 or \`px\` is less than 0.0005.\
The px will be rounded down to the nearest 0.0005 when the remainder of
px to 0.0005 is less than 0.00025 and \`px\` is more than 0.0005.

For placing order with TP/Sl:\
1. TP/SL algo order will be generated only when this order is filled
fully, or there is no TP/SL algo order generated.\
2. Attaching TP/SL is neither supported for market buy with tgtCcy is
base_ccy or market sell with tgtCcy is quote_ccy\
3. If tpOrdKind is limit, and there is only one conditional TP order,
attachAlgoClOrdId can be used as clOrdId for retrieving on \"GET / Order
details\" endpoint.\
4. For "split TPs", including condition TP order and limit TP order.\
\* TP/SL orders in Split TPs only support one-way TP/SL. You can\'t use
slTriggerPx&slOrdPx and tpTriggerPx&tpOrdPx at the same time, or error
code 51076 will be thrown.\
\* Take-profit trigger price types (tpTriggerPxType) must be the same in
an order with Split TPs attached, or error code 51080 will be thrown.\
\* Take-profit trigger prices (tpTriggerPx) cannot be the same in an
order with Split TPs attached, or error code 51081 will be thrown.\
\* The size of the TP order among split TPs attached cannot be empty, or
error code 51089 will be thrown.\
\* The total size of TP orders with Split TPs attached in a same order
should equal the size of this order, or error code 51083 will be
thrown.\
\* The number of TP orders with Split TPs attached in a same order
cannot exceed 10, or error code 51079 will be thrown.\
\* Setting multiple TP and cost-price SL orders isn't supported for spot
and margin trading, or error code 51077 will be thrown.\
\* The number of SL orders with Split TPs attached in a same order
cannot exceed 1, or error code 51084 will be thrown.\
\* The number of TP orders cannot be less than 2 when cost-price SL is
enabled (amendPxOnTriggerType set as 1) for Split TPs, or error code
51085 will be thrown.\
\* All TP orders in one order must be of the same type, or error code
51091 will be thrown.\
\* TP order prices (tpOrdPx) in one order must be different, or error
code 51092 will be thrown.\
\* TP limit order prices (tpOrdPx) in one order can\'t be --1 (market
price), or error code 51093 will be thrown.\
\* You can\'t place TP limit orders in spot, margin, or options trading.
Otherwise, error code 51094 will be thrown.\

Mandatory self trade prevention (STP)\
The trading platform imposes mandatory self trade prevention at master
account level, which means the accounts under the same master account,
including master account itself and all its affiliated sub-accounts,
will be prevented from self trade. The account-level acctStpMode will be
used to place orders by default. The default value of this field is
\`cancel_maker\`. Users can log in to the webpage through the master
account to modify this configuration. Users can also utilize the stpMode
request parameter of the placing order endpoint to determine the stpMode
of a certain order.\
Mandatory self trade prevention will not lead to latency.\
There are three STP modes. The STP mode is always taken based on the
configuration in the taker order.\
1. Cancel Maker: This is the default STP mode, which cancels the maker
order to prevent self-trading. Then, the taker order continues to match
with the next order based on the order book priority.\
2. Cancel Taker: The taker order is canceled to prevent self-trading. If
the user\'s own maker order is lower in the order book priority, the
taker order is partially filled and then canceled. FOK orders are always
honored and canceled if they would result in self-trading.\
3. Cancel Both: Both taker and maker orders are canceled to prevent
self-trading. If the user\'s own maker order is lower in the order book
priority, the taker order is partially filled. Then, the remaining
quantity of the taker order and the first maker order are canceled. FOK
orders are not supported in this mode.

tradeQuoteCcy\
For users in specific countries and regions, this parameter must be
filled out for a successful order. Otherwise, the system will use the
quote currency of instId as the default value, then error code 51000
will occur.\
The value provided must be one of the enumerated values from
tradeQuoteCcyList, which can be obtained from the endpoint Get
instruments (GET /api/v5/account/instruments).

### POST / Place multiple orders {#order-book-trading-trade-post-place-multiple-orders}

Place orders in batches. Maximum 20 orders can be placed per request.\
Request parameters should be passed in the form of an array. Orders will
be placed in turn\

#### Rate Limit: 300 orders per 2 seconds {#order-book-trading-trade-post-place-multiple-orders-rate-limit-300-orders-per-2-seconds}

#### Rate Limit of lead trader lead instruments for Copy Trading: 4 orders per 2 seconds {#order-book-trading-trade-post-place-multiple-orders-rate-limit-of-lead-trader-lead-instruments-for-copy-trading-4-orders-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-place-multiple-orders-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-place-multiple-orders-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-place-multiple-orders-permission-trade}

Rate limit of this endpoint will also be affected by the rules
[Sub-account rate
limit](/docs-v5/en/#overview-rate-limits-sub-account-rate-limit) and
[Fill ratio based sub-account rate
limit](/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit).

Unlike other endpoints, the rate limit of this endpoint is determined by
the number of orders. If there is only one order in the request, it will
consume the rate limit of \`Place order\`.

#### HTTP Request {#order-book-trading-trade-post-place-multiple-orders-http-request}

`POST /api/v5/trade/batch-orders`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
 batch place order for SPOT
 POST /api/v5/trade/batch-orders
 body
 [
    {
        "instId":"BTC-USDT",
        "tdMode":"cash",
        "clOrdId":"b15",
        "side":"buy",
        "ordType":"limit",
        "px":"2.15",
        "sz":"2"
    },
    {
        "instId":"BTC-USDT",
        "tdMode":"cash",
        "clOrdId":"b16",
        "side":"buy",
        "ordType":"limit",
        "px":"2.15",
        "sz":"2"
    }
]
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Place multiple orders
place_orders_without_clOrdId = [
    {"instId": "BTC-USDT", "tdMode": "cash", "clOrdId": "b15", "side": "buy", "ordType": "limit", "px": "2.15", "sz": "2"},
    {"instId": "BTC-USDT", "tdMode": "cash", "clOrdId": "b16", "side": "buy", "ordType": "limit", "px": "2.15", "sz": "2"}
]

result = tradeAPI.place_multiple_orders(place_orders_without_clOrdId)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-place-multiple-orders-request-parameters}

  ----------------------------------------------------------------------------------------------------------------------
  Parameter              Type              Required          Description
  ---------------------- ----------------- ----------------- -----------------------------------------------------------
  instId                 String            Yes               Instrument ID, e.g. `BTC-USDT`

  tdMode                 String            Yes               Trade mode\
                                                             Margin mode `cross` `isolated`\
                                                             Non-Margin mode `cash`\
                                                             `spot_isolated` (only applicable to SPOT lead trading,
                                                             `tdMode` should be `spot_isolated` for `SPOT` lead
                                                             trading.)\
                                                             Note: `isolated` is not available in multi-currency margin
                                                             mode and portfolio margin mode.

  ccy                    String            No                Margin currency\
                                                             Applicable to all `isolated` `MARGIN` orders and `cross`
                                                             `MARGIN` orders in `Futures mode`.

  clOrdId                String            No                Client Order ID as assigned by the client\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 32 characters.

  tag                    String            No                Order tag\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 16 characters.

  side                   String            Yes               Order side `buy` `sell`

  posSide                String            Conditional       Position side\
                                                             The default is `net` in the `net` mode\
                                                             It is required in the `long/short` mode, and can only be
                                                             `long` or `short`.\
                                                             Only applicable to `FUTURES`/`SWAP`.

  ordType                String            Yes               Order type\
                                                             `market`: Market order, only applicable to
                                                             `SPOT/MARGIN/FUTURES/SWAP`\
                                                             `limit`: Limit order\
                                                             `post_only`: Post-only order\
                                                             `fok`: Fill-or-kill order\
                                                             `ioc`: Immediate-or-cancel order\
                                                             `optimal_limit_ioc`: Market order with immediate-or-cancel
                                                             order (applicable only to Expiry Futures and Perpetual
                                                             Futures).\
                                                             `mmp`: Market Maker Protection (only applicable to Option
                                                             in Portfolio Margin mode)\
                                                             `mmp_and_post_only`: Market Maker Protection and Post-only
                                                             order(only applicable to Option in Portfolio Margin mode)

  sz                     String            Yes               Quantity to buy or sell

  px                     String            Conditional       Order price. Only applicable to
                                                             `limit`,`post_only`,`fok`,`ioc`,`mmp`,`mmp_and_post_only`
                                                             order.\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  pxUsd                  String            Conditional       Place options orders in `USD`\
                                                             Only applicable to options\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  pxVol                  String            Conditional       Place options orders based on implied volatility, where 1
                                                             represents 100%\
                                                             Only applicable to options\
                                                             When placing an option order, one of px/pxUsd/pxVol must be
                                                             filled in, and only one can be filled in

  reduceOnly             Boolean           No                Whether the order can only reduce position size.\
                                                             Valid options: `true` or `false`. The default value is
                                                             `false`.\
                                                             Only applicable to `MARGIN` orders, and `FUTURES`/`SWAP`
                                                             orders in `net` mode\
                                                             Only applicable to `Futures mode` and
                                                             `Multi-currency margin`

  tgtCcy                 String            No                Order quantity unit setting for `sz`\
                                                             `base_ccy`: Base currency ,`quote_ccy`: Quote currency\
                                                             Only applicable to `SPOT` Market Orders\
                                                             Default is `quote_ccy` for buy, `base_ccy` for sell

  banAmend               Boolean           No                Whether to disallow the system from amending the size of
                                                             the SPOT Market Order.\
                                                             Valid options: `true` or `false`. The default value is
                                                             `false`.\
                                                             If `true`, system will not amend and reject the market
                                                             order if user does not have sufficient funds.\
                                                             Only applicable to SPOT Market Orders

  pxAmendType            String            No                The price amendment type for orders\
                                                             `0`: Do not allow the system to amend to order price if
                                                             `px` exceeds the price limit\
                                                             `1`: Allow the system to amend the price to the best
                                                             available value within the price limit if `px` exceeds the
                                                             price limit\
                                                             The default value is `0`

  tradeQuoteCcy          String            No                The quote currency used for trading. Only applicable to
                                                             `SPOT`.\
                                                             The default value is the quote currency of the `instId`,
                                                             for example: for `BTC-USD`, the default is `USD`.

  stpMode                String            No                Self trade prevention mode.\
                                                             `cancel_maker`,`cancel_taker`, `cancel_both`\
                                                             Cancel both does not support FOK.\
                                                             \
                                                             The account-level acctStpMode will be used to place orders
                                                             by default. The default value of this field is
                                                             `cancel_maker`. Users can log in to the webpage through the
                                                             master account to modify this configuration. Users can also
                                                             utilize the stpMode request parameter of the placing order
                                                             endpoint to determine the stpMode of a certain order.

  attachAlgoOrds         Array of objects  No                TP/SL information attached when placing order

  \> attachAlgoClOrdId   String            No                Client-supplied Algo ID when placing order attaching TP/SL\
                                                             A combination of case-sensitive alphanumerics, all numbers,
                                                             or all letters of up to 32 characters.\
                                                             It will be posted to `algoClOrdId` when placing TP/SL order
                                                             once the general order is filled completely.

  \> tpTriggerPx         String            Conditional       Take-profit trigger price\
                                                             For condition TP order, if you fill in this parameter, you
                                                             should fill in the take-profit order price as well.

  \> tpOrdPx             String            Conditional       Take-profit order price\
                                                             For condition TP order, if you fill in this parameter, you
                                                             should fill in the take-profit trigger price as well.\
                                                             For limit TP order, you need to fill in this parameter,
                                                             take-profit trigger needn\'t to be filled.\
                                                             If the price is -1, take-profit will be executed at the
                                                             market price.

  \> tpOrdKind           String            No                TP order kind\
                                                             `condition`\
                                                             `limit`\
                                                             The default is `condition`

  \> slTriggerPx         String            Conditional       Stop-loss trigger price\
                                                             If you fill in this parameter, you should fill in the
                                                             stop-loss order price.

  \> slOrdPx             String            Conditional       Stop-loss order price\
                                                             If you fill in this parameter, you should fill in the
                                                             stop-loss trigger price.\
                                                             If the price is -1, stop-loss will be executed at the
                                                             market price.

  \> tpTriggerPxType     String            No                Take-profit trigger price type\
                                                             `last`: last price\
                                                             `index`: index price\
                                                             `mark`: mark price\
                                                             The default is last

  \> slTriggerPxType     String            No                Stop-loss trigger price type\
                                                             `last`: last price\
                                                             `index`: index price\
                                                             `mark`: mark price\
                                                             The default is last

  \> sz                  String            Conditional       Size. Only applicable to TP order of split TPs, and it is
                                                             required for TP order of split TPs

  \>                     String            No                Whether to enable Cost-price SL. Only applicable to SL
  amendPxOnTriggerType                                       order of split TPs. Whether `slTriggerPx` will move to
                                                             `avgPx` when the first TP order is triggered\
                                                             `0`: disable, the default value\
                                                             `1`: Enable
  ----------------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "tag":"",
            "ts":"1695190491421",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "tag":"",
            "ts":"1695190491421",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-place-multiple-orders-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> tag                  String                  Order tag

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection or success
                                                  message of event
                                                  execution.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

In the \`Portfolio Margin\` account mode, either all orders are accepted
by the system successfully, or all orders are rejected by the system.

clOrdId\
clOrdId is a user-defined unique ID used to identify the order. It will
be included in the response parameters if you have specified during
order submission, and can be used as a request parameter to the
endpoints to query, cancel and amend orders.\
clOrdId must be unique among all pending orders and the current request.

### POST / Cancel order {#order-book-trading-trade-post-cancel-order}

Cancel an incomplete order.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-post-cancel-order-rate-limit-60-requests-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-cancel-order-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-cancel-order-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-cancel-order-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-cancel-order-http-request}

`POST /api/v5/trade/cancel-order`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/cancel-order
body
{
    "ordId":"590908157585625111",
    "instId":"BTC-USD-190927"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Cancel order
result = tradeAPI.cancel_order(instId="BTC-USDT", ordId="590908157585625111")
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-cancel-order-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`

  ordId             String            Conditional       Order ID\
                                                        Either `ordId` or
                                                        `clOrdId` is
                                                        required. If both
                                                        are passed, ordId
                                                        will be used.

  clOrdId           String            Conditional       Client Order ID
                                                        as assigned by
                                                        the client
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "ts":"1695190491421",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-cancel-order-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection message if
                                                  the request is
                                                  unsuccessful.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

Cancel order returns with sCode equal to 0. It is not strictly
considered that the order has been canceled. It only means that your
cancellation request has been accepted by the system server. The result
of the cancellation is subject to the state pushed by the order channel
or the get order state.\

### POST / Cancel multiple orders {#order-book-trading-trade-post-cancel-multiple-orders}

Cancel incomplete orders in batches. Maximum 20 orders can be canceled
per request. Request parameters should be passed in the form of an
array.

#### Rate Limit: 300 orders per 2 seconds {#order-book-trading-trade-post-cancel-multiple-orders-rate-limit-300-orders-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-cancel-multiple-orders-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-cancel-multiple-orders-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-cancel-multiple-orders-permission-trade}

Unlike other endpoints, the rate limit of this endpoint is determined by
the number of orders. If there is only one order in the request, it will
consume the rate limit of \`Cancel order\`.

#### HTTP Request {#order-book-trading-trade-post-cancel-multiple-orders-http-request}

`POST /api/v5/trade/cancel-batch-orders`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/cancel-batch-orders
body
[
    {
        "instId":"BTC-USDT",
        "ordId":"590908157585625111"
    },
    {
        "instId":"BTC-USDT",
        "ordId":"590908544950571222"
    }
]
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Cancel multiple orders by ordId
cancel_orders_with_orderId = [
    {"instId": "BTC-USDT", "ordId": "590908157585625111"},
    {"instId": "BTC-USDT", "ordId": "590908544950571222"}
]

result = tradeAPI.cancel_multiple_orders(cancel_orders_with_orderId)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-cancel-multiple-orders-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`

  ordId             String            Conditional       Order ID\
                                                        Either `ordId` or
                                                        `clOrdId` is
                                                        required. If both
                                                        are passed,
                                                        `ordId` will be
                                                        used.

  clOrdId           String            Conditional       Client Order ID
                                                        as assigned by
                                                        the client
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "ts":"1695190491421",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "ts":"1695190491421",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-cancel-multiple-orders-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection message if
                                                  the request is
                                                  unsuccessful.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

### POST / Amend order {#order-book-trading-trade-post-amend-order}

Amend an incomplete order.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-post-amend-order-rate-limit-60-requests-per-2-seconds}

#### Rate Limit of lead trader lead instruments for Copy Trading: 4 requests per 2 seconds {#order-book-trading-trade-post-amend-order-rate-limit-of-lead-trader-lead-instruments-for-copy-trading-4-requests-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-amend-order-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-amend-order-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-amend-order-permission-trade}

Rate limit of this endpoint will also be affected by the rules
[Sub-account rate
limit](/docs-v5/en/#overview-rate-limits-sub-account-rate-limit) and
[Fill ratio based sub-account rate
limit](/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit).

#### HTTP Request {#order-book-trading-trade-post-amend-order-http-request}

`POST /api/v5/trade/amend-order`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/amend-order
body
{
    "ordId":"590909145319051111",
    "newSz":"2",
    "instId":"BTC-USDT"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Amend order
result = tradeAPI.amend_order(
    instId="BTC-USDT",
    ordId="590909145319051111",
    newSz="2"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-amend-order-request-parameters}

  ------------------------------------------------------------------------------
  Parameter              Type              Required          Description
  ---------------------- ----------------- ----------------- -------------------
  instId                 String            Yes               Instrument ID

  cxlOnFail              Boolean           No                Whether the order
                                                             needs to be
                                                             automatically
                                                             canceled when the
                                                             order amendment
                                                             fails\
                                                             Valid options:
                                                             `false` or `true`,
                                                             the default is
                                                             `false`.

  ordId                  String            Conditional       Order ID\
                                                             Either `ordId` or
                                                             `clOrdId` is
                                                             required. If both
                                                             are passed, `ordId`
                                                             will be used.

  clOrdId                String            Conditional       Client Order ID as
                                                             assigned by the
                                                             client

  reqId                  String            No                Client Request ID
                                                             as assigned by the
                                                             client for order
                                                             amendment\
                                                             A combination of
                                                             case-sensitive
                                                             alphanumerics, all
                                                             numbers, or all
                                                             letters of up to 32
                                                             characters.\
                                                             The response will
                                                             include the
                                                             corresponding
                                                             `reqId` to help you
                                                             identify the
                                                             request if you
                                                             provide it in the
                                                             request.

  newSz                  String            Conditional       New quantity after
                                                             amendment and it
                                                             has to be larger
                                                             than 0. When
                                                             amending a
                                                             partially-filled
                                                             order, the `newSz`
                                                             should include the
                                                             amount that has
                                                             been filled.

  newPx                  String            Conditional       New price after
                                                             amendment.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol. It must
                                                             be consistent with
                                                             parameters when
                                                             placing orders. For
                                                             example, if users
                                                             placed the order
                                                             using px, they
                                                             should use newPx
                                                             when modifying the
                                                             order.

  newPxUsd               String            Conditional       Modify options
                                                             orders using USD
                                                             prices\
                                                             Only applicable to
                                                             options.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol.

  newPxVol               String            Conditional       Modify options
                                                             orders based on
                                                             implied volatility,
                                                             where 1 represents
                                                             100%\
                                                             Only applicable to
                                                             options.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol.

  pxAmendType            String            No                The price amendment
                                                             type for orders\
                                                             `0`: Do not allow
                                                             the system to amend
                                                             to order price if
                                                             `newPx` exceeds the
                                                             price limit\
                                                             `1`: Allow the
                                                             system to amend the
                                                             price to the best
                                                             available value
                                                             within the price
                                                             limit if `newPx`
                                                             exceeds the price
                                                             limit\
                                                             The default value
                                                             is `0`

  attachAlgoOrds         Array of objects  No                TP/SL information
                                                             attached when
                                                             placing order

  \> attachAlgoId        String            Conditional       The order ID of
                                                             attached TP/SL
                                                             order. It is
                                                             required to
                                                             identity the TP/SL
                                                             order when
                                                             amending. It will
                                                             not be posted to
                                                             algoId when placing
                                                             TP/SL order after
                                                             the general order
                                                             is filled
                                                             completely.

  \> attachAlgoClOrdId   String            Conditional       Client-supplied
                                                             Algo ID when
                                                             placing order
                                                             attaching TP/SL\
                                                             A combination of
                                                             case-sensitive
                                                             alphanumerics, all
                                                             numbers, or all
                                                             letters of up to 32
                                                             characters.\
                                                             It will be posted
                                                             to `algoClOrdId`
                                                             when placing TP/SL
                                                             order once the
                                                             general order is
                                                             filled completely.

  \> newTpTriggerPx      String            Conditional       Take-profit trigger
                                                             price.\
                                                             Either the take
                                                             profit trigger
                                                             price or order
                                                             price is 0, it
                                                             means that the take
                                                             profit is deleted.

  \> newTpOrdPx          String            Conditional       Take-profit order
                                                             price\
                                                             If the price is -1,
                                                             take-profit will be
                                                             executed at the
                                                             market price.

  \> newTpOrdKind        String            No                TP order kind\
                                                             `condition`\
                                                             `limit`

  \> newSlTriggerPx      String            Conditional       Stop-loss trigger
                                                             price\
                                                             Either the stop
                                                             loss trigger price
                                                             or order price is
                                                             0, it means that
                                                             the stop loss is
                                                             deleted.

  \> newSlOrdPx          String            Conditional       Stop-loss order
                                                             price\
                                                             If the price is -1,
                                                             stop-loss will be
                                                             executed at the
                                                             market price.

  \> newTpTriggerPxType  String            Conditional       Take-profit trigger
                                                             price type\
                                                             `last`: last price\
                                                             `index`: index
                                                             price\
                                                             `mark`: mark price\
                                                             Only applicable to
                                                             `FUTURES`/`SWAP`\
                                                             If you want to add
                                                             the take-profit,
                                                             this parameter is
                                                             required

  \> newSlTriggerPxType  String            Conditional       Stop-loss trigger
                                                             price type\
                                                             `last`: last price\
                                                             `index`: index
                                                             price\
                                                             `mark`: mark price\
                                                             Only applicable to
                                                             `FUTURES`/`SWAP`\
                                                             If you want to add
                                                             the stop-loss, this
                                                             parameter is
                                                             required

  \> sz                  String            Conditional       New size. Only
                                                             applicable to TP
                                                             order of split TPs,
                                                             and it is required
                                                             for TP order of
                                                             split TPs

  \>                     String            No                Whether to enable
  amendPxOnTriggerType                                       Cost-price SL. Only
                                                             applicable to SL
                                                             order of split
                                                             TPs.\
                                                             `0`: disable, the
                                                             default value\
                                                             `1`: Enable
  ------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
         "clOrdId":"",
         "ordId":"12344",
         "ts":"1695190491421",
         "reqId":"b12344",
         "sCode":"0",
         "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-amend-order-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> reqId                String                  Client Request ID as
                                                  assigned by the client
                                                  for order amendment.

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection message if
                                                  the request is
                                                  unsuccessful.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

newSz\
If the new quantity of the order is less than or equal to the filled
quantity when you are amending a partially-filled order, the order
status will be changed to filled.

The amend order returns sCode equal to 0. It is not strictly considered
that the order has been amended. It only means that your amend order
request has been accepted by the system server. The result of the amend
is subject to the status pushed by the order channel or the order status
query

### POST / Amend multiple orders {#order-book-trading-trade-post-amend-multiple-orders}

Amend incomplete orders in batches. Maximum 20 orders can be amended per
request. Request parameters should be passed in the form of an array.

#### Rate Limit: 300 orders per 2 seconds {#order-book-trading-trade-post-amend-multiple-orders-rate-limit-300-orders-per-2-seconds}

#### Rate Limit of lead trader lead instruments for Copy Trading: 4 orders per 2 seconds {#order-book-trading-trade-post-amend-multiple-orders-rate-limit-of-lead-trader-lead-instruments-for-copy-trading-4-orders-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-amend-multiple-orders-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-amend-multiple-orders-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-amend-multiple-orders-permission-trade}

Rate limit of this endpoint will also be affected by the rules
[Sub-account rate
limit](/docs-v5/en/#overview-rate-limits-sub-account-rate-limit) and
[Fill ratio based sub-account rate
limit](/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit).

Unlike other endpoints, the rate limit of this endpoint is determined by
the number of orders. If there is only one order in the request, it will
consume the rate limit of \`Amend order\`.

#### HTTP Request {#order-book-trading-trade-post-amend-multiple-orders-http-request}

`POST /api/v5/trade/amend-batch-orders`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/amend-batch-orders
body
[
    {
        "ordId":"590909308792049444",
        "newSz":"2",
        "instId":"BTC-USDT"
    },
    {
        "ordId":"590909308792049555",
        "newSz":"2",
        "instId":"BTC-USDT"
    }
]
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Amend incomplete orders in batches by ordId
amend_orders_with_orderId = [
    {"instId": "BTC-USDT", "ordId": "590909308792049444","newSz":"2"},
    {"instId": "BTC-USDT", "ordId": "590909308792049555","newSz":"2"}
]

result = tradeAPI.amend_multiple_orders(amend_orders_with_orderId)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-amend-multiple-orders-request-parameters}

  ------------------------------------------------------------------------------
  Parameter              Type              Required          Description
  ---------------------- ----------------- ----------------- -------------------
  instId                 String            Yes               Instrument ID

  cxlOnFail              Boolean           No                Whether the order
                                                             needs to be
                                                             automatically
                                                             canceled when the
                                                             order amendment
                                                             fails\
                                                             `false` `true`, the
                                                             default is `false`.

  ordId                  String            Conditional       Order ID\
                                                             Either `ordId` or
                                                             `clOrdId`is
                                                             required, if both
                                                             are passed, `ordId`
                                                             will be used.

  clOrdId                String            Conditional       Client Order ID as
                                                             assigned by the
                                                             client

  reqId                  String            No                Client Request ID
                                                             as assigned by the
                                                             client for order
                                                             amendment\
                                                             A combination of
                                                             case-sensitive
                                                             alphanumerics, all
                                                             numbers, or all
                                                             letters of up to 32
                                                             characters.\
                                                             The response will
                                                             include the
                                                             corresponding
                                                             `reqId` to help you
                                                             identify the
                                                             request if you
                                                             provide it in the
                                                             request.

  newSz                  String            Conditional       New quantity after
                                                             amendment and it
                                                             has to be larger
                                                             than 0. When
                                                             amending a
                                                             partially-filled
                                                             order, the `newSz`
                                                             should include the
                                                             amount that has
                                                             been filled.

  newPx                  String            Conditional       New price after
                                                             amendment.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol. It must
                                                             be consistent with
                                                             parameters when
                                                             placing orders. For
                                                             example, if users
                                                             placed the order
                                                             using px, they
                                                             should use newPx
                                                             when modifying the
                                                             order.

  newPxUsd               String            Conditional       Modify options
                                                             orders using USD
                                                             prices\
                                                             Only applicable to
                                                             options.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol.

  newPxVol               String            Conditional       Modify options
                                                             orders based on
                                                             implied volatility,
                                                             where 1 represents
                                                             100%\
                                                             Only applicable to
                                                             options.\
                                                             When modifying
                                                             options orders,
                                                             users can only fill
                                                             in one of the
                                                             following: newPx,
                                                             newPxUsd, or
                                                             newPxVol.

  pxAmendType            String            No                The price amendment
                                                             type for orders\
                                                             `0`: Do not allow
                                                             the system to amend
                                                             to order price if
                                                             `newPx` exceeds the
                                                             price limit\
                                                             `1`: Allow the
                                                             system to amend the
                                                             price to the best
                                                             available value
                                                             within the price
                                                             limit if `newPx`
                                                             exceeds the price
                                                             limit\
                                                             The default value
                                                             is `0`

  attachAlgoOrds         Array of objects  No                TP/SL information
                                                             attached when
                                                             placing order

  \> attachAlgoId        String            Conditional       The order ID of
                                                             attached TP/SL
                                                             order. It is
                                                             required to
                                                             identity the TP/SL
                                                             order when
                                                             amending. It will
                                                             not be posted to
                                                             algoId when placing
                                                             TP/SL order after
                                                             the general order
                                                             is filled
                                                             completely.

  \> attachAlgoClOrdId   String            Conditional       Client-supplied
                                                             Algo ID when
                                                             placing order
                                                             attaching TP/SL\
                                                             A combination of
                                                             case-sensitive
                                                             alphanumerics, all
                                                             numbers, or all
                                                             letters of up to 32
                                                             characters.\
                                                             It will be posted
                                                             to `algoClOrdId`
                                                             when placing TP/SL
                                                             order once the
                                                             general order is
                                                             filled completely.

  \> newTpTriggerPx      String            Conditional       Take-profit trigger
                                                             price.\
                                                             Either the take
                                                             profit trigger
                                                             price or order
                                                             price is 0, it
                                                             means that the take
                                                             profit is deleted.

  \> newTpOrdPx          String            Conditional       Take-profit order
                                                             price\
                                                             If the price is -1,
                                                             take-profit will be
                                                             executed at the
                                                             market price.

  \> newTpOrdKind        String            No                TP order kind\
                                                             `condition`\
                                                             `limit`

  \> newSlTriggerPx      String            Conditional       Stop-loss trigger
                                                             price\
                                                             Either the stop
                                                             loss trigger price
                                                             or order price is
                                                             0, it means that
                                                             the stop loss is
                                                             deleted.

  \> newSlOrdPx          String            Conditional       Stop-loss order
                                                             price\
                                                             If the price is -1,
                                                             stop-loss will be
                                                             executed at the
                                                             market price.

  \> newTpTriggerPxType  String            Conditional       Take-profit trigger
                                                             price type\
                                                             `last`: last price\
                                                             `index`: index
                                                             price\
                                                             `mark`: mark price\
                                                             Only applicable to
                                                             `FUTURES`/`SWAP`\
                                                             If you want to add
                                                             the take-profit,
                                                             this parameter is
                                                             required

  \> newSlTriggerPxType  String            Conditional       Stop-loss trigger
                                                             price type\
                                                             `last`: last price\
                                                             `index`: index
                                                             price\
                                                             `mark`: mark price\
                                                             Only applicable to
                                                             `FUTURES`/`SWAP`\
                                                             If you want to add
                                                             the stop-loss, this
                                                             parameter is
                                                             required

  \> sz                  String            Conditional       New size. Only
                                                             applicable to TP
                                                             order of split TPs,
                                                             and it is required
                                                             for TP order of
                                                             split TPs

  \>                     String            No                Whether to enable
  amendPxOnTriggerType                                       Cost-price SL. Only
                                                             applicable to SL
                                                             order of split
                                                             TPs.\
                                                             `0`: disable, the
                                                             default value\
                                                             `1`: Enable
  ------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "clOrdId":"oktswap6",
            "ordId":"12345689",
            "ts":"1695190491421",
            "reqId":"b12344",
            "sCode":"0",
            "sMsg":""
        },
        {
            "clOrdId":"oktswap7",
            "ordId":"12344",
            "ts":"1695190491421",
            "reqId":"b12344",
            "sCode":"0",
            "sMsg":""
        }
    ],
    "inTime": "1695190491421339",
    "outTime": "1695190491423240"
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-amend-multiple-orders-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  data                    Array of objects        Array of objects
                                                  contains the response
                                                  results

  \> ordId                String                  Order ID

  \> clOrdId              String                  Client Order ID as
                                                  assigned by the client

  \> ts                   String                  Timestamp when the
                                                  order request
                                                  processing is finished
                                                  by our system, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  \> reqId                String                  Client Request ID as
                                                  assigned by the client
                                                  for order amendment.

  \> sCode                String                  The code of the event
                                                  execution result, `0`
                                                  means success.

  \> sMsg                 String                  Rejection message if
                                                  the request is
                                                  unsuccessful.

  inTime                  String                  Timestamp at REST
                                                  gateway when the
                                                  request is received,
                                                  Unix timestamp format
                                                  in microseconds, e.g.
                                                  `1597026383085123`\
                                                  The time is recorded
                                                  after authentication.

  outTime                 String                  Timestamp at REST
                                                  gateway when the
                                                  response is sent, Unix
                                                  timestamp format in
                                                  microseconds, e.g.
                                                  `1597026383085123`
  -----------------------------------------------------------------------

newSz\
If the new quantity of the order is less than or equal to the filled
quantity when you are amending a partially-filled order, the order
status will be changed to filled.

### POST / Close positions {#order-book-trading-trade-post-close-positions}

Close the position of an instrument via a market order.

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-trade-post-close-positions-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-post-close-positions-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-post-close-positions-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Trade {#order-book-trading-trade-post-close-positions-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-close-positions-http-request}

`POST /api/v5/trade/close-position`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/close-position
body
{
    "instId":"BTC-USDT-SWAP",
    "mgnMode":"cross"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Close the position of an instrument via a market order
result = tradeAPI.close_positions(
    instId="BTC-USDT-SWAP",
    mgnMode="cross"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-close-positions-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID

  posSide           String            Conditional       Position side\
                                                        This parameter
                                                        can be omitted in
                                                        `net` mode, and
                                                        the default value
                                                        is `net`. You can
                                                        only fill with
                                                        `net`.\
                                                        This parameter
                                                        must be filled in
                                                        under the
                                                        `long/short`
                                                        mode. Fill in
                                                        `long` for
                                                        close-long and
                                                        `short` for
                                                        close-short.

  mgnMode           String            Yes               Margin mode\
                                                        `cross`
                                                        `isolated`

  ccy               String            Conditional       Margin currency,
                                                        required in the
                                                        case of closing
                                                        `cross` `MARGIN`
                                                        position for
                                                        `Futures mode`.

  autoCxl           Boolean           No                Whether any
                                                        pending orders
                                                        for closing out
                                                        needs to be
                                                        automatically
                                                        canceled when
                                                        close position
                                                        via a market
                                                        order.\
                                                        `false` or
                                                        `true`, the
                                                        default is
                                                        `false`.

  clOrdId           String            No                Client-supplied
                                                        ID\
                                                        A combination of
                                                        case-sensitive
                                                        alphanumerics,
                                                        all numbers, or
                                                        all letters of up
                                                        to 32 characters.

  tag               String            No                Order tag\
                                                        A combination of
                                                        case-sensitive
                                                        alphanumerics,
                                                        all numbers, or
                                                        all letters of up
                                                        to 16 characters.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "clOrdId": "",
            "instId": "BTC-USDT-SWAP",
            "posSide": "long",
            "tag": ""
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-close-positions-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instId                  String                  Instrument ID

  posSide                 String                  Position side

  clOrdId                 String                  Client-supplied ID\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.

  tag                     String                  Order tag\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 16 characters.
  -----------------------------------------------------------------------

if there are any pending orders for closing out and the orders do not
need to be automatically canceled, it will return an error code and
message to prompt users to cancel pending orders before closing the
positions.\

### GET / Order details {#order-book-trading-trade-get-order-details}

Retrieve order details.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-get-order-details-rate-limit-60-requests-per-2-seconds}

#### Rate limit rule (except Options): User ID + Instrument ID {#order-book-trading-trade-get-order-details-rate-limit-rule-except-options-user-id-instrument-id}

#### Rate limit rule (Options only): User ID + Instrument Family {#order-book-trading-trade-get-order-details-rate-limit-rule-options-only-user-id-instrument-family}

#### Permission: Read {#order-book-trading-trade-get-order-details-permission-read}

#### HTTP Request {#order-book-trading-trade-get-order-details-http-request}

`GET /api/v5/trade/order`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/order?ordId=1753197687182819328&instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve order details by ordId
result = tradeAPI.get_order(
    instId="BTC-USDT",
    ordId="680800019749904384"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-order-details-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID,
                                                        e.g. `BTC-USDT`\
                                                        Only applicable
                                                        to live
                                                        instruments

  ordId             String            Conditional       Order ID\
                                                        Either `ordId` or
                                                        `clOrdId` is
                                                        required, if both
                                                        are passed,
                                                        `ordId` will be
                                                        used

  clOrdId           String            Conditional       Client Order ID
                                                        as assigned by
                                                        the client\
                                                        If the `clOrdId`
                                                        is associated
                                                        with multiple
                                                        orders, only the
                                                        latest one will
                                                        be returned.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "isTpLimit": "false",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "net",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-order-details-response-parameters}

  ---------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ---------------------------
  instType                String                  Instrument type\
                                                  `SPOT`\
                                                  `MARGIN`\
                                                  `SWAP`\
                                                  `FUTURES`\
                                                  `OPTION`

  instId                  String                  Instrument ID

  tgtCcy                  String                  Order quantity unit setting
                                                  for `sz`\
                                                  `base_ccy`: Base currency
                                                  ,`quote_ccy`: Quote
                                                  currency\
                                                  Only applicable to `SPOT`
                                                  Market Orders\
                                                  Default is `quote_ccy` for
                                                  buy, `base_ccy` for sell

  ccy                     String                  Margin currency\
                                                  Applicable to all
                                                  `isolated` `MARGIN` orders
                                                  and `cross` `MARGIN` orders
                                                  in `Futures mode`,
                                                  `FUTURES` and `SWAP`
                                                  contracts.

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as assigned
                                                  by the client

  tag                     String                  Order tag

  px                      String                  Price\
                                                  For options, use coin as
                                                  unit (e.g. BTC, ETH)

  pxUsd                   String                  Options price in USDOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxVol                   String                  Implied volatility of the
                                                  options orderOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxType                  String                  Price type of options\
                                                  `px`: Place an order based
                                                  on price, in the unit of
                                                  coin (the unit for the
                                                  request parameter px is BTC
                                                  or ETH)\
                                                  `pxVol`: Place an order
                                                  based on pxVol\
                                                  `pxUsd`: Place an order
                                                  based on pxUsd, in the unit
                                                  of USD (the unit for the
                                                  request parameter px is
                                                  USD)

  sz                      String                  Quantity to buy or sell

  pnl                     String                  Profit and loss (excluding
                                                  the fee).\
                                                  Applicable to orders which
                                                  have a trade and aim to
                                                  close position. It always
                                                  is 0 in other conditions

  ordType                 String                  Order type\
                                                  `market`: Market order\
                                                  `limit`: Limit order\
                                                  `post_only`: Post-only
                                                  order\
                                                  `fok`: Fill-or-kill order\
                                                  `ioc`: Immediate-or-cancel
                                                  order\
                                                  `optimal_limit_ioc`: Market
                                                  order with
                                                  immediate-or-cancel order\
                                                  `mmp`: Market Maker
                                                  Protection (only applicable
                                                  to Option in Portfolio
                                                  Margin mode)\
                                                  `mmp_and_post_only`: Market
                                                  Maker Protection and
                                                  Post-only order(only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `op_fok`: Simple options
                                                  (fok)

  side                    String                  Order side

  posSide                 String                  Position side

  tdMode                  String                  Trade mode

  accFillSz               String                  Accumulated fill quantity\
                                                  The unit is `base_ccy` for
                                                  SPOT and MARGIN, e.g.
                                                  BTC-USDT, the unit is BTC;
                                                  For market orders, the unit
                                                  both is `base_ccy` when the
                                                  tgtCcy is `base_ccy` or
                                                  `quote_ccy`;\
                                                  The unit is contract for
                                                  `FUTURES`/`SWAP`/`OPTION`

  fillPx                  String                  Last filled price. If none
                                                  is filled, it will return
                                                  \"\".

  tradeId                 String                  Last traded ID

  fillSz                  String                  Last filled quantity\
                                                  The unit is `base_ccy` for
                                                  SPOT and MARGIN, e.g.
                                                  BTC-USDT, the unit is BTC;
                                                  For market orders, the unit
                                                  both is `base_ccy` when the
                                                  tgtCcy is `base_ccy` or
                                                  `quote_ccy`;\
                                                  The unit is contract for
                                                  `FUTURES`/`SWAP`/`OPTION`

  fillTime                String                  Last filled time

  avgPx                   String                  Average filled price. If
                                                  none is filled, it will
                                                  return \"\".

  state                   String                  State\
                                                  `canceled`\
                                                  `live`\
                                                  `partially_filled`\
                                                  `filled`\
                                                  `mmp_canceled`

  stpId                   String                  ~~Self trade prevention ID\
                                                  Return \"\" if self trade
                                                  prevention is not
                                                  applicable~~ (deprecated)

  stpMode                 String                  Self trade prevention mode

  lever                   String                  Leverage, from `0.01` to
                                                  `125`.\
                                                  Only applicable to
                                                  `MARGIN/FUTURES/SWAP`

  attachAlgoClOrdId       String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL.

  tpTriggerPx             String                  Take-profit trigger price.

  tpTriggerPxType         String                  Take-profit trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  tpOrdPx                 String                  Take-profit order price.

  slTriggerPx             String                  Stop-loss trigger price.

  slTriggerPxType         String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  slOrdPx                 String                  Stop-loss order price.

  attachAlgoOrds          Array of objects        TP/SL information attached
                                                  when placing order

  \> attachAlgoId         String                  The order ID of attached
                                                  TP/SL order. It can be used
                                                  to identity the TP/SL order
                                                  when amending. It will not
                                                  be posted to algoId when
                                                  placing TP/SL order after
                                                  the general order is filled
                                                  completely.

  \> attachAlgoClOrdId    String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all numbers,
                                                  or all letters of up to 32
                                                  characters.\
                                                  It will be posted to
                                                  `algoClOrdId` when placing
                                                  TP/SL order once the
                                                  general order is filled
                                                  completely.

  \> tpOrdKind            String                  TP order kind\
                                                  `condition`\
                                                  `limit`

  \> tpTriggerPx          String                  Take-profit trigger price.

  \> tpTriggerPxType      String                  Take-profit trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> tpOrdPx              String                  Take-profit order price.

  \> slTriggerPx          String                  Stop-loss trigger price.

  \> slTriggerPxType      String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> slOrdPx              String                  Stop-loss order price.

  \> sz                   String                  Size. Only applicable to TP
                                                  order of split TPs

  \> amendPxOnTriggerType String                  Whether to enable
                                                  Cost-price SL. Only
                                                  applicable to SL order of
                                                  split TPs.\
                                                  `0`: disable, the default
                                                  value\
                                                  `1`: Enable

  \> amendPxOnTriggerType String                  Whether to enable
                                                  Cost-price SL. Only
                                                  applicable to SL order of
                                                  split TPs.\
                                                  `0`: disable, the default
                                                  value\
                                                  `1`: Enable

  \> failCode             String                  The error code when failing
                                                  to place TP/SL order, e.g.
                                                  51020\
                                                  The default is \"\"

  \> failReason           String                  The error reason when
                                                  failing to place TP/SL
                                                  order.\
                                                  The default is \"\"

  linkedAlgoOrd           Object                  Linked SL order detail,
                                                  only applicable to the
                                                  order that is placed by
                                                  one-cancels-the-other (OCO)
                                                  order that contains the TP
                                                  limit order.

  \> algoId               String                  Algo ID

  feeCcy                  String                  Fee currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the quote
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which fees are
                                                  charged.

  fee                     String                  Fee amount\
                                                  For Spot and Margin
                                                  (excluding maker sell
                                                  orders): accumulated fee
                                                  charged by the platform,
                                                  always negative\
                                                  For maker sell orders in
                                                  Spot and Margin, Expiry
                                                  Futures, Perpetual Futures
                                                  and Options: accumulated
                                                  fee and rebate (always in
                                                  quote currency for maker
                                                  sell orders in Spot and
                                                  Margin)

  rebateCcy               String                  Rebate currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the base
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which rebates
                                                  are paid.

  rebate                  String                  Rebate amount, only
                                                  applicable to Spot and
                                                  Margin\
                                                  For maker sell orders:
                                                  Accumulated fee and rebate
                                                  amount in base currency.\
                                                  For all other cases, it
                                                  represents the maker rebate
                                                  amount, always positive,
                                                  return \"\" if no rebate.

  source                  String                  Order source\
                                                  `6`: The normal order
                                                  triggered by the
                                                  `trigger order`\
                                                  `7`:The normal order
                                                  triggered by the
                                                  `TP/SL order`\
                                                  `13`: The normal order
                                                  triggered by the algo
                                                  order\
                                                  `25`:The normal order
                                                  triggered by the
                                                  `trailing stop order`\
                                                  `34`: The normal order
                                                  triggered by the chase
                                                  order

  category                String                  Category\
                                                  `normal`\
                                                  `twap`\
                                                  `adl`\
                                                  `full_liquidation`\
                                                  `partial_liquidation`\
                                                  `delivery`\
                                                  `ddh`: Delta dynamic hedge\
                                                  `auto_conversion`

  reduceOnly              String                  Whether the order can only
                                                  reduce the position size.
                                                  Valid options: true or
                                                  false.

  isTpLimit               String                  Whether it is TP limit
                                                  order. true or false

  cancelSource            String                  Code of the cancellation
                                                  source.

  cancelSourceReason      String                  Reason for the
                                                  cancellation.

  quickMgnType            String                  Quick Margin type, Only
                                                  applicable to Quick Margin
                                                  Mode of isolated margin\
                                                  `manual`, `auto_borrow`,
                                                  `auto_repay`

  algoClOrdId             String                  Client-supplied Algo ID.
                                                  There will be a value when
                                                  algo order attaching
                                                  `algoClOrdId` is triggered,
                                                  or it will be \"\".

  algoId                  String                  Algo ID. There will be a
                                                  value when algo order is
                                                  triggered, or it will be
                                                  \"\".

  uTime                   String                  Update time, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`

  cTime                   String                  Creation time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  tradeQuoteCcy           String                  The quote currency used for
                                                  trading.
  ---------------------------------------------------------------------------

### GET / Order List {#order-book-trading-trade-get-order-list}

Retrieve all incomplete orders under the current account.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-get-order-list-rate-limit-60-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-order-list-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-order-list-permission-read}

#### HTTP Request {#order-book-trading-trade-get-order-list-http-request}

`GET /api/v5/trade/orders-pending`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/orders-pending?ordType=post_only,fok,ioc&instType=SPOT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve all incomplete orders
result = tradeAPI.get_order_list(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-order-list-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            No                Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USD-200927`

  ordType           String            No                Order type\
                                                        `market`: Market order\
                                                        `limit`: Limit order\
                                                        `post_only`: Post-only
                                                        order\
                                                        `fok`: Fill-or-kill order\
                                                        `ioc`: Immediate-or-cancel
                                                        order\
                                                        `optimal_limit_ioc`: Market
                                                        order with
                                                        immediate-or-cancel order\
                                                        `mmp`: Market Maker
                                                        Protection (only applicable
                                                        to Option in Portfolio
                                                        Margin mode)\
                                                        `mmp_and_post_only`: Market
                                                        Maker Protection and
                                                        Post-only order(only
                                                        applicable to Option in
                                                        Portfolio Margin mode)\
                                                        `op_fok`: Simple options
                                                        (fok)

  state             String            No                State\
                                                        `live`\
                                                        `partially_filled`

  after             String            No                Pagination of data to
                                                        return records earlier than
                                                        the requested `ordId`

  before            String            No                Pagination of data to
                                                        return records newer than
                                                        the requested `ordId`

  limit             String            No                Number of results per
                                                        request. The maximum is
                                                        `100`; The default is `100`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "",
            "cTime": "1724733617998",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "0",
            "feeCcy": "BTC",
            "fillPx": "",
            "fillSz": "0",
            "fillTime": "",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "isTpLimit": "false",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "1752588852617379840",
            "ordType": "post_only",
            "pnl": "0",
            "posSide": "net",
            "px": "13013.5",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "live",
            "stpId": "",
            "stpMode": "cancel_maker",
            "sz": "0.001",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "",
            "tradeQuoteCcy": "USDT",
            "uTime": "1724733617998"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-order-list-response-parameters}

  ------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ------------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  tgtCcy                  String                  Order quantity unit
                                                  setting for `sz`\
                                                  `base_ccy`: Base
                                                  currency ,`quote_ccy`:
                                                  Quote currency\
                                                  Only applicable to
                                                  `SPOT` Market Orders\
                                                  Default is `quote_ccy`
                                                  for buy, `base_ccy` for
                                                  sell

  ccy                     String                  Margin currency\
                                                  Applicable to all
                                                  `isolated` `MARGIN`
                                                  orders and `cross`
                                                  `MARGIN` orders in
                                                  `Futures mode`,
                                                  `FUTURES` and `SWAP`
                                                  contracts.

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client

  tag                     String                  Order tag

  px                      String                  Price\
                                                  For options, use coin as
                                                  unit (e.g. BTC, ETH)

  pxUsd                   String                  Options price in USDOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxVol                   String                  Implied volatility of
                                                  the options orderOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxType                  String                  Price type of options\
                                                  `px`: Place an order
                                                  based on price, in the
                                                  unit of coin (the unit
                                                  for the request
                                                  parameter px is BTC or
                                                  ETH)\
                                                  `pxVol`: Place an order
                                                  based on pxVol\
                                                  `pxUsd`: Place an order
                                                  based on pxUsd, in the
                                                  unit of USD (the unit
                                                  for the request
                                                  parameter px is USD)

  sz                      String                  Quantity to buy or sell

  pnl                     String                  Profit and loss
                                                  (excluding the fee).\
                                                  Applicable to orders
                                                  which have a trade and
                                                  aim to close position.
                                                  It always is 0 in other
                                                  conditions

  ordType                 String                  Order type\
                                                  `market`: Market order\
                                                  `limit`: Limit order\
                                                  `post_only`: Post-only
                                                  order\
                                                  `fok`: Fill-or-kill
                                                  order\
                                                  `ioc`:
                                                  Immediate-or-cancel
                                                  order\
                                                  `optimal_limit_ioc`:
                                                  Market order with
                                                  immediate-or-cancel
                                                  order\
                                                  `mmp`: Market Maker
                                                  Protection (only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `mmp_and_post_only`:
                                                  Market Maker Protection
                                                  and Post-only order(only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `op_fok`: Simple options
                                                  (fok)

  side                    String                  Order side

  posSide                 String                  Position side

  tdMode                  String                  Trade mode

  accFillSz               String                  Accumulated fill
                                                  quantity

  fillPx                  String                  Last filled price

  tradeId                 String                  Last trade ID

  fillSz                  String                  Last filled quantity

  fillTime                String                  Last filled time

  avgPx                   String                  Average filled price. If
                                                  none is filled, it will
                                                  return \"\".

  state                   String                  State\
                                                  `live`\
                                                  `partially_filled`

  lever                   String                  Leverage, from `0.01` to
                                                  `125`.\
                                                  Only applicable to
                                                  `MARGIN/FUTURES/SWAP`

  attachAlgoClOrdId       String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL.

  tpTriggerPx             String                  Take-profit trigger
                                                  price.

  tpTriggerPxType         String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  tpOrdPx                 String                  Take-profit order price.

  slTriggerPx             String                  Stop-loss trigger price.

  slTriggerPxType         String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  slOrdPx                 String                  Stop-loss order price.

  attachAlgoOrds          Array of objects        TP/SL information
                                                  attached when placing
                                                  order

  \> attachAlgoId         String                  The order ID of attached
                                                  TP/SL order. It can be
                                                  used to identity the
                                                  TP/SL order when
                                                  amending. It will not be
                                                  posted to algoId when
                                                  placing TP/SL order
                                                  after the general order
                                                  is filled completely.

  \> attachAlgoClOrdId    String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.\
                                                  It will be posted to
                                                  `algoClOrdId` when
                                                  placing TP/SL order once
                                                  the general order is
                                                  filled completely.

  \> tpOrdKind            String                  TP order kind\
                                                  `condition`\
                                                  `limit`

  \> tpTriggerPx          String                  Take-profit trigger
                                                  price.

  \> tpTriggerPxType      String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> tpOrdPx              String                  Take-profit order price.

  \> slTriggerPx          String                  Stop-loss trigger price.

  \> slTriggerPxType      String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> slOrdPx              String                  Stop-loss order price.

  \> sz                   String                  Size. Only applicable to
                                                  TP order of split TPs

  \> amendPxOnTriggerType String                  Whether to enable
                                                  Cost-price SL. Only
                                                  applicable to SL order
                                                  of split TPs.\
                                                  `0`: disable, the
                                                  default value\
                                                  `1`: Enable

  \> failCode             String                  The error code when
                                                  failing to place TP/SL
                                                  order, e.g. 51020\
                                                  The default is \"\"

  \> failReason           String                  The error reason when
                                                  failing to place TP/SL
                                                  order.\
                                                  The default is \"\"

  linkedAlgoOrd           Object                  Linked SL order detail,
                                                  only applicable to the
                                                  order that is placed by
                                                  one-cancels-the-other
                                                  (OCO) order that
                                                  contains the TP limit
                                                  order.

  \> algoId               String                  Algo ID

  stpId                   String                  ~~Self trade prevention
                                                  ID\
                                                  Return \"\" if self
                                                  trade prevention is not
                                                  applicable~~
                                                  (deprecated)

  stpMode                 String                  Self trade prevention
                                                  mode

  feeCcy                  String                  Fee currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the quote
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which fees
                                                  are charged.

  fee                     String                  Fee amount\
                                                  For Spot and Margin
                                                  (excluding maker sell
                                                  orders): accumulated fee
                                                  charged by the platform,
                                                  always negative\
                                                  For maker sell orders in
                                                  Spot and Margin, Expiry
                                                  Futures, Perpetual
                                                  Futures and Options:
                                                  accumulated fee and
                                                  rebate (always in quote
                                                  currency for maker sell
                                                  orders in Spot and
                                                  Margin)

  rebateCcy               String                  Rebate currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the base
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which
                                                  rebates are paid.

  rebate                  String                  Rebate amount, only
                                                  applicable to Spot and
                                                  Margin\
                                                  For maker sell orders:
                                                  Accumulated fee and
                                                  rebate amount in base
                                                  currency.\
                                                  For all other cases, it
                                                  represents the maker
                                                  rebate amount, always
                                                  positive, return \"\" if
                                                  no rebate.

  source                  String                  Order source\
                                                  `6`: The normal order
                                                  triggered by the
                                                  `trigger order`\
                                                  `7`:The normal order
                                                  triggered by the
                                                  `TP/SL order`\
                                                  `13`: The normal order
                                                  triggered by the algo
                                                  order\
                                                  `25`:The normal order
                                                  triggered by the
                                                  `trailing stop order`\
                                                  `34`: The normal order
                                                  triggered by the chase
                                                  order

  category                String                  Category\
                                                  `normal`

  reduceOnly              String                  Whether the order can
                                                  only reduce the position
                                                  size. Valid options:
                                                  true or false.

  quickMgnType            String                  Quick Margin type, Only
                                                  applicable to Quick
                                                  Margin Mode of isolated
                                                  margin\
                                                  `manual`, `auto_borrow`,
                                                  `auto_repay`

  algoClOrdId             String                  Client-supplied Algo ID.
                                                  There will be a value
                                                  when algo order
                                                  attaching `algoClOrdId`
                                                  is triggered, or it will
                                                  be \"\".

  algoId                  String                  Algo ID. There will be a
                                                  value when algo order is
                                                  triggered, or it will be
                                                  \"\".

  isTpLimit               String                  Whether it is TP limit
                                                  order. true or false

  uTime                   String                  Update time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  cTime                   String                  Creation time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  cancelSource            String                  Code of the cancellation
                                                  source.

  cancelSourceReason      String                  Reason for the
                                                  cancellation.

  tradeQuoteCcy           String                  The quote currency used
                                                  for trading.
  ------------------------------------------------------------------------

### GET / Order history (last 7 days) {#order-book-trading-trade-get-order-history-last-7-days}

Get completed orders which are placed in the last 7 days, including
those placed 7 days ago but completed in the last 7 days.\

The incomplete orders that have been canceled are only reserved for 2
hours.

#### Rate Limit: 40 requests per 2 seconds {#order-book-trading-trade-get-order-history-last-7-days-rate-limit-40-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-order-history-last-7-days-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-order-history-last-7-days-permission-read}

#### HTTP Request {#order-book-trading-trade-get-order-history-last-7-days-http-request}

`GET /api/v5/trade/orders-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/orders-history?ordType=post_only,fok,ioc&instType=SPOT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get completed SPOT orders which are placed in the last 7 days
# The incomplete orders that have been canceled are only reserved for 2 hours
result = tradeAPI.get_orders_history(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-order-history-last-7-days-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            yes               Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`

  ordType           String            No                Order type\
                                                        `market`: market order\
                                                        `limit`: limit order\
                                                        `post_only`: Post-only
                                                        order\
                                                        `fok`: Fill-or-kill order\
                                                        `ioc`: Immediate-or-cancel
                                                        order\
                                                        `optimal_limit_ioc`: Market
                                                        order with
                                                        immediate-or-cancel order\
                                                        `mmp`: Market Maker
                                                        Protection (only applicable
                                                        to Option in Portfolio
                                                        Margin mode)\
                                                        `mmp_and_post_only`: Market
                                                        Maker Protection and
                                                        Post-only order(only
                                                        applicable to Option in
                                                        Portfolio Margin mode)\
                                                        `op_fok`: Simple options
                                                        (fok)

  state             String            No                State\
                                                        `canceled`\
                                                        `filled`\
                                                        `mmp_canceled`: Order
                                                        canceled automatically due
                                                        to Market Maker Protection

  category          String            No                Category\
                                                        `twap`\
                                                        `adl`\
                                                        `full_liquidation`\
                                                        `partial_liquidation`\
                                                        `delivery`\
                                                        `ddh`: Delta dynamic hedge

  after             String            No                Pagination of data to
                                                        return records earlier than
                                                        the requested `ordId`

  before            String            No                Pagination of data to
                                                        return records newer than
                                                        the requested `ordId`

  begin             String            No                Filter with a begin
                                                        timestamp `cTime`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        1597026383085

  end               String            No                Filter with an end
                                                        timestamp `cTime`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        1597026383085

  limit             String            No                Number of results per
                                                        request. The maximum is
                                                        `100`; The default is `100`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "",
            "linkedAlgoOrd": {
                "algoId": ""
            },
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362",
            "isTpLimit": "false"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-order-history-last-7-days-response-parameters}

  ------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ------------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  tgtCcy                  String                  Order quantity unit
                                                  setting for `sz`\
                                                  `base_ccy`: Base
                                                  currency ,`quote_ccy`:
                                                  Quote currency\
                                                  Only applicable to
                                                  `SPOT` Market Orders\
                                                  Default is `quote_ccy`
                                                  for buy, `base_ccy` for
                                                  sell

  ccy                     String                  Margin currency\
                                                  Applicable to all
                                                  `isolated` `MARGIN`
                                                  orders and `cross`
                                                  `MARGIN` orders in
                                                  `Futures mode`,
                                                  `FUTURES` and `SWAP`
                                                  contracts.

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client

  tag                     String                  Order tag

  px                      String                  Price\
                                                  For options, use coin as
                                                  unit (e.g. BTC, ETH)

  pxUsd                   String                  Options price in USDOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxVol                   String                  Implied volatility of
                                                  the options orderOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxType                  String                  Price type of options\
                                                  `px`: Place an order
                                                  based on price, in the
                                                  unit of coin (the unit
                                                  for the request
                                                  parameter px is BTC or
                                                  ETH)\
                                                  `pxVol`: Place an order
                                                  based on pxVol\
                                                  `pxUsd`: Place an order
                                                  based on pxUsd, in the
                                                  unit of USD (the unit
                                                  for the request
                                                  parameter px is USD)

  sz                      String                  Quantity to buy or sell

  ordType                 String                  Order type\
                                                  `market`: market order\
                                                  `limit`: limit order\
                                                  `post_only`: Post-only
                                                  order\
                                                  `fok`: Fill-or-kill
                                                  order\
                                                  `ioc`:
                                                  Immediate-or-cancel
                                                  order\
                                                  `optimal_limit_ioc`:
                                                  Market order with
                                                  immediate-or-cancel
                                                  order\
                                                  `mmp`: Market Maker
                                                  Protection (only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `mmp_and_post_only`:
                                                  Market Maker Protection
                                                  and Post-only order(only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `op_fok`: Simple options
                                                  (fok)

  side                    String                  Order side

  posSide                 String                  Position side

  tdMode                  String                  Trade mode

  accFillSz               String                  Accumulated fill
                                                  quantity

  fillPx                  String                  Last filled price. If
                                                  none is filled, it will
                                                  return \"\".

  tradeId                 String                  Last trade ID

  fillSz                  String                  Last filled quantity

  fillTime                String                  Last filled time

  avgPx                   String                  Average filled price. If
                                                  none is filled, it will
                                                  return \"\".

  state                   String                  State\
                                                  `canceled`\
                                                  `filled`\
                                                  `mmp_canceled`

  lever                   String                  Leverage, from `0.01` to
                                                  `125`.\
                                                  Only applicable to
                                                  `MARGIN/FUTURES/SWAP`

  attachAlgoClOrdId       String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL.

  tpTriggerPx             String                  Take-profit trigger
                                                  price.

  tpTriggerPxType         String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  tpOrdPx                 String                  Take-profit order price.

  slTriggerPx             String                  Stop-loss trigger price.

  slTriggerPxType         String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  slOrdPx                 String                  Stop-loss order price.

  attachAlgoOrds          Array of objects        TP/SL information
                                                  attached when placing
                                                  order

  \> attachAlgoId         String                  The order ID of attached
                                                  TP/SL order. It can be
                                                  used to identity the
                                                  TP/SL order when
                                                  amending. It will not be
                                                  posted to algoId when
                                                  placing TP/SL order
                                                  after the general order
                                                  is filled completely.

  \> attachAlgoClOrdId    String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.\
                                                  It will be posted to
                                                  `algoClOrdId` when
                                                  placing TP/SL order once
                                                  the general order is
                                                  filled completely.

  \> tpOrdKind            String                  TP order kind\
                                                  `condition`\
                                                  `limit`

  \> tpTriggerPx          String                  Take-profit trigger
                                                  price.

  \> tpTriggerPxType      String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> tpOrdPx              String                  Take-profit order price.

  \> slTriggerPx          String                  Stop-loss trigger price.

  \> slTriggerPxType      String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> slOrdPx              String                  Stop-loss order price.

  \> sz                   String                  Size. Only applicable to
                                                  TP order of split TPs

  \> amendPxOnTriggerType String                  Whether to enable
                                                  Cost-price SL. Only
                                                  applicable to SL order
                                                  of split TPs.\
                                                  `0`: disable, the
                                                  default value\
                                                  `1`: Enable

  \> failCode             String                  The error code when
                                                  failing to place TP/SL
                                                  order, e.g. 51020\
                                                  The default is \"\"

  \> failReason           String                  The error reason when
                                                  failing to place TP/SL
                                                  order.\
                                                  The default is \"\"

  linkedAlgoOrd           Object                  Linked SL order detail,
                                                  only applicable to the
                                                  order that is placed by
                                                  one-cancels-the-other
                                                  (OCO) order that
                                                  contains the TP limit
                                                  order.

  \> algoId               String                  Algo ID

  stpId                   String                  ~~Self trade prevention
                                                  ID\
                                                  Return \"\" if self
                                                  trade prevention is not
                                                  applicable~~
                                                  (deprecated)

  stpMode                 String                  Self trade prevention
                                                  mode

  feeCcy                  String                  Fee currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the quote
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which fees
                                                  are charged.

  fee                     String                  Fee amount\
                                                  For Spot and Margin
                                                  (excluding maker sell
                                                  orders): accumulated fee
                                                  charged by the platform,
                                                  always negative\
                                                  For maker sell orders in
                                                  Spot and Margin, Expiry
                                                  Futures, Perpetual
                                                  Futures and Options:
                                                  accumulated fee and
                                                  rebate (always in quote
                                                  currency for maker sell
                                                  orders in Spot and
                                                  Margin)

  rebateCcy               String                  Rebate currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the base
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which
                                                  rebates are paid.

  rebate                  String                  Rebate amount, only
                                                  applicable to Spot and
                                                  Margin\
                                                  For maker sell orders:
                                                  Accumulated fee and
                                                  rebate amount in base
                                                  currency.\
                                                  For all other cases, it
                                                  represents the maker
                                                  rebate amount, always
                                                  positive, return \"\" if
                                                  no rebate.

  source                  String                  Order source\
                                                  `6`: The normal order
                                                  triggered by the
                                                  `trigger order`\
                                                  `7`:The normal order
                                                  triggered by the
                                                  `TP/SL order`\
                                                  `13`: The normal order
                                                  triggered by the algo
                                                  order\
                                                  `25`:The normal order
                                                  triggered by the
                                                  `trailing stop order`\
                                                  `34`: The normal order
                                                  triggered by the chase
                                                  order

  pnl                     String                  Profit and loss
                                                  (excluding the fee).\
                                                  Applicable to orders
                                                  which have a trade and
                                                  aim to close position.
                                                  It always is 0 in other
                                                  conditions

  category                String                  Category\
                                                  `normal`\
                                                  `twap`\
                                                  `adl`\
                                                  `full_liquidation`\
                                                  `partial_liquidation`\
                                                  `delivery`\
                                                  `ddh`: Delta dynamic
                                                  hedge\
                                                  `auto_conversion`

  reduceOnly              String                  Whether the order can
                                                  only reduce the position
                                                  size. Valid options:
                                                  true or false.

  cancelSource            String                  Code of the cancellation
                                                  source.

  cancelSourceReason      String                  Reason for the
                                                  cancellation.

  algoClOrdId             String                  Client-supplied Algo ID.
                                                  There will be a value
                                                  when algo order
                                                  attaching `algoClOrdId`
                                                  is triggered, or it will
                                                  be \"\".

  algoId                  String                  Algo ID. There will be a
                                                  value when algo order is
                                                  triggered, or it will be
                                                  \"\".

  isTpLimit               String                  Whether it is TP limit
                                                  order. true or false

  uTime                   String                  Update time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  cTime                   String                  Creation time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  quickMgnType            String                  ~~Quick Margin type,
                                                  Only applicable to Quick
                                                  Margin Mode of isolated
                                                  margin\
                                                  `manual`, `auto_borrow`,
                                                  `auto_repay`~~
                                                  (Deprecated)

  tradeQuoteCcy           String                  The quote currency used
                                                  for trading.
  ------------------------------------------------------------------------

### GET / Order history (last 3 months) {#order-book-trading-trade-get-order-history-last-3-months}

Get completed orders which are placed in the last 3 months, including
those placed 3 months ago but completed in the last 3 months.\

#### Rate Limit: 20 requests per 2 seconds {#order-book-trading-trade-get-order-history-last-3-months-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-order-history-last-3-months-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-order-history-last-3-months-permission-read}

#### HTTP Request {#order-book-trading-trade-get-order-history-last-3-months-http-request}

`GET /api/v5/trade/orders-history-archive`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/orders-history-archive?ordType=post_only,fok,ioc&instType=SPOT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get completed SPOT orders which are placed in the last 3 months
result = tradeAPI.get_orders_history_archive(
    instType="SPOT",
    ordType="post_only,fok,ioc"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-order-history-last-3-months-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            yes               Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USD-200927`

  ordType           String            No                Order type\
                                                        `market`: Market order\
                                                        `limit`: Limit order\
                                                        `post_only`: Post-only
                                                        order\
                                                        `fok`: Fill-or-kill order\
                                                        `ioc`: Immediate-or-cancel
                                                        order\
                                                        `optimal_limit_ioc`: Market
                                                        order with
                                                        immediate-or-cancel order\
                                                        `mmp`: Market Maker
                                                        Protection (only applicable
                                                        to Option in Portfolio
                                                        Margin mode)\
                                                        `mmp_and_post_only`: Market
                                                        Maker Protection and
                                                        Post-only order(only
                                                        applicable to Option in
                                                        Portfolio Margin mode)\
                                                        `op_fok`: Simple options
                                                        (fok)

  state             String            No                State\
                                                        `canceled`\
                                                        `filled`\
                                                        `mmp_canceled`: Order
                                                        canceled automatically due
                                                        to Market Maker Protection

  category          String            No                Category\
                                                        `twap`\
                                                        `adl`\
                                                        `full_liquidation`\
                                                        `partial_liquidation`\
                                                        `delivery`\
                                                        `ddh`: Delta dynamic hedge

  after             String            No                Pagination of data to
                                                        return records earlier than
                                                        the requested `ordId`

  before            String            No                Pagination of data to
                                                        return records newer than
                                                        the requested `ordId`

  begin             String            No                Filter with a begin
                                                        timestamp `cTime`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        1597026383085

  end               String            No                Filter with an end
                                                        timestamp `cTime`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        1597026383085

  limit             String            No                Number of results per
                                                        request. The maximum is
                                                        `100`; The default is `100`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "accFillSz": "0.00192834",
            "algoClOrdId": "",
            "algoId": "",
            "attachAlgoClOrdId": "",
            "attachAlgoOrds": [],
            "avgPx": "51858",
            "cTime": "1708587373361",
            "cancelSource": "",
            "cancelSourceReason": "",
            "category": "normal",
            "ccy": "",
            "clOrdId": "",
            "fee": "-0.00000192834",
            "feeCcy": "BTC",
            "fillPx": "51858",
            "fillSz": "0.00192834",
            "fillTime": "1708587373361",
            "instId": "BTC-USDT",
            "instType": "SPOT",
            "lever": "",
            "ordId": "680800019749904384",
            "ordType": "market",
            "pnl": "0",
            "posSide": "",
            "px": "",
            "pxType": "",
            "pxUsd": "",
            "pxVol": "",
            "quickMgnType": "",
            "rebate": "0",
            "rebateCcy": "USDT",
            "reduceOnly": "false",
            "side": "buy",
            "slOrdPx": "",
            "slTriggerPx": "",
            "slTriggerPxType": "",
            "source": "",
            "state": "filled",
            "stpId": "",
            "stpMode": "",
            "sz": "100",
            "tag": "",
            "tdMode": "cash",
            "tgtCcy": "quote_ccy",
            "tpOrdPx": "",
            "tpTriggerPx": "",
            "tpTriggerPxType": "",
            "tradeId": "744876980",
            "tradeQuoteCcy": "USDT",
            "uTime": "1708587373362",
            "isTpLimit": "false",
            "linkedAlgoOrd": {
                "algoId": ""
            }
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-order-history-last-3-months-response-parameters}

  ------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ------------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  tgtCcy                  String                  Order quantity unit
                                                  setting for `sz`\
                                                  `base_ccy`: Base
                                                  currency ,`quote_ccy`:
                                                  Quote currency\
                                                  Only applicable to
                                                  `SPOT` Market Orders\
                                                  Default is `quote_ccy`
                                                  for buy, `base_ccy` for
                                                  sell

  ccy                     String                  Margin currency\
                                                  Applicable to all
                                                  `isolated` `MARGIN`
                                                  orders and `cross`
                                                  `MARGIN` orders in
                                                  `Futures mode`,
                                                  `FUTURES` and `SWAP`
                                                  contracts.

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client

  tag                     String                  Order tag

  px                      String                  Price\
                                                  For options, use coin as
                                                  unit (e.g. BTC, ETH)

  pxUsd                   String                  Options price in USDOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxVol                   String                  Implied volatility of
                                                  the options orderOnly
                                                  applicable to options;
                                                  return \"\" for other
                                                  instrument types

  pxType                  String                  Price type of options\
                                                  `px`: Place an order
                                                  based on price, in the
                                                  unit of coin (the unit
                                                  for the request
                                                  parameter px is BTC or
                                                  ETH)\
                                                  `pxVol`: Place an order
                                                  based on pxVol\
                                                  `pxUsd`: Place an order
                                                  based on pxUsd, in the
                                                  unit of USD (the unit
                                                  for the request
                                                  parameter px is USD)

  sz                      String                  Quantity to buy or sell

  ordType                 String                  Order type\
                                                  `market`: Market order\
                                                  `limit`: Limit order\
                                                  `post_only`: Post-only
                                                  order\
                                                  `fok`: Fill-or-kill
                                                  order\
                                                  `ioc`:
                                                  Immediate-or-cancel
                                                  order\
                                                  `optimal_limit_ioc`:
                                                  Market order with
                                                  immediate-or-cancel
                                                  order\
                                                  `mmp`: Market Maker
                                                  Protection (only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `mmp_and_post_only`:
                                                  Market Maker Protection
                                                  and Post-only order(only
                                                  applicable to Option in
                                                  Portfolio Margin mode)\
                                                  `op_fok`: Simple options
                                                  (fok)

  side                    String                  Order side

  posSide                 String                  Position side

  tdMode                  String                  Trade mode

  accFillSz               String                  Accumulated fill
                                                  quantity

  fillPx                  String                  Last filled price. If
                                                  none is filled, it will
                                                  return \"\".

  tradeId                 String                  Last trade ID

  fillSz                  String                  Last filled quantity

  fillTime                String                  Last filled time

  avgPx                   String                  Average filled price. If
                                                  none is filled, it will
                                                  return \"\".

  state                   String                  State\
                                                  `canceled`\
                                                  `filled`\
                                                  `mmp_canceled`

  lever                   String                  Leverage, from `0.01` to
                                                  `125`.\
                                                  Only applicable to
                                                  `MARGIN/FUTURES/SWAP`

  attachAlgoClOrdId       String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL.

  tpTriggerPx             String                  Take-profit trigger
                                                  price.

  tpTriggerPxType         String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  tpOrdPx                 String                  Take-profit order price.

  slTriggerPx             String                  Stop-loss trigger price.

  slTriggerPxType         String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  slOrdPx                 String                  Stop-loss order price.

  attachAlgoOrds          Array of objects        TP/SL information
                                                  attached when placing
                                                  order

  \> attachAlgoId         String                  The order ID of attached
                                                  TP/SL order. It can be
                                                  used to identity the
                                                  TP/SL order when
                                                  amending. It will not be
                                                  posted to algoId when
                                                  placing TP/SL order
                                                  after the general order
                                                  is filled completely.

  \> attachAlgoClOrdId    String                  Client-supplied Algo ID
                                                  when placing order
                                                  attaching TP/SL\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.\
                                                  It will be posted to
                                                  `algoClOrdId` when
                                                  placing TP/SL order once
                                                  the general order is
                                                  filled completely.

  \> tpOrdKind            String                  TP order kind\
                                                  `condition`\
                                                  `limit`

  \> tpTriggerPx          String                  Take-profit trigger
                                                  price.

  \> tpTriggerPxType      String                  Take-profit trigger
                                                  price type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> tpOrdPx              String                  Take-profit order price.

  \> slTriggerPx          String                  Stop-loss trigger price.

  \> slTriggerPxType      String                  Stop-loss trigger price
                                                  type.\
                                                  `last`: last price\
                                                  `index`: index price\
                                                  `mark`: mark price

  \> slOrdPx              String                  Stop-loss order price.

  \> sz                   String                  Size. Only applicable to
                                                  TP order of split TPs

  \> amendPxOnTriggerType String                  Whether to enable
                                                  Cost-price SL. Only
                                                  applicable to SL order
                                                  of split TPs.\
                                                  `0`: disable, the
                                                  default value\
                                                  `1`: Enable

  \> failCode             String                  The error code when
                                                  failing to place TP/SL
                                                  order, e.g. 51020\
                                                  The default is \"\"

  \> failReason           String                  The error reason when
                                                  failing to place TP/SL
                                                  order.\
                                                  The default is \"\"

  linkedAlgoOrd           Object                  Linked SL order detail,
                                                  only applicable to the
                                                  order that is placed by
                                                  one-cancels-the-other
                                                  (OCO) order that
                                                  contains the TP limit
                                                  order.

  \> algoId               String                  Algo ID

  stpId                   String                  ~~Self trade prevention
                                                  ID\
                                                  Return \"\" if self
                                                  trade prevention is not
                                                  applicable~~
                                                  (deprecated)

  stpMode                 String                  Self trade prevention
                                                  mode

  feeCcy                  String                  Fee currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the quote
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which fees
                                                  are charged.

  fee                     String                  Fee amount\
                                                  For Spot and Margin
                                                  (excluding maker sell
                                                  orders): accumulated fee
                                                  charged by the platform,
                                                  always negative\
                                                  For maker sell orders in
                                                  Spot and Margin, Expiry
                                                  Futures, Perpetual
                                                  Futures and Options:
                                                  accumulated fee and
                                                  rebate (always in quote
                                                  currency for maker sell
                                                  orders in Spot and
                                                  Margin)

  rebateCcy               String                  Rebate currency\
                                                  For maker sell orders of
                                                  Spot and Margin, this
                                                  represents the base
                                                  currency. For all other
                                                  cases, it represents the
                                                  currency in which
                                                  rebates are paid.

  rebate                  String                  Rebate amount, only
                                                  applicable to Spot and
                                                  Margin\
                                                  For maker sell orders:
                                                  Accumulated fee and
                                                  rebate amount in base
                                                  currency.\
                                                  For all other cases, it
                                                  represents the maker
                                                  rebate amount, always
                                                  positive, return \"\" if
                                                  no rebate.

  source                  String                  Order source\
                                                  `6`: The normal order
                                                  triggered by the
                                                  `trigger order`\
                                                  `7`:The normal order
                                                  triggered by the
                                                  `TP/SL order`\
                                                  `13`: The normal order
                                                  triggered by the algo
                                                  order\
                                                  `25`:The normal order
                                                  triggered by the
                                                  `trailing stop order`\
                                                  `34`: The normal order
                                                  triggered by the
                                                  `chase order`

  pnl                     String                  Profit and loss
                                                  (excluding the fee).\
                                                  Applicable to orders
                                                  which have a trade and
                                                  aim to close position.
                                                  It always is 0 in other
                                                  conditions

  category                String                  Category\
                                                  `normal`\
                                                  `twap`\
                                                  `adl`\
                                                  `full_liquidation`\
                                                  `partial_liquidation`\
                                                  `delivery`\
                                                  `ddh`: Delta dynamic
                                                  hedge\
                                                  `auto_conversion`

  reduceOnly              String                  Whether the order can
                                                  only reduce the position
                                                  size. Valid options:
                                                  true or false.

  cancelSource            String                  Code of the cancellation
                                                  source.

  cancelSourceReason      String                  Reason for the
                                                  cancellation.

  algoClOrdId             String                  Client-supplied Algo ID.
                                                  There will be a value
                                                  when algo order
                                                  attaching `algoClOrdId`
                                                  is triggered, or it will
                                                  be \"\".

  algoId                  String                  Algo ID. There will be a
                                                  value when algo order is
                                                  triggered, or it will be
                                                  \"\".

  isTpLimit               String                  Whether it is TP limit
                                                  order. true or false

  uTime                   String                  Update time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  cTime                   String                  Creation time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  quickMgnType            String                  ~~Quick Margin type,
                                                  Only applicable to Quick
                                                  Margin Mode of isolated
                                                  margin\
                                                  `manual`, `auto_borrow`,
                                                  `auto_repay`~~
                                                  (Deprecated)

  tradeQuoteCcy           String                  The quote currency used
                                                  for trading.
  ------------------------------------------------------------------------

This interface does not contain the order data of the \`Canceled orders
without any fills\` type, which can be obtained through the \`Get Order
History (last 7 days)\` interface.\

As far as OPTION orders that are complete, pxVol and pxUsd will update
in time for px order, pxVol will update in time for pxUsd order, pxUsd
will update in time for pxVol order.\

### GET / Transaction details (last 3 days) {#order-book-trading-trade-get-transaction-details-last-3-days}

Retrieve recently-filled transaction details in the last 3 day.

#### Rate Limit: 60 requests per 2 seconds {#order-book-trading-trade-get-transaction-details-last-3-days-rate-limit-60-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-transaction-details-last-3-days-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-transaction-details-last-3-days-permission-read}

#### HTTP Request {#order-book-trading-trade-get-transaction-details-last-3-days-http-request}

`GET /api/v5/trade/fills`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/fills
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve recently-filled transaction details
result = tradeAPI.get_fills()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-transaction-details-last-3-days-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            No                Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`

  ordId             String            No                Order ID

  subType           String            No                Transaction type\
                                                        `1`: Buy\
                                                        `2`: Sell\
                                                        `3`: Open long\
                                                        `4`: Open short\
                                                        `5`: Close long\
                                                        `6`: Close short\
                                                        `100`: Partial liquidation
                                                        close long\
                                                        `101`: Partial liquidation
                                                        close short\
                                                        `102`: Partial liquidation
                                                        buy\
                                                        `103`: Partial liquidation
                                                        sell\
                                                        `104`: Liquidation long\
                                                        `105`: Liquidation short\
                                                        `106`: Liquidation buy\
                                                        `107`: Liquidation sell\
                                                        `110`: Liquidation transfer
                                                        in\
                                                        `111`: Liquidation transfer
                                                        out\
                                                        `118`: System token
                                                        conversion transfer in\
                                                        `119`: System token
                                                        conversion transfer out\
                                                        `112`: Delivery long\
                                                        `113`: Delivery short\
                                                        `125`: ADL close long\
                                                        `126`: ADL close short\
                                                        `127`: ADL buy\
                                                        `128`: ADL sell\
                                                        `212`: Auto borrow of quick
                                                        margin\
                                                        `213`: Auto repay of quick
                                                        margin\
                                                        `204`: block trade buy\
                                                        `205`: block trade sell\
                                                        `206`: block trade open
                                                        long\
                                                        `207`: block trade open
                                                        short\
                                                        `208`: block trade close
                                                        long\
                                                        `209`: block trade close
                                                        short\
                                                        `236`: Easy convert in\
                                                        `237`: Easy convert out\
                                                        `270`: Spread trading buy\
                                                        `271`: Spread trading sell\
                                                        `272`: Spread trading open
                                                        long\
                                                        `273`: Spread trading open
                                                        short\
                                                        `274`: Spread trading close
                                                        long\
                                                        `275`: Spread trading close
                                                        short\
                                                        `324`: Move position buy\
                                                        `325`: Move position sell\
                                                        `326`: Move position open
                                                        long\
                                                        `327`: Move position open
                                                        short\
                                                        `328`: Move position close
                                                        long\
                                                        `329`: Move position close
                                                        short\
                                                        `376`: Collateralized
                                                        borrowing auto conversion
                                                        buy\
                                                        `377`: Collateralized
                                                        borrowing auto conversion
                                                        sell

  after             String            No                Pagination of data to
                                                        return records earlier than
                                                        the requested `billId`

  before            String            No                Pagination of data to
                                                        return records newer than
                                                        the requested `billId`

  begin             String            No                Filter with a begin
                                                        timestamp `ts`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  end               String            No                Filter with an end
                                                        timestamp `ts`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  limit             String            No                Number of results per
                                                        request. The maximum is
                                                        `100`; The default is `100`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "side": "buy",
            "fillSz": "0.00192834",
            "fillPx": "51858",
            "fillPxVol": "",
            "fillFwdPx": "",
            "fee": "-0.00000192834",
            "fillPnl": "0",
            "ordId": "680800019749904384",
            "feeRate": "-0.001",
            "instType": "SPOT",
            "fillPxUsd": "",
            "instId": "BTC-USDT",
            "clOrdId": "",
            "posSide": "net",
            "billId": "680800019754098688",
            "subType": "1",
            "fillMarkVol": "",
            "tag": "",
            "fillTime": "1708587373361",
            "execType": "T",
            "fillIdxPx": "",
            "tradeId": "744876980",
            "fillMarkPx": "",
            "feeCcy": "BTC",
            "ts": "1708587373362",
            "tradeQuoteCcy": "USDT"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-transaction-details-last-3-days-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  tradeId                 String                  Last trade ID

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client

  billId                  String                  Bill ID

  subType                 String                  Transaction type

  tag                     String                  Order tag

  fillPx                  String                  Last filled price. It
                                                  is the same as the px
                                                  from \"Get bills
                                                  details\".

  fillSz                  String                  Last filled quantity

  fillIdxPx               String                  Index price at the
                                                  moment of trade
                                                  execution\
                                                  For cross currency spot
                                                  pairs, it returns
                                                  baseCcy-USDT index
                                                  price. For example, for
                                                  LTC-ETH, this field
                                                  returns the index price
                                                  of LTC-USDT.

  fillPnl                 String                  Last filled profit and
                                                  loss, applicable to
                                                  orders which have a
                                                  trade and aim to close
                                                  position. It always is
                                                  0 in other conditions

  fillPxVol               String                  Implied volatility when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillPxUsd               String                  Options price when
                                                  filled, in the unit of
                                                  USD\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillMarkVol             String                  Mark volatility when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillFwdPx               String                  Forward price when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillMarkPx              String                  Mark price when filled\
                                                  Applicable to
                                                  `FUTURES`, `SWAP`,
                                                  `OPTION`

  side                    String                  Order side, `buy`
                                                  `sell`

  posSide                 String                  Position side\
                                                  `long` `short`\
                                                  it returns `net`
                                                  in`net` mode.

  execType                String                  Liquidity taker or
                                                  maker\
                                                  `T`: taker\
                                                  `M`: maker\
                                                  Not applicable to
                                                  system orders such as
                                                  ADL and liquidation

  feeCcy                  String                  Trading fee or rebate
                                                  currency

  fee                     String                  The amount of trading
                                                  fee or rebate. The
                                                  trading fee deduction
                                                  is negative, such as
                                                  \'-0.01\'; the rebate
                                                  is positive, such as
                                                  \'0.01\'.

  ts                      String                  Data generation time,
                                                  Unix timestamp format
                                                  in milliseconds, e.g.
                                                  `1597026383085`.

  fillTime                String                  Trade time which is the
                                                  same as `fillTime` for
                                                  the order channel.

  feeRate                 String                  Fee rate. This field is
                                                  returned for `SPOT` and
                                                  `MARGIN` only

  tradeQuoteCcy           String                  The quote currency for
                                                  trading.
  -----------------------------------------------------------------------

tradeId\
For partial_liquidation, full_liquidation, or adl, when it comes to fill
information, this field will be assigned a negative value to distinguish
it from other matching transaction scenarios, when it comes to order
information, this field will be 0.

ordId\
Order ID, always \"\" for block trading.\

clOrdId\
Client-supplied order ID, always \"\" for block trading.

### GET / Transaction details (last 3 months) {#order-book-trading-trade-get-transaction-details-last-3-months}

This endpoint can retrieve data from the last 3 months.

#### Rate Limit: 10 requests per 2 seconds {#order-book-trading-trade-get-transaction-details-last-3-months-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-transaction-details-last-3-months-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-transaction-details-last-3-months-permission-read}

#### HTTP Request {#order-book-trading-trade-get-transaction-details-last-3-months-http-request}

`GET /api/v5/trade/fills-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/fills-history?instType=SPOT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve SPOT transaction details in the last 3 months.
result = tradeAPI.get_fills_history(
    instType="SPOT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-transaction-details-last-3-months-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            YES               Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            No                Instrument family\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`

  ordId             String            No                Order ID

  subType           String            No                Transaction type\
                                                        `1`: Buy\
                                                        `2`: Sell\
                                                        `3`: Open long\
                                                        `4`: Open short\
                                                        `5`: Close long\
                                                        `6`: Close short\
                                                        `100`: Partial liquidation
                                                        close long\
                                                        `101`: Partial liquidation
                                                        close short\
                                                        `102`: Partial liquidation
                                                        buy\
                                                        `103`: Partial liquidation
                                                        sell\
                                                        `104`: Liquidation long\
                                                        `105`: Liquidation short\
                                                        `106`: Liquidation buy\
                                                        `107`: Liquidation sell\
                                                        `110`: Liquidation transfer
                                                        in\
                                                        `111`: Liquidation transfer
                                                        out\
                                                        `118`: System token
                                                        conversion transfer in\
                                                        `119`: System token
                                                        conversion transfer out\
                                                        `112`: Delivery long\
                                                        `113`: Delivery short\
                                                        `125`: ADL close long\
                                                        `126`: ADL close short\
                                                        `127`: ADL buy\
                                                        `128`: ADL sell\
                                                        `212`: Auto borrow of quick
                                                        margin\
                                                        `213`: Auto repay of quick
                                                        margin\
                                                        `204`: block trade buy\
                                                        `205`: block trade sell\
                                                        `206`: block trade open
                                                        long\
                                                        `207`: block trade open
                                                        short\
                                                        `208`: block trade close
                                                        long\
                                                        `209`: block trade close
                                                        short\
                                                        `236`: Easy convert in\
                                                        `237`: Easy convert out\
                                                        `270`: Spread trading buy\
                                                        `271`: Spread trading sell\
                                                        `272`: Spread trading open
                                                        long\
                                                        `273`: Spread trading open
                                                        short\
                                                        `274`: Spread trading close
                                                        long\
                                                        `275`: Spread trading close
                                                        short\
                                                        `324`: Move position buy\
                                                        `325`: Move position sell\
                                                        `326`: Move position open
                                                        long\
                                                        `327`: Move position open
                                                        short\
                                                        `328`: Move position close
                                                        long\
                                                        `329`: Move position close
                                                        short\
                                                        `376`: Collateralized
                                                        borrowing auto conversion
                                                        buy\
                                                        `377`: Collateralized
                                                        borrowing auto conversion
                                                        sell

  after             String            No                Pagination of data to
                                                        return records earlier than
                                                        the requested `billId`

  before            String            No                Pagination of data to
                                                        return records newer than
                                                        the requested `billId`

  begin             String            No                Filter with a begin
                                                        timestamp `ts`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  end               String            No                Filter with an end
                                                        timestamp `ts`. Unix
                                                        timestamp format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  limit             String            No                Number of results per
                                                        request. The maximum is
                                                        `100`; The default is `100`
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "side": "buy",
            "fillSz": "0.00192834",
            "fillPx": "51858",
            "fillPxVol": "",
            "fillFwdPx": "",
            "fee": "-0.00000192834",
            "fillPnl": "0",
            "ordId": "680800019749904384",
            "feeRate": "-0.001",
            "instType": "SPOT",
            "fillPxUsd": "",
            "instId": "BTC-USDT",
            "clOrdId": "",
            "posSide": "net",
            "billId": "680800019754098688",
            "subType": "1",
            "fillMarkVol": "",
            "tag": "",
            "fillTime": "1708587373361",
            "execType": "T",
            "fillIdxPx": "",
            "tradeId": "744876980",
            "fillMarkPx": "",
            "feeCcy": "BTC",
            "ts": "1708587373362",
            "tradeQuoteCcy": "USDT"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-transaction-details-last-3-months-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  tradeId                 String                  Last trade ID

  ordId                   String                  Order ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client

  billId                  String                  Bill ID

  subType                 String                  Transaction type

  tag                     String                  Order tag

  fillPx                  String                  Last filled price

  fillSz                  String                  Last filled quantity

  fillIdxPx               String                  Index price at the
                                                  moment of trade
                                                  execution\
                                                  For cross currency spot
                                                  pairs, it returns
                                                  baseCcy-USDT index
                                                  price. For example, for
                                                  LTC-ETH, this field
                                                  returns the index price
                                                  of LTC-USDT.

  fillPnl                 String                  Last filled profit and
                                                  loss, applicable to
                                                  orders which have a
                                                  trade and aim to close
                                                  position. It always is
                                                  0 in other conditions

  fillPxVol               String                  Implied volatility when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillPxUsd               String                  Options price when
                                                  filled, in the unit of
                                                  USD\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillMarkVol             String                  Mark volatility when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillFwdPx               String                  Forward price when
                                                  filled\
                                                  Only applicable to
                                                  options; return \"\"
                                                  for other instrument
                                                  types

  fillMarkPx              String                  Mark price when filled\
                                                  Applicable to
                                                  `FUTURES`, `SWAP`,
                                                  `OPTION`

  side                    String                  Order side\
                                                  `buy`\
                                                  `sell`

  posSide                 String                  Position side\
                                                  `long`\
                                                  `short`\
                                                  it returns `net`
                                                  in`net` mode.

  execType                String                  Liquidity taker or
                                                  maker\
                                                  `T`: taker\
                                                  `M`: maker\
                                                  Not applicable to
                                                  system orders such as
                                                  ADL and liquidation

  feeCcy                  String                  Trading fee or rebate
                                                  currency

  fee                     String                  The amount of trading
                                                  fee or rebate. The
                                                  trading fee deduction
                                                  is negative, such as
                                                  \'-0.01\'; the rebate
                                                  is positive, such as
                                                  \'0.01\'.

  ts                      String                  Data generation time,
                                                  Unix timestamp format
                                                  in milliseconds, e.g.
                                                  `1597026383085`.

  fillTime                String                  Trade time which is the
                                                  same as `fillTime` for
                                                  the order channel.

  feeRate                 String                  Fee rate. This field is
                                                  returned for `SPOT` and
                                                  `MARGIN` only

  tradeQuoteCcy           String                  The quote currency for
                                                  trading.
  -----------------------------------------------------------------------

tradeId\
When the order category to which the transaction details belong is
partial_liquidation, full_liquidation, or adl, this field will be
assigned a negative value to distinguish it from other matching
transaction scenarios.\

ordId\
Order ID, always \"\" for block trading.\

clOrdId\
Client-supplied order ID, always \"\" for block trading.

We advise you to use Get Transaction details (last 3 days)when you
request data for recent 3 days.

### GET / Easy convert currency list {#order-book-trading-trade-get-easy-convert-currency-list}

Get list of small convertibles and mainstream currencies. Only
applicable to the crypto balance less than \$10.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-easy-convert-currency-list-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-easy-convert-currency-list-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-easy-convert-currency-list-permission-read}

#### HTTP Request {#order-book-trading-trade-get-easy-convert-currency-list-http-request}

`GET /api/v5/trade/easy-convert-currency-list`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/easy-convert-currency-list
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get list of small convertibles and mainstream currencies
result = tradeAPI.get_easy_convert_currency_list()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-easy-convert-currency-list-request-parameters}

  -----------------------------------------------------------------------
  Parameters        Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  source            String            No                Funding source\
                                                        `1`: Trading
                                                        account\
                                                        `2`: Funding
                                                        account\
                                                        The default is
                                                        `1`.

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "fromData": [
                {
                    "fromAmt": "6.580712708344864",
                    "fromCcy": "ADA"
                },
                {
                    "fromAmt": "2.9970000013055097",
                    "fromCcy": "USDC"
                }
            ],
            "toCcy": [
                "USDT",
                "BTC",
                "ETH",
                "OKB"
            ]
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-easy-convert-currency-list-response-parameters}

  Parameter    Type               Description
  ------------ ------------------ ---------------------------------------------------------
  fromData     Array of objects   Currently owned and convertible small currency list
  \> fromCcy   String             Type of small payment currency convert from, e.g. `BTC`
  \> fromAmt   String             Amount of small payment currency convert from
  toCcy        Array of strings   Type of mainstream currency convert to, e.g. `USDT`

### POST / Place easy convert {#order-book-trading-trade-post-place-easy-convert}

Convert small currencies to mainstream currencies.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-post-place-easy-convert-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-post-place-easy-convert-rate-limit-rule-user-id}

#### Permission: Trade {#order-book-trading-trade-post-place-easy-convert-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-place-easy-convert-http-request}

`POST /api/v5/trade/easy-convert`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/easy-convert
body
{
    "fromCcy": ["ADA","USDC"], //Seperated by commas
    "toCcy": "OKB"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Convert small currencies to mainstream currencies
result = tradeAPI.easy_convert(
    fromCcy=["ADA", "USDC"],
    toCcy="OKB"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-place-easy-convert-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  fromCcy           Array of strings  Yes               Type of small
                                                        payment currency
                                                        convert from\
                                                        Maximum 5
                                                        currencies can be
                                                        selected in one
                                                        order. If there
                                                        are multiple
                                                        currencies,
                                                        separate them
                                                        with commas.

  toCcy             String            Yes               Type of
                                                        mainstream
                                                        currency convert
                                                        to\
                                                        Only one
                                                        receiving
                                                        currency type can
                                                        be selected in
                                                        one order and
                                                        cannot be the
                                                        same as the small
                                                        payment
                                                        currencies.

  source            String            No                Funding source\
                                                        `1`: Trading
                                                        account\
                                                        `2`: Funding
                                                        account\
                                                        The default is
                                                        `1`.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "fillFromSz": "6.5807127",
            "fillToSz": "0.17171580105126",
            "fromCcy": "ADA",
            "status": "running",
            "toCcy": "OKB",
            "uTime": "1661419684687"
        },
        {
            "fillFromSz": "2.997",
            "fillToSz": "0.1683755161661844",
            "fromCcy": "USDC",
            "status": "running",
            "toCcy": "OKB",
            "uTime": "1661419684687"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-place-easy-convert-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  status                  String                  Current status of easy
                                                  convert\
                                                  `running`: Running\
                                                  `filled`: Filled\
                                                  `failed`: Failed

  fromCcy                 String                  Type of small payment
                                                  currency convert from

  toCcy                   String                  Type of mainstream
                                                  currency convert to

  fillFromSz              String                  Filled amount of small
                                                  payment currency
                                                  convert from

  fillToSz                String                  Filled amount of
                                                  mainstream currency
                                                  convert to

  uTime                   String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  1597026383085
  -----------------------------------------------------------------------

### GET / Easy convert history {#order-book-trading-trade-get-easy-convert-history}

Get the history and status of easy convert trades in the past 7 days.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-easy-convert-history-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-easy-convert-history-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-easy-convert-history-permission-read}

#### HTTP Request {#order-book-trading-trade-get-easy-convert-history-http-request}

`GET /api/v5/trade/easy-convert-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/easy-convert-history
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get the history of easy convert trades
result = tradeAPI.get_easy_convert_history()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-easy-convert-history-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ---------------------------------------------------------------------------------------------------------------------------------------------
  after       String   No         Pagination of data to return records earlier than the requested time (exclude), Unix timestamp format in milliseconds, e.g. `1597026383085`
  before      String   No         Pagination of data to return records newer than the requested time (exclude), Unix timestamp format in milliseconds, e.g. `1597026383085`
  limit       String   No         Number of results per request. The maximum is 100. The default is 100.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "fillFromSz": "0.1761712511667539",
            "fillToSz": "6.7342205900000000",
            "fromCcy": "OKB",
            "status": "filled",
            "toCcy": "ADA",
            "acct": "18",
            "uTime": "1661313307979"
        },
        {
            "fillFromSz": "0.1722106121112177",
            "fillToSz": "2.9971018300000000",
            "fromCcy": "OKB",
            "status": "filled",
            "toCcy": "USDC",
            "acct": "18",
            "uTime": "1661313307979"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-easy-convert-history-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  fromCcy                 String                  Type of small payment
                                                  currency convert from

  fillFromSz              String                  Amount of small payment
                                                  currency convert from

  toCcy                   String                  Type of mainstream
                                                  currency convert to

  fillToSz                String                  Amount of mainstream
                                                  currency convert to

  acct                    String                  The account where the
                                                  mainstream currency is
                                                  located\
                                                  `6`: Funding account\
                                                  `18`: Trading account

  status                  String                  Current status of easy
                                                  convert\
                                                  `running`: Running\
                                                  `filled`: Filled\
                                                  `failed`: Failed

  uTime                   String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`
  -----------------------------------------------------------------------

### GET / One-click repay currency list {#order-book-trading-trade-get-one-click-repay-currency-list}

Get list of debt currency data and repay currencies. Debt currencies
include both cross and isolated debts. Only applicable to
`Multi-currency margin`/`Portfolio margin`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-one-click-repay-currency-list-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-one-click-repay-currency-list-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-one-click-repay-currency-list-permission-read}

#### HTTP Request {#order-book-trading-trade-get-one-click-repay-currency-list-http-request}

`GET /api/v5/trade/one-click-repay-currency-list`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/one-click-repay-currency-list
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get list of debt currency data and repay currencies
result = tradeAPI.get_oneclick_repay_list()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-one-click-repay-currency-list-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  debtType          String            No                Debt type\
                                                        `cross`: cross\
                                                        `isolated`:
                                                        isolated

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtData": [
                {
                    "debtAmt": "29.653478",
                    "debtCcy": "LTC"
                },
                {
                    "debtAmt": "237803.6828295906051002",
                    "debtCcy": "USDT"
                }
            ],
            "debtType": "cross",
            "repayData": [
                {
                    "repayAmt": "0.4978335419825104",
                    "repayCcy": "ETH"
                }
            ]
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-one-click-repay-currency-list-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  debtData                Array of objects        Debt currency data list

  \> debtCcy              String                  Debt currency

  \> debtAmt              String                  Debt currency amount\
                                                  Including principal and
                                                  interest

  debtType                String                  Debt type\
                                                  `cross`: cross\
                                                  `isolated`: isolated

  repayData               Array of objects        Repay currency data
                                                  list

  \> repayCcy             String                  Repay currency

  \> repayAmt             String                  Repay currency\'s
                                                  available balance
                                                  amount
  -----------------------------------------------------------------------

### POST / Trade one-click repay {#order-book-trading-trade-post-trade-one-click-repay}

Trade one-click repay to repay cross debts. Isolated debts are not
applicable. The maximum repayment amount is based on the remaining
available balance of funding and trading accounts. Only applicable to
`Multi-currency margin`/`Portfolio margin`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-post-trade-one-click-repay-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-post-trade-one-click-repay-rate-limit-rule-user-id}

#### Permission: Trade {#order-book-trading-trade-post-trade-one-click-repay-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-trade-one-click-repay-http-request}

`POST /api/v5/trade/one-click-repay`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/one-click-repay
body
{
    "debtCcy": ["ETH","BTC"],
    "repayCcy": "USDT"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Trade one-click repay to repay cross debts
result = tradeAPI.oneclick_repay(
    debtCcy=["ETH", "BTC"],
    repayCcy="USDT"
)
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-trade-one-click-repay-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  debtCcy           Array of strings  Yes               Debt currency
                                                        type\
                                                        Maximum 5
                                                        currencies can be
                                                        selected in one
                                                        order. If there
                                                        are multiple
                                                        currencies,
                                                        separate them
                                                        with commas.

  repayCcy          String            Yes               Repay currency
                                                        type\
                                                        Only one
                                                        receiving
                                                        currency type can
                                                        be selected in
                                                        one order and
                                                        cannot be the
                                                        same as the small
                                                        payment
                                                        currencies.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtCcy": "ETH",
            "fillDebtSz": "0.01023052",
            "fillRepaySz": "30",
            "repayCcy": "USDT",
            "status": "filled",
            "uTime": "1646188520338"
        },
        {
            "debtCcy": "BTC",
            "fillFromSz": "3",
            "fillToSz": "60,221.15910001",
            "repayCcy": "USDT",
            "status": "filled",
            "uTime": "1646188520338"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-trade-one-click-repay-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  status                  String                  Current status of
                                                  one-click repay\
                                                  `running`: Running\
                                                  `filled`: Filled\
                                                  `failed`: Failed

  debtCcy                 String                  Debt currency type

  repayCcy                String                  Repay currency type

  fillDebtSz              String                  Filled amount of debt
                                                  currency

  fillRepaySz             String                  Filled amount of repay
                                                  currency

  uTime                   String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  1597026383085
  -----------------------------------------------------------------------

### GET / One-click repay history {#order-book-trading-trade-get-one-click-repay-history}

Get the history and status of one-click repay trades in the past 7 days.
Only applicable to `Multi-currency margin`/`Portfolio margin`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-one-click-repay-history-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-one-click-repay-history-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-one-click-repay-history-permission-read}

#### HTTP Request {#order-book-trading-trade-get-one-click-repay-history-http-request}

`GET /api/v5/trade/one-click-repay-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/one-click-repay-history
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Get the history of one-click repay trades
result = tradeAPI.oneclick_repay_history()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-one-click-repay-history-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ---------------------------------------------------------------------------------------------------------------------------------
  after       String   No         Pagination of data to return records earlier than the requested time, Unix timestamp format in milliseconds, e.g. 1597026383085
  before      String   No         Pagination of data to return records newer than the requested time, Unix timestamp format in milliseconds, e.g. 1597026383085
  limit       String   No         Number of results per request. The maximum is 100. The default is 100.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtCcy": "USDC",
            "fillDebtSz": "6950.4865447900000000",
            "fillRepaySz": "4.3067975995094930",
            "repayCcy": "ETH",
            "status": "filled",
            "uTime": "1661256148746"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-one-click-repay-history-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  debtCcy                 String                  Debt currency type

  fillDebtSz              String                  Amount of debt currency
                                                  transacted

  repayCcy                String                  Repay currency type

  fillRepaySz             String                  Amount of repay
                                                  currency transacted

  status                  String                  Current status of
                                                  one-click repay\
                                                  `running`: Running\
                                                  `filled`: Filled\
                                                  `failed`: Failed

  uTime                   String                  Trade time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  1597026383085
  -----------------------------------------------------------------------

### GET / One-click repay currency list (New) {#order-book-trading-trade-get-one-click-repay-currency-list-new}

Get list of debt currency data and repay currencies. Only applicable to
`SPOT mode`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-one-click-repay-currency-list-new-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-one-click-repay-currency-list-new-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-one-click-repay-currency-list-new-permission-read}

#### HTTP Request {#order-book-trading-trade-get-one-click-repay-currency-list-new-http-request}

`GET /api/v5/trade/one-click-repay-currency-list-v2`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/one-click-repay-currency-list-v2
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"
flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag,debug=True)
result = tradeAPI.get_oneclick_repay_list_v2()
print(result)
```
:::

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtData": [
                {
                    "debtAmt": "100",
                    "debtCcy": "USDC"
                }
            ],
            "repayData": [
                {
                    "repayAmt": "1.000022977",
                    "repayCcy": "BTC"
                },
                {
                    "repayAmt": "4998.0002397",
                    "repayCcy": "USDT"
                },
                {
                    "repayAmt": "100",
                    "repayCcy": "OKB"
                },
                {
                    "repayAmt": "1",
                    "repayCcy": "ETH"
                },
                {
                    "repayAmt": "100",
                    "repayCcy": "USDC"
                }
            ]
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-one-click-repay-currency-list-new-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  debtData                Array of objects        Debt currency data list

  \> debtCcy              String                  Debt currency

  \> debtAmt              String                  Debt currency amount\
                                                  Including principal and
                                                  interest

  repayData               Array of objects        Repay currency data
                                                  list

  \> repayCcy             String                  Repay currency

  \> repayAmt             String                  Repay currency\'s
                                                  available balance
                                                  amount
  -----------------------------------------------------------------------

### POST / Trade one-click repay (New) {#order-book-trading-trade-post-trade-one-click-repay-new}

Trade one-click repay to repay debts. Only applicable to `SPOT mode`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-post-trade-one-click-repay-new-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-post-trade-one-click-repay-new-rate-limit-rule-user-id}

#### Permission: Trade {#order-book-trading-trade-post-trade-one-click-repay-new-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-trade-one-click-repay-new-http-request}

`POST /api/v5/trade/one-click-repay-v2`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/one-click-repay-v2
body
{
    "debtCcy": "USDC",
    "repayCcyList": ["USDC","BTC"]
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"
flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag,debug=True)
result = tradeAPI.oneclick_repay_v2("USDC",["USDC","BTC"])
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-trade-one-click-repay-new-request-parameters}

  -----------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------------
  debtCcy           String            Yes               Debt currency

  repayCcyList      Array of strings  Yes               Repay currency list,
                                                        e.g.
                                                        \[\"USDC\",\"BTC\"\]\
                                                        The priority of
                                                        currency to repay is
                                                        consistent with the
                                                        order in the array.
                                                        (The first item has the
                                                        highest priority)
  -----------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtCcy": "USDC",
            "repayCcyList": [
                "USDC",
                "BTC"
            ],
            "ts": "1742192217514"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-trade-one-click-repay-new-response-parameters}

  Parameter      Type               Description
  -------------- ------------------ ---------------------------------------------------------------------------
  debtCcy        String             Debt currency
  repayCcyList   Array of strings   Repay currency list, e.g. \[\"USDC\",\"BTC\"\]
  ts             String             Request time, Unix timestamp format in milliseconds, e.g. `1597026383085`

### GET / One-click repay history (New) {#order-book-trading-trade-get-one-click-repay-history-new}

Get the history and status of one-click repay trades in the past 7 days.
Only applicable to `SPOT mode`.

#### Rate Limit: 1 request per 2 seconds {#order-book-trading-trade-get-one-click-repay-history-new-rate-limit-1-request-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-get-one-click-repay-history-new-rate-limit-rule-user-id}

#### Permission: Read {#order-book-trading-trade-get-one-click-repay-history-new-permission-read}

#### HTTP Request {#order-book-trading-trade-get-one-click-repay-history-new-http-request}

`GET /api/v5/trade/one-click-repay-history-v2`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/trade/one-click-repay-history-v2
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"
flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)
result = tradeAPI.oneclick_repay_history_v2()
print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-get-one-click-repay-history-new-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ----------------------------------------------------------------------------------------------------------------------------------------------------
  after       String   No         Pagination of data to return records earlier than (included) the requested time `ts` , Unix timestamp format in milliseconds, e.g. `1597026383085`
  before      String   No         Pagination of data to return records newer than (included) the requested time `ts`, Unix timestamp format in milliseconds, e.g. `1597026383085`
  limit       String   No         Number of results per request. The maximum is 100. The default is 100.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debtCcy": "USDC",
            "fillDebtSz": "9.079631989",
            "ordIdInfo": [
                {
                    "cTime": "1742194485439",
                    "fillPx": "1",
                    "fillSz": "9.088651",
                    "instId": "USDC-USDT",
                    "ordId": "2338478342062235648",
                    "ordType": "ioc",
                    "px": "1.0049",
                    "side": "buy",
                    "state": "filled",
                    "sz": "9.0886514537313433"
                },
                {
                    "cTime": "1742194482326",
                    "fillPx": "83271.9",
                    "fillSz": "0.00010969",
                    "instId": "BTC-USDT",
                    "ordId": "2338478237607288832",
                    "ordType": "ioc",
                    "px": "82856.7",
                    "side": "sell",
                    "state": "filled",
                    "sz": "0.000109696512171"
                }
            ],
            "repayCcyList": [
                "USDC",
                "BTC"
            ],
            "status": "filled",
            "ts": "1742194481852"
        },
        {
            "debtCcy": "USDC",
            "fillDebtSz": "100",
            "ordIdInfo": [],
            "repayCcyList": [
                "USDC",
                "BTC"
            ],
            "status": "filled",
            "ts": "1742192217511"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-one-click-repay-history-new-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  debtCcy                 String                  Debt currency

  repayCcyList            Array of strings        Repay currency list,
                                                  e.g.
                                                  \[\"USDC\",\"BTC\"\]

  fillDebtSz              String                  Amount of debt currency
                                                  transacted

  status                  String                  Current status of
                                                  one-click repay\
                                                  `running`: Running\
                                                  `filled`: Filled\
                                                  `failed`: Failed

  ordIdInfo               Array of objects        Order info

  \> ordId                String                  Order ID

  \> instId               String                  Instrument ID, e.g.
                                                  `BTC-USDT`

  \> ordType              String                  Order type\
                                                  `ioc`:
                                                  Immediate-or-cancel
                                                  order

  \> side                 String                  Side\
                                                  `buy`\
                                                  `sell`

  \> px                   String                  Price

  \> sz                   String                  Quantity to buy or sell

  \> fillPx               String                  Last filled price.\
                                                  If none is filled, it
                                                  will return \"\".

  \> fillSz               String                  Last filled quantity

  \> state                String                  State\
                                                  `filled`\
                                                  `canceled`

  \> cTime                String                  Creation time for
                                                  order, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`

  ts                      String                  Request time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`
  -----------------------------------------------------------------------

### POST / Mass cancel order {#order-book-trading-trade-post-mass-cancel-order}

Cancel all the MMP pending orders of an instrument family.\

Only applicable to Option in Portfolio Margin mode, and MMP privilege is
required.

#### Rate Limit: 5 requests per 2 seconds {#order-book-trading-trade-post-mass-cancel-order-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-post-mass-cancel-order-rate-limit-rule-user-id}

#### Permission: Trade {#order-book-trading-trade-post-mass-cancel-order-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-mass-cancel-order-http-request}

`POST /api/v5/trade/mass-cancel`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/mass-cancel
body
{
    "instType":"OPTION",
    "instFamily":"BTC-USD"
}
```
:::

#### Request Parameters {#order-book-trading-trade-post-mass-cancel-order-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instType          String            Yes               Instrument type\
                                                        `OPTION`

  instFamily        String            Yes               Instrument family

  lockInterval      String            No                Lock
                                                        interval(ms)\
                                                        The range should
                                                        be \[0, 10 000\]\
                                                        The default is 0.
                                                        You can set it as
                                                        \"0\" if you want
                                                        to unlock it
                                                        immediately.\
                                                        Error 54008 will
                                                        be returned when
                                                        placing order
                                                        during lock
                                                        interval, it is
                                                        different from
                                                        51034 which is
                                                        thrown when MMP
                                                        is triggered
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "result":true
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-mass-cancel-order-response-parameters}

  Parameter   Type      Description
  ----------- --------- ---------------------------------------
  result      Boolean   Result of the request `true`, `false`

### POST / Cancel All After {#order-book-trading-trade-post-cancel-all-after}

Cancel all pending orders after the countdown timeout. Applicable to all
trading symbols through order book (except Spread trading)\

#### Rate Limit: 1 request per second {#order-book-trading-trade-post-cancel-all-after-rate-limit-1-request-per-second}

#### Rate limit rule: User ID + tag {#order-book-trading-trade-post-cancel-all-after-rate-limit-rule-user-id-tag}

#### Permission: Trade {#order-book-trading-trade-post-cancel-all-after-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-cancel-all-after-http-request}

`POST /api/v5/trade/cancel-all-after`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/trade/cancel-all-after
{
   "timeOut":"60"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Trade as Trade

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading: 0, Demo trading: 1

tradeAPI = Trade.TradeAPI(apikey, secretkey, passphrase, False, flag)

# Set cancel all after
result = tradeAPI.cancel_all_after(
    timeOut="10"
)

print(result)
```
:::

#### Request Parameters {#order-book-trading-trade-post-cancel-all-after-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  timeOut           String            Yes               The countdown for
                                                        order
                                                        cancellation,
                                                        with second as
                                                        the unit.\
                                                        Range of value
                                                        can be 0, \[10,
                                                        120\].\
                                                        Setting timeOut
                                                        to 0 disables
                                                        Cancel All After.

  tag               String            No                CAA order tag\
                                                        A combination of
                                                        case-sensitive
                                                        alphanumerics,
                                                        all numbers, or
                                                        all letters of up
                                                        to 16 characters.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "triggerTime":"1587971460",
            "tag":"",
            "ts":"1587971400"
        }
    ]
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-cancel-all-after-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  triggerTime             String                  The time the
                                                  cancellation is
                                                  triggered.\
                                                  triggerTime=0 means
                                                  Cancel All After is
                                                  disabled.

  tag                     String                  CAA order tag

  ts                      String                  The time the request is
                                                  received.
  -----------------------------------------------------------------------

Users are recommended to send heartbeat to the exchange every second.
When the cancel all after is triggered, the trading engine will cancel
orders on behalf of the client one by one and this operation may take up
to a few seconds. This feature is intended as a protection mechanism for
clients only and clients should not use this feature as part of their
trading strategies.

\
To use tag level CAA, first, users need to set tags for their orders
using the \`tag\` request parameter in the placing orders endpoint. When
calling the CAA endpoint, if the \`tag\` request parameter is not
provided, the default will be to set CAA at the account level. In this
case, all pending orders for all order book trading symbols under that
sub-account will be cancelled when CAA triggers, consistent with the
existing logic. If the \`tag\` request parameter is provided, CAA will
be set at the order tag level. When triggered, only pending orders of
order book trading symbols with the specified tag will be canceled,
while orders with other tags or no tags will remain unaffected.\
\
Users can run a maximum of 20 tag level CAAs simultaneously under the
same sub-account. The system will only count live tag level CAAs. CAAs
that have been triggered or revoked by the user will not be counted. The
user will receive error code 51071 when exceeding the limit.

### GET / Account rate limit {#order-book-trading-trade-get-account-rate-limit}

Get account rate limit related information.\

Only new order requests and amendment order requests will be counted
towards this limit. For batch order requests consisting of multiple
orders, each order will be counted individually.\

For details, please refer to [Fill ratio based sub-account rate
limit](/docs-v5/en/#overview-rate-limits-fill-ratio-based-sub-account-rate-limit)

#### Rate Limit: 1 request per second {#order-book-trading-trade-get-account-rate-limit-rate-limit-1-request-per-second}

#### Rate limit rule: User ID {#order-book-trading-trade-get-account-rate-limit-rate-limit-rule-user-id}

#### HTTP Request {#order-book-trading-trade-get-account-rate-limit-http-request}

`GET /api/v5/trade/account-rate-limit`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Get the account rate limit
GET /api/v5/trade/account-rate-limit
```
:::

#### Request Parameters {#order-book-trading-trade-get-account-rate-limit-request-parameters}

None

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
   "code":"0",
   "data":[
      {
         "accRateLimit":"2000",
         "fillRatio":"0.1234",
         "mainFillRatio":"0.1234",
         "nextAccRateLimit":"2000",
         "ts":"123456789000"
      }
   ],
   "msg":""
}
```
:::

#### Response Parameters {#order-book-trading-trade-get-account-rate-limit-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  fillRatio               String                  Sub account fill ratio
                                                  during the monitoring
                                                  period\
                                                  Applicable for users
                                                  with trading fee level
                                                  \>= VIP 5 and return
                                                  \"\" for others\
                                                  For accounts with no
                                                  trading volume during
                                                  the monitoring period,
                                                  return \"0\". For
                                                  accounts with trading
                                                  volume but no order
                                                  count due to our
                                                  counting logic, return
                                                  \"9999\".

  mainFillRatio           String                  Master account
                                                  aggregated fill ratio
                                                  during the monitoring
                                                  period\
                                                  Applicable for users
                                                  with trading fee level
                                                  \>= VIP 5 and return
                                                  \"\" for others\
                                                  For accounts with no
                                                  trading volume during
                                                  the monitoring period,
                                                  return \"0\"

  accRateLimit            String                  Current sub-account
                                                  rate limit per two
                                                  seconds

  nextAccRateLimit        String                  Expected sub-account
                                                  rate limit (per two
                                                  seconds) in the next
                                                  period\
                                                  Applicable for users
                                                  with trading fee level
                                                  \>= VIP 5 and return
                                                  \"\" for others

  ts                      String                  Data update time\
                                                  For users with trading
                                                  fee level \>= VIP 5,
                                                  the data will be
                                                  generated at 08:00 am
                                                  (UTC)\
                                                  For users with trading
                                                  fee level \< VIP 5,
                                                  return the current
                                                  timestamp
  -----------------------------------------------------------------------

### POST / Order precheck {#order-book-trading-trade-post-order-precheck}

This endpoint is used to precheck the account information before and
after placing the order.\
Only applicable to `Multi-currency margin mode`, and
`Portfolio margin mode`.

#### Rate Limit: 5 requests per 2 seconds {#order-book-trading-trade-post-order-precheck-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#order-book-trading-trade-post-order-precheck-rate-limit-rule-user-id}

#### Permission: Trade {#order-book-trading-trade-post-order-precheck-permission-trade}

#### HTTP Request {#order-book-trading-trade-post-order-precheck-http-request}

`POST /api/v5/trade/order-precheck`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# place order for SPOT
POST /api/v5/trade/order-precheck
 body
 {
    "instId":"BTC-USDT",
    "tdMode":"cash",
    "clOrdId":"b15",
    "side":"buy",
    "ordType":"limit",
    "px":"2.15",
    "sz":"2"
}
```
:::

#### Request Parameters {#order-book-trading-trade-post-order-precheck-request-parameters}

  -------------------------------------------------------------------------------------------------------------------
  Parameter           Type              Required          Description
  ------------------- ----------------- ----------------- -----------------------------------------------------------
  instId              String            Yes               Instrument ID, e.g. `BTC-USDT`

  tdMode              String            Yes               Trade mode\
                                                          Margin mode `cross` `isolated`\
                                                          Non-Margin mode `cash`\
                                                          `spot_isolated` (only applicable to SPOT lead trading,
                                                          `tdMode` should be `spot_isolated` for `SPOT` lead
                                                          trading.)

  side                String            Yes               Order side, `buy` `sell`

  posSide             String            Conditional       Position side\
                                                          The default is `net` in the `net` mode\
                                                          It is required in the `long/short` mode, and can only be
                                                          `long` or `short`.\
                                                          Only applicable to `FUTURES`/`SWAP`.

  ordType             String            Yes               Order type\
                                                          `market`: Market order\
                                                          `limit`: Limit order\
                                                          `post_only`: Post-only order\
                                                          `fok`: Fill-or-kill order\
                                                          `ioc`: Immediate-or-cancel order\
                                                          `optimal_limit_ioc`: Market order with immediate-or-cancel
                                                          order (applicable only to Expiry Futures and Perpetual
                                                          Futures).

  sz                  String            Yes               Quantity to buy or sell

  px                  String            Conditional       Order price. Only applicable to
                                                          `limit`,`post_only`,`fok`,`ioc`,`mmp`,`mmp_and_post_only`
                                                          order.

  reduceOnly          Boolean           No                Whether orders can only reduce in position size.\
                                                          Valid options: `true` or `false`. The default value is
                                                          `false`.\
                                                          Only applicable to `MARGIN` orders, and `FUTURES`/`SWAP`
                                                          orders in `net` mode\
                                                          Only applicable to `Futures mode` and
                                                          `Multi-currency margin`

  tgtCcy              String            No                Whether the target currency uses the quote or base
                                                          currency.\
                                                          `base_ccy`: Base currency ,`quote_ccy`: Quote currency\
                                                          Only applicable to `SPOT` Market Orders\
                                                          Default is `quote_ccy` for buy, `base_ccy` for sell

  attachAlgoOrds      Array of objects  No                TP/SL information attached when placing order

  \>                  String            No                Client-supplied Algo ID when placing order attaching TP/SL\
  attachAlgoClOrdId                                       A combination of case-sensitive alphanumerics, all numbers,
                                                          or all letters of up to 32 characters.\
                                                          It will be posted to `algoClOrdId` when placing TP/SL order
                                                          once the general order is filled completely.

  \> tpTriggerPx      String            Conditional       Take-profit trigger price\
                                                          For condition TP order, if you fill in this parameter, you
                                                          should fill in the take-profit order price as well.

  \> tpOrdPx          String            Conditional       Take-profit order price\
                                                          \
                                                          For condition TP order, if you fill in this parameter, you
                                                          should fill in the take-profit trigger price as well.\
                                                          For limit TP order, you need to fill in this parameter,
                                                          take-profit trigger needn't to be filled.\
                                                          If the price is -1, take-profit will be executed at the
                                                          market price.

  \> tpOrdKind        String            No                TP order kind\
                                                          `condition`\
                                                          `limit`\
                                                          The default is `condition`

  \> slTriggerPx      String            Conditional       Stop-loss trigger price\
                                                          If you fill in this parameter, you should fill in the
                                                          stop-loss order price.

  \> slOrdPx          String            Conditional       Stop-loss order price\
                                                          If you fill in this parameter, you should fill in the
                                                          stop-loss trigger price.\
                                                          If the price is -1, stop-loss will be executed at the
                                                          market price.

  \> tpTriggerPxType  String            No                Take-profit trigger price type\
                                                          `last`: last price\
                                                          `index`: index price\
                                                          `mark`: mark price\
                                                          The default is last

  \> slTriggerPxType  String            No                Stop-loss trigger price type\
                                                          `last`: last price\
                                                          `index`: index price\
                                                          `mark`: mark price\
                                                          The default is last

  \> sz               String            Conditional       Size. Only applicable to TP order of split TPs, and it is
                                                          required for TP order of split TPs
  -------------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "adjEq": "41.94347460746277",
            "adjEqChg": "-226.05616481626",
            "availBal": "0",
            "availBalChg": "0",
            "imr": "0",
            "imrChg": "57.74709688430927",
            "liab": "0",
            "liabChg": "0",
            "liabChgCcy": "",
            "liqPx": "6764.8556232031115",
            "liqPxDiff": "-57693.044376796888536773622035980224609375",
            "liqPxDiffRatio": "-0.8950500152315991",
            "mgnRatio": "0",
            "mgnRatioChg": "0",
            "mmr": "0",
            "mmrChg": "0",
            "posBal": "",
            "posBalChg": "",
            "type": ""
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#order-book-trading-trade-post-order-precheck-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  adjEq                   String                  Current adjusted /
                                                  Effective equity in
                                                  `USD`

  adjEqChg                String                  After placing order,
                                                  changed quantity of
                                                  adjusted / Effective
                                                  equity in `USD`

  imr                     String                  Current initial margin
                                                  requirement in `USD`

  imrChg                  String                  After placing order,
                                                  changed quantity of
                                                  initial margin
                                                  requirement in `USD`

  mmr                     String                  Current Maintenance
                                                  margin requirement in
                                                  `USD`

  mmrChg                  String                  After placing order,
                                                  changed quantity of
                                                  maintenance margin
                                                  requirement in `USD`

  mgnRatio                String                  Current Maintenance
                                                  margin ratio in `USD`

  mgnRatioChg             String                  After placing order,
                                                  changed quantity of
                                                  Maintenance margin
                                                  ratio in `USD`

  availBal                String                  Current available
                                                  balance in margin coin
                                                  currency, only
                                                  applicable to turn auto
                                                  borrow off

  availBalChg             String                  After placing order,
                                                  changed quantity of
                                                  available balance after
                                                  placing order, only
                                                  applicable to turn auto
                                                  borrow off

  liqPx                   String                  Current estimated
                                                  liquidation price

  liqPxDiff               String                  After placing order,
                                                  the distance between
                                                  estimated liquidation
                                                  price and mark price

  liqPxDiffRatio          String                  After placing order,
                                                  the distance rate
                                                  between estimated
                                                  liquidation price and
                                                  mark price

  posBal                  String                  Current positive asset,
                                                  only applicable to
                                                  margin isolated
                                                  position

  posBalChg               String                  After placing order,
                                                  positive asset of
                                                  margin isolated, only
                                                  applicable to margin
                                                  isolated position

  liab                    String                  Current liabilities of
                                                  currency\
                                                  For cross, it is cross
                                                  liabilities\
                                                  For isolated position,
                                                  it is isolated
                                                  liabilities

  liabChg                 String                  After placing order,
                                                  changed quantity of
                                                  liabilities\
                                                  For cross, it is cross
                                                  liabilities\
                                                  For isolated position,
                                                  it is isolated
                                                  liabilities

  liabChgCcy              String                  After placing order,
                                                  the unit of changed
                                                  liabilities quantity\
                                                  only applicable cross
                                                  and in auto borrow

  type                    String                  Unit type of positive
                                                  asset, only applicable
                                                  to margin isolated
                                                  position\
                                                  `1`: it is both base
                                                  currency before and
                                                  after placing order\
                                                  `2`: before plaing
                                                  order, it is base
                                                  currency. after placing
                                                  order, it is quota
                                                  currency.\
                                                  `3`: before plaing
                                                  order, it is quota
                                                  currency. after placing
                                                  order, it is base
                                                  currency\
                                                  `4`: it is both quota
                                                  currency before and
                                                  after placing order
  -----------------------------------------------------------------------
