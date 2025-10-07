# Trading Account

The API endpoints of `Account` require authentication.

## REST API {#trading-account-rest-api}

### Get instruments {#trading-account-rest-api-get-instruments}

Retrieve available instruments info of current account.

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-instruments-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID + Instrument Type {#trading-account-rest-api-get-instruments-rate-limit-rule-user-id-instrument-type}

#### Permission: Read {#trading-account-rest-api-get-instruments-permission-read}

#### HTTP Request {#trading-account-rest-api-get-instruments-http-request}

`GET /api/v5/account/instruments`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/instruments?instType=SPOT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1" # Production trading: 0, Demo trading: 1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.get_instruments(instType="SPOT")
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-instruments-request-parameters}

  ----------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ----------------------------
  instType          String            Yes               Instrument type\
                                                        `SPOT`: Spot\
                                                        `MARGIN`: Margin\
                                                        `SWAP`: Perpetual Futures\
                                                        `FUTURES`: Expiry Futures\
                                                        `OPTION`: Option

  instFamily        String            Conditional       Instrument family\
                                                        Only applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`.
                                                        If instType is `OPTION`,
                                                        `instFamily` is required.

  instId            String            No                Instrument ID
  ----------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "auctionEndTime": "",
            "baseCcy": "BTC",
            "ctMult": "",
            "ctType": "",
            "ctVal": "",
            "ctValCcy": "",
            "contTdSwTime": "1704876947000",
            "expTime": "",
            "futureSettlement": false,
            "instFamily": "",
            "instId": "BTC-EUR",
            "instType": "SPOT",
            "lever": "",
            "listTime": "1704876947000",
            "lotSz": "0.00000001",
            "maxIcebergSz": "9999999999.0000000000000000",
            "maxLmtAmt": "1000000",
            "maxLmtSz": "9999999999",
            "maxMktAmt": "1000000",
            "maxMktSz": "1000000",
            "maxStopSz": "1000000",
            "maxTriggerSz": "9999999999.0000000000000000",
            "maxTwapSz": "9999999999.0000000000000000",
            "minSz": "0.00001",
            "optType": "",
            "openType": "call_auction",
            "preMktSwTime": "",
            "quoteCcy": "EUR",
            "tradeQuoteCcyList": [
                "EUR"
            ],
            "settleCcy": "",
            "state": "live",
            "ruleType": "normal",
            "stk": "",
            "tickSz": "1",
            "uly": "",
            "instIdCode": 1000000000
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-instruments-response-parameters}

  --------------------------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- --------------------------------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID, e.g. `BTC-USD-SWAP`

  uly                     String                  Underlying, e.g. `BTC-USD`\
                                                  Only applicable to
                                                  `MARGIN/FUTURES`/`SWAP`/`OPTION`

  instFamily              String                  Instrument family, e.g. `BTC-USD`\
                                                  Only applicable to
                                                  `MARGIN/FUTURES`/`SWAP`/`OPTION`

  baseCcy                 String                  Base currency, e.g. `BTC` in`BTC-USDT`\
                                                  Only applicable to `SPOT`/`MARGIN`

  quoteCcy                String                  Quote currency, e.g. `USDT` in `BTC-USDT`\
                                                  Only applicable to `SPOT`/`MARGIN`

  settleCcy               String                  Settlement and margin currency, e.g. `BTC`\
                                                  Only applicable to `FUTURES`/`SWAP`/`OPTION`

  ctVal                   String                  Contract value\
                                                  Only applicable to `FUTURES`/`SWAP`/`OPTION`

  ctMult                  String                  Contract multiplier\
                                                  Only applicable to `FUTURES`/`SWAP`/`OPTION`

  ctValCcy                String                  Contract value currency\
                                                  Only applicable to `FUTURES`/`SWAP`/`OPTION`

  optType                 String                  Option type, `C`: Call `P`: put\
                                                  Only applicable to `OPTION`

  stk                     String                  Strike price\
                                                  Only applicable to `OPTION`

  listTime                String                  Listing time, Unix timestamp format in
                                                  milliseconds, e.g. `1597026383085`

  auctionEndTime          String                  ~~The end time of call auction, Unix
                                                  timestamp format in milliseconds, e.g.
                                                  `1597026383085`\
                                                  Only applicable to `SPOT` that are listed
                                                  through call auctions, return \"\" in other
                                                  cases (deprecated, use contTdSwTime)~~

  contTdSwTime            String                  Continuous trading switch time. The switch
                                                  time from call auction, prequote to
                                                  continuous trading, Unix timestamp format in
                                                  milliseconds. e.g. `1597026383085`.\
                                                  Only applicable to `SPOT`/`MARGIN` that are
                                                  listed through call auction or prequote,
                                                  return \"\" in other cases.

  preMktSwTime            String                  The time premarket swap switched to normal
                                                  swap, Unix timestamp format in milliseconds,
                                                  e.g. `1597026383085`.\
                                                  Only applicable premarket `SWAP`

  openType                String                  Open type\
                                                  `fix_price`: fix price opening\
                                                  `pre_quote`: pre-quote\
                                                  `call_auction`: call auction\
                                                  Only applicable to `SPOT`/`MARGIN`, return
                                                  \"\" for all other business lines

  expTime                 String                  Expiry time\
                                                  Applicable to
                                                  `SPOT`/`MARGIN`/`FUTURES`/`SWAP`/`OPTION`.
                                                  For `FUTURES`/`OPTION`, it is natural
                                                  delivery/exercise time. It is the instrument
                                                  offline time when there is
                                                  `SPOT/MARGIN/FUTURES/SWAP/` manual offline.
                                                  Update once change.

  lever                   String                  Max Leverage,\
                                                  Not applicable to `SPOT`, `OPTION`

  tickSz                  String                  Tick size, e.g. `0.0001`\
                                                  For Option, it is minimum tickSz among tick
                                                  band, please use \"Get option tick bands\"
                                                  if you want get option tickBands.

  lotSz                   String                  Lot size\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.

  minSz                   String                  Minimum order size\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.

  ctType                  String                  Contract type\
                                                  `linear`: linear contract\
                                                  `inverse`: inverse contract\
                                                  Only applicable to `FUTURES`/`SWAP`

  state                   String                  Instrument status\
                                                  `live`\
                                                  `suspend`\
                                                  `preopen` e.g. Futures and options contracts
                                                  rollover from generation to trading start;
                                                  certain symbols before they go live\
                                                  `test`: Test pairs, can\'t be traded

  ruleType                String                  Trading rule types\
                                                  `normal`: normal trading\
                                                  `pre_market`: pre-market trading

  maxLmtSz                String                  The maximum order quantity of a single limit
                                                  order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.

  maxMktSz                String                  The maximum order quantity of a single
                                                  market order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `USDT`.

  maxLmtAmt               String                  Max USD amount for a single limit order

  maxMktAmt               String                  Max USD amount for a single market order\
                                                  Only applicable to `SPOT`/`MARGIN`

  maxTwapSz               String                  The maximum order quantity of a single TWAP
                                                  order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.\
                                                  The minimum order quantity of a single TWAP
                                                  order is minSz\*2

  maxIcebergSz            String                  The maximum order quantity of a single
                                                  iceBerg order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.

  maxTriggerSz            String                  The maximum order quantity of a single
                                                  trigger order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `base currency`.

  maxStopSz               String                  The maximum order quantity of a single stop
                                                  market order.\
                                                  If it is a derivatives contract, the value
                                                  is the number of contracts.\
                                                  If it is `SPOT`/`MARGIN`, the value is the
                                                  quantity in `USDT`.

  futureSettlement        Boolean                 Whether daily settlement for expiry feature
                                                  is enabled\
                                                  Applicable to `FUTURES` `cross`

  tradeQuoteCcyList       Array of strings        List of quote currencies available for
                                                  trading, e.g. \[\"USD\", \"USDC\"\].

  instIdCode              Integer                 Instrument ID code.\
                                                  For simple binary encoding, you must use
                                                  `instIdCode` instead of `instId`.\
                                                  For the same `instId`, it\'s value may be
                                                  different between production and demo
                                                  trading.
  --------------------------------------------------------------------------------------------

listTime and contTdSwTime\
For spot symbols listed through a call auction or pre-open, listTime
represents the start time of the auction or pre-open, and contTdSwTime
indicates the end of the auction or pre-open and the start of continuous
trading. For other scenarios, listTime will mark the beginning of
continuous trading, and contTdSwTime will return an empty value \"\".

state\
The state will always change from \`preopen\` to \`live\` when the
listTime is reached.\
When a product is going to be delisted (e.g. when a FUTURES contract is
settled or OPTION contract is exercised), the instrument will not be
available.

### Get balance {#trading-account-rest-api-get-balance}

Retrieve a list of assets (with non-zero balance), remaining balance,
and available amount in the trading account.

Interest-free quota and discount rates are public data and not displayed
on the account interface.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-balance-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-balance-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-balance-permission-read}

#### HTTP Request {#trading-account-rest-api-get-balance-http-request}

`GET /api/v5/account/balance`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Get the balance of all assets in the account
GET /api/v5/account/balance

# Get the balance of BTC and ETH assets in the account
GET /api/v5/account/balance?ccy=BTC,ETH
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account balance
result = accountAPI.get_account_balance()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-balance-request-parameters}

  **Parameters**   **Types**   **Required**   **Description**
  ---------------- ----------- -------------- ---------------------------------------------------------------------------------------------------------
  ccy              String      No             Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` or `BTC,ETH`.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "adjEq": "55415.624719833286",
            "availEq": "55415.624719833286",
            "borrowFroz": "0",
            "details": [
                {
                    "autoLendStatus": "off",
                    "autoLendMtAmt": "0",
                    "availBal": "4834.317093622894",
                    "availEq": "4834.3170936228935",
                    "borrowFroz": "0",
                    "cashBal": "4850.435693622894",
                    "ccy": "USDT",
                    "crossLiab": "0",
                    "colRes": "0",
                    "collateralEnabled": false,
                    "collateralRestrict": false,
                    "colBorrAutoConversion": "0",
                    "disEq": "4991.542013297616",
                    "eq": "4992.890093622894",
                    "eqUsd": "4991.542013297616",
                    "smtSyncEq": "0",
                    "spotCopyTradingEq": "0",
                    "fixedBal": "0",
                    "frozenBal": "158.573",
                    "frpType": "0",
                    "imr": "",
                    "interest": "0",
                    "isoEq": "0",
                    "isoLiab": "0",
                    "isoUpl": "0",
                    "liab": "0",
                    "maxLoan": "0",
                    "mgnRatio": "",
                    "mmr": "",
                    "notionalLever": "",
                    "ordFrozen": "0",
                    "rewardBal": "0",
                    "spotInUseAmt": "",
                    "clSpotInUseAmt": "",
                    "maxSpotInUse": "",
                    "spotIsoBal": "0",
                    "stgyEq": "150",
                    "twap": "0",
                    "uTime": "1705449605015",
                    "upl": "-7.545600000000006",
                    "uplLiab": "0",
                    "spotBal": "",
                    "openAvgPx": "",
                    "accAvgPx": "",
                    "spotUpl": "",
                    "spotUplRatio": "",
                    "totalPnl": "",
                    "totalPnlRatio": ""
                }
            ],
            "imr": "0",
            "isoEq": "0",
            "mgnRatio": "",
            "mmr": "0",
            "notionalUsd": "0",
            "notionalUsdForBorrow": "0",
            "notionalUsdForFutures": "0",
            "notionalUsdForOption": "0",
            "notionalUsdForSwap": "0",
            "ordFroz": "",
            "totalEq": "55837.43556134779",
            "uTime": "1705474164160",
            "upl": "0",
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-balance-response-parameters}

  ---------------------------------------------------------------------------------------------------------------------------------------------------------
  **Parameters**          **Types**               **Description**
  ----------------------- ----------------------- ---------------------------------------------------------------------------------------------------------
  uTime                   String                  Update time of account information, millisecond format of Unix timestamp, e.g. `1597026383085`

  totalEq                 String                  The total amount of equity in `USD`

  isoEq                   String                  Isolated margin equity in `USD`\
                                                  Applicable to `Futures mode`/`Multi-currency margin`/`Portfolio margin`

  adjEq                   String                  Adjusted / Effective equity in `USD`\
                                                  The net fiat value of the assets in the account that can provide margins for spot, expiry futures,
                                                  perpetual futures and options under the cross-margin mode.\
                                                  In multi-ccy or PM mode, the asset and margin requirement will all be converted to USD value to process
                                                  the order check or liquidation.\
                                                  Due to the volatility of each currency market, our platform calculates the actual USD value of each
                                                  currency based on discount rates to balance market risks.\
                                                  Applicable to `Spot mode`/`Multi-currency margin` and `Portfolio margin`

  availEq                 String                  Account level available equity, excluding currencies that are restricted due to the collateralized
                                                  borrowing limit.\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  ordFroz                 String                  Cross margin frozen for pending orders in `USD`\
                                                  Only applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  imr                     String                  Initial margin requirement in `USD`\
                                                  The sum of initial margins of all open positions and pending orders under cross-margin mode in `USD`.\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  mmr                     String                  Maintenance margin requirement in `USD`\
                                                  The sum of maintenance margins of all open positions and pending orders under cross-margin mode in
                                                  `USD`.\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  borrowFroz              String                  Potential borrowing IMR of the account in `USD`\
                                                  Only applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`. It is \"\" for other margin
                                                  modes.

  mgnRatio                String                  Maintenance margin ratio in `USD`\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  notionalUsd             String                  Notional value of positions in `USD`\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  notionalUsdForBorrow    String                  Notional value for `Borrow` in USD\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  notionalUsdForSwap      String                  Notional value of positions for `Perpetual Futures` in USD\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  notionalUsdForFutures   String                  Notional value of positions for `Expiry Futures` in USD\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  notionalUsdForOption    String                  Notional value of positions for `Option` in USD\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  upl                     String                  Cross-margin info of unrealized profit and loss at the account level in `USD`\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  details                 Array of objects        Detailed asset information in all currencies

  \> ccy                  String                  Currency

  \> eq                   String                  Equity of currency

  \> cashBal              String                  Cash balance

  \> uTime                String                  Update time of currency balance information, Unix timestamp format in milliseconds, e.g. `1597026383085`

  \> isoEq                String                  Isolated margin equity of currency\
                                                  Applicable to `Futures mode`/`Multi-currency margin`/`Portfolio margin`

  \> availEq              String                  Available equity of currency\
                                                  Applicable to `Futures mode`/`Multi-currency margin`/`Portfolio margin`

  \> disEq                String                  Discount equity of currency in `USD`.\
                                                  Applicable to `Spot mode`(enabled spot borrow)/`Multi-currency margin`/`Portfolio margin`

  \> fixedBal             String                  Frozen balance for `Dip Sniper` and `Peak Sniper`

  \> availBal             String                  Available balance of currency

  \> frozenBal            String                  Frozen balance of currency

  \> ordFrozen            String                  Margin frozen for open orders\
                                                  Applicable to `Spot mode`/`Futures mode`/`Multi-currency margin`

  \> liab                 String                  Liabilities of currency\
                                                  It is a positive value, e.g. `21625.64`\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> upl                  String                  The sum of the unrealized profit & loss of all margin and derivatives positions of currency.\
                                                  Applicable to `Futures mode`/`Multi-currency margin`/`Portfolio margin`

  \> uplLiab              String                  Liabilities due to Unrealized loss of currency\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  \> crossLiab            String                  Cross liabilities of currency\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> rewardBal            String                  Trial fund balance

  \> isoLiab              String                  Isolated liabilities of currency\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`

  \> mgnRatio             String                  Cross maintenance margin ratio of currency\
                                                  The index for measuring the risk of a certain asset in the account.\
                                                  Applicable to `Futures mode` and when there is cross position

  \> imr                  String                  Cross initial margin requirement at the currency level\
                                                  Applicable to `Futures mode` and when there is cross position

  \> mmr                  String                  Cross maintenance margin requirement at the currency level\
                                                  Applicable to `Futures mode` and when there is cross position

  \> interest             String                  Accrued interest of currency\
                                                  It is a positive value, e.g. `9.01`\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> twap                 String                  Risk indicator of forced repayment\
                                                  Divided into multiple levels from 0 to 5, the larger the number, the more likely the forced repayment
                                                  will be triggered.\
                                                  Applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> frpType              String                  Forced repayment (FRP) type\
                                                  `0`: no FRP\
                                                  `1`: user based FRP\
                                                  `2`: platform based FRP\
                                                  \
                                                  Return `1`/`2` when twap is \>= 1, applicable to `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> maxLoan              String                  Max loan of currency\
                                                  Applicable to `cross` of `Spot mode`/`Multi-currency margin`/`Portfolio margin`

  \> eqUsd                String                  Equity in `USD` of currency

  \> borrowFroz           String                  Potential borrowing IMR of currency in `USD`\
                                                  Applicable to `Multi-currency margin`/`Portfolio margin`. It is \"\" for other margin modes.

  \> notionalLever        String                  Leverage of currency\
                                                  Applicable to `Futures mode`

  \> stgyEq               String                  Strategy equity

  \> isoUpl               String                  Isolated unrealized profit and loss of currency\
                                                  Applicable to `Futures mode`/`Multi-currency margin`/`Portfolio margin`

  \> spotInUseAmt         String                  Spot in use amount\
                                                  Applicable to `Portfolio margin`

  \> clSpotInUseAmt       String                  User-defined spot risk offset amount\
                                                  Applicable to `Portfolio margin`

  \> maxSpotInUse         String                  Max possible spot risk offset amount\
                                                  Applicable to `Portfolio margin`

  \> spotIsoBal           String                  Spot isolated balance\
                                                  Applicable to copy trading\
                                                  Applicable to `Spot mode`/`Futures mode`.

  \> smtSyncEq            String                  Smart sync equity\
                                                  The default is \"0\", only applicable to copy trader.

  \> spotCopyTradingEq    String                  Spot smart sync equity.\
                                                  The default is \"0\", only applicable to copy trader.

  \> spotBal              String                  Spot balance. The unit is currency, e.g. BTC. [More
                                                  details](https://www.okx.com/help/i-introduction-of-spot)

  \> openAvgPx            String                  Spot average cost price. The unit is USD. [More details](https://www.okx.com/help/i-introduction-of-spot)

  \> accAvgPx             String                  Spot accumulated cost price. The unit is USD. [More
                                                  details](https://www.okx.com/help/i-introduction-of-spot)

  \> spotUpl              String                  Spot unrealized profit and loss. The unit is USD. [More
                                                  details](https://www.okx.com/help/i-introduction-of-spot)

  \> spotUplRatio         String                  Spot unrealized profit and loss ratio. [More details](https://www.okx.com/help/i-introduction-of-spot)

  \> totalPnl             String                  Spot accumulated profit and loss. The unit is USD. [More
                                                  details](https://www.okx.com/help/i-introduction-of-spot)

  \> totalPnlRatio        String                  Spot accumulated profit and loss ratio. [More details](https://www.okx.com/help/i-introduction-of-spot)

  \> colRes               String                  Platform level collateral restriction status\
                                                  `0`: The restriction is not enabled.\
                                                  `1`: The restriction is not enabled. But the crypto is close to the platform\'s collateral limit.\
                                                  `2`: The restriction is enabled. This crypto can\'t be used as margin for your new orders. This may
                                                  result in failed orders. But it will still be included in the account\'s adjusted equity and doesn\'t
                                                  impact margin ratio.\
                                                  Refer to [Introduction to the platform collateralized borrowing
                                                  limit](https://www.okx.com/help/introduction-to-the-platforms-collateralized-borrowing-limit-mechanism)
                                                  for more details.

  \>                      String                  Risk indicator of auto conversion. Divided into multiple levels from 1-5, the larger the number, the more
  colBorrAutoConversion                           likely the repayment will be triggered. The default will be 0, indicating there is no risk currently. 5
                                                  means this user is undergoing auto conversion now, 4 means this user will undergo auto conversion soon
                                                  whereas 1/2/3 indicates there is a risk for auto conversion.\
                                                  Applicable to `Spot mode`/`Futures mode`/`Multi-currency margin`/`Portfolio margin`\
                                                  When the total liability for each crypto set as collateral exceeds a certain percentage of the
                                                  platform\'s total limit, the auto-conversion mechanism may be triggered. This may result in the automatic
                                                  sale of excess collateral crypto if you\'ve set this crypto as collateral and have large borrowings. To
                                                  lower this risk, consider reducing your use of the crypto as collateral or reducing your liabilities.\
                                                  Refer to [Introduction to the platform collateralized borrowing
                                                  limit](https://www.okx.com/help/introduction-to-the-platforms-collateralized-borrowing-limit-mechanism)
                                                  for more details.

  \> collateralRestrict   Boolean                 ~~Platform level collateralized borrow restriction\
                                                  `true`\
                                                  `false`~~(deprecated, use colRes instead)

  \> collateralEnabled    Boolean                 `true`: Collateral enabled\
                                                  `false`: Collateral disabled\
                                                  Applicable to `Multi-currency margin`

  \> autoLendStatus       String                  Auto lend status\
                                                  `unsupported`: auto lend is not supported by this currency\
                                                  `off`: auto lend is supported but turned off\
                                                  `pending`: auto lend is turned on but pending matching\
                                                  `active`: auto lend is turned on and matched

  \> autoLendMtAmt        String                  Auto lend currency matched amount\
                                                  Return \"0\" when autoLendStatus is `unsupported/off/pending`. Return matched amount when autoLendStatus
                                                  is `active`
  ---------------------------------------------------------------------------------------------------------------------------------------------------------

- Regarding more parameter details, you can refer to product
  documentations below:\
  [Futures mode: cross margin
  trading](https://www.okx.com/help/iii-single-currency-margin-cross-margin-trading)\
  [Multi-currency margin mode: cross margin
  trading](https://www.okx.com/help/iv-multi-currency-margin-mode-cross-margin-trading)\
  [Multi-currency margin mode vs. Portfolio margin
  mode](https://www.okx.com/help/vi-multi-currency-margin-mode-vs-portfolio-margin-mode)\

\"\" will be returned for inapplicable fields under the current account
level.

The currency details will not be returned when cashBal and eq is both 0.

Distribution of applicable fields under each account level are as
follows:

  **Parameters**          **Spot mode**   **Futures mode**   **Multi-currency margin mode**   **Portfolio margin mode**
  ----------------------- --------------- ------------------ -------------------------------- ---------------------------
  uTime                   Yes             Yes                Yes                              Yes
  totalEq                 Yes             Yes                Yes                              Yes
  isoEq                                   Yes                Yes                              Yes
  adjEq                   Yes                                Yes                              Yes
  availEq                                                    Yes                              Yes
  ordFroz                 Yes                                Yes                              Yes
  imr                     Yes                                Yes                              Yes
  mmr                     Yes                                Yes                              Yes
  borrowFroz              Yes                                Yes                              Yes
  mgnRatio                Yes                                Yes                              Yes
  notionalUsd             Yes                                Yes                              Yes
  notionalUsdForSwap                                         Yes                              Yes
  notionalUsdForFutures                                      Yes                              Yes
  notionalUsdForOption    Yes                                Yes                              Yes
  notionalUsdForBorrow    Yes                                Yes                              Yes
  upl                                                        Yes                              Yes
  details                                                    Yes                              Yes
  \> ccy                  Yes             Yes                Yes                              Yes
  \> eq                   Yes             Yes                Yes                              Yes
  \> cashBal              Yes             Yes                Yes                              Yes
  \> uTime                Yes             Yes                Yes                              Yes
  \> isoEq                                Yes                Yes                              Yes
  \> availEq                              Yes                Yes                              Yes
  \> disEq                Yes                                Yes                              Yes
  \> availBal             Yes             Yes                Yes                              Yes
  \> frozenBal            Yes             Yes                Yes                              Yes
  \> ordFrozen            Yes             Yes                Yes                              Yes
  \> liab                 Yes                                Yes                              Yes
  \> upl                                  Yes                Yes                              Yes
  \> uplLiab                                                 Yes                              Yes
  \> crossLiab            Yes                                Yes                              Yes
  \> isoLiab                                                 Yes                              Yes
  \> mgnRatio                             Yes
  \> interest             Yes                                Yes                              Yes
  \> twap                 Yes                                Yes                              Yes
  \> maxLoan              Yes                                Yes                              Yes
  \> eqUsd                Yes             Yes                Yes                              Yes
  \> borrowFroz           Yes                                Yes                              Yes
  \> notionalLever                        Yes
  \> stgyEq               Yes             Yes                Yes                              Yes
  \> isoUpl                               Yes                Yes                              Yes
  \> spotInUseAmt                                                                             Yes
  \> spotIsoBal           Yes             Yes
  \> imr                                  Yes
  \> mmr                                  Yes
  \> smtSyncEq            Yes             Yes                Yes                              Yes
  \> spotCopyTradingEq    Yes             Yes                Yes                              Yes
  \> spotBal              Yes             Yes                Yes                              Yes
  \> openAvgPx            Yes             Yes                Yes                              Yes
  \> accAvgPx             Yes             Yes                Yes                              Yes
  \> spotUpl              Yes             Yes                Yes                              Yes
  \> spotUplRatio         Yes             Yes                Yes                              Yes
  \> totalPnl             Yes             Yes                Yes                              Yes
  \> totalPnlRatio c      Yes             Yes                Yes                              Yes
  \> collateralEnabled                                       Yes

### Get positions {#trading-account-rest-api-get-positions}

Retrieve information on your positions. When the account is in `net`
mode, `net` positions will be displayed, and when the account is in
`long/short` mode, `long` or `short` positions will be displayed. Return
in reverse chronological order using ctime.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-positions-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-positions-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-positions-permission-read}

#### HTTP Request {#trading-account-rest-api-get-positions-http-request}

`GET /api/v5/account/positions`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Query BTC-USDT position information
GET /api/v5/account/positions?instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get positions information
result = accountAPI.get_positions()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-positions-request-parameters}

  ------------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- ------------------
  instType          String            No                Instrument type\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`\
                                                        `instId` will be
                                                        checked against
                                                        `instType` when
                                                        both parameters
                                                        are passed.

  instId            String            No                Instrument ID,
                                                        e.g.
                                                        `BTC-USDT-SWAP`.
                                                        Single instrument
                                                        ID or multiple
                                                        instrument IDs (no
                                                        more than 10)
                                                        separated with
                                                        comma

  posId             String            No                Single position ID
                                                        or multiple
                                                        position IDs (no
                                                        more than 20)
                                                        separated with
                                                        comma.\
                                                        There is attribute
                                                        expiration, the
                                                        posId and position
                                                        information will
                                                        be cleared if it
                                                        is more than 30
                                                        days after the
                                                        last full close
                                                        position.
  ------------------------------------------------------------------------

instId\
If the instrument ever had position and its open interest is 0, it will
return the position information with specific instId. It will not return
the position information with specific instId if there is no valid
posId; it will not return the position information without specific
instId.

In the isolated margin trading settings, if it is set to the manual
transfers mode, after the position is transferred to the margin, a
position with a position of 0 will be generated

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "adl": "1",
            "availPos": "0.00190433573",
            "avgPx": "62961.4",
            "baseBal": "",
            "baseBorrowed": "",
            "baseInterest": "",
            "bePx": "",
            "bizRefId": "",
            "bizRefType": "",
            "cTime": "1724740225685",
            "ccy": "BTC",
            "clSpotInUseAmt": "",
            "closeOrderAlgo": [],
            "deltaBS": "",
            "deltaPA": "",
            "fee": "",
            "fundingFee": "",
            "gammaBS": "",
            "gammaPA": "",
            "idxPx": "62890.5",
            "imr": "",
            "instId": "BTC-USDT",
            "instType": "MARGIN",
            "interest": "0",
            "last": "62892.9",
            "lever": "5",
            "liab": "-99.9998177776581948",
            "liabCcy": "USDT",
            "liqPenalty": "",
            "liqPx": "53615.448336593756",
            "margin": "0.000317654",
            "markPx": "62891.9",
            "maxSpotInUseAmt": "",
            "mgnMode": "isolated",
            "mgnRatio": "9.404143929947395",
            "mmr": "0.0000318005395854",
            "notionalUsd": "119.756628017499",
            "optVal": "",
            "pendingCloseOrdLiabVal": "0",
            "pnl": "",
            "pos": "0.00190433573",
            "posCcy": "BTC",
            "posId": "1752810569801498626",
            "posSide": "net",
            "quoteBal": "",
            "quoteBorrowed": "",
            "quoteInterest": "",
            "realizedPnl": "",
            "spotInUseAmt": "",
            "spotInUseCcy": "",
            "thetaBS": "",
            "thetaPA": "",
            "tradeId": "785524470",
            "uTime": "1724742632153",
            "upl": "-0.0000033452492717",
            "uplLastPx": "-0.0000033199677697",
            "uplRatio": "-0.0105311101755551",
            "uplRatioLastPx": "-0.0104515220008934",
            "usdPx": "",
            "vegaBS": "",
            "vegaPA": "",
            "nonSettleAvgPx":"",
            "settledPnl":""
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-positions-response-parameters}

  -------------------------------------------------------------------------------------------------------------------
  **Parameter**            **Type**                **Description**
  ------------------------ ----------------------- ------------------------------------------------------------------
  instType                 String                  Instrument type

  mgnMode                  String                  Margin mode\
                                                   `cross`\
                                                   `isolated`

  posId                    String                  Position ID

  posSide                  String                  Position side\
                                                   `long`, `pos` is positive\
                                                   `short`, `pos` is positive\
                                                   `net` (`FUTURES`/`SWAP`/`OPTION`: positive `pos` means long
                                                   position and negative `pos` means short position. For `MARGIN`,
                                                   `pos` is always positive, `posCcy` being base currency means long
                                                   position, `posCcy` being quote currency means short position.)

  pos                      String                  Quantity of positions. In the isolated margin mode, when doing
                                                   manual transfers, a position with pos of `0` will be generated
                                                   after the deposit is transferred

  baseBal                  String                  ~~Base currency balance, only applicable to `MARGIN`（Quick Margin
                                                   Mode）~~(Deprecated)

  quoteBal                 String                  ~~Quote currency balance, only applicable to `MARGIN`（Quick
                                                   Margin Mode）~~(Deprecated)

  baseBorrowed             String                  ~~Base currency amount already borrowed, only applicable to
                                                   MARGIN(Quick Margin Mode）~~(Deprecated)

  baseInterest             String                  ~~Base Interest, undeducted interest that has been incurred, only
                                                   applicable to MARGIN(Quick Margin Mode）~~(Deprecated)

  quoteBorrowed            String                  ~~Quote currency amount already borrowed, only applicable to
                                                   MARGIN(Quick Margin Mode）~~(Deprecated)

  quoteInterest            String                  ~~Quote Interest, undeducted interest that has been incurred, only
                                                   applicable to MARGIN(Quick Margin Mode）~~(Deprecated)

  posCcy                   String                  Position currency, only applicable to `MARGIN` positions.

  availPos                 String                  Position that can be closed\
                                                   Only applicable to `MARGIN` and `OPTION`.\
                                                   For `MARGIN` position, the rest of sz will be `SPOT` trading after
                                                   the liability is repaid while closing the position. Please get the
                                                   available reduce-only amount from \"Get maximum available tradable
                                                   amount\" if you want to reduce the amount of `SPOT` trading as
                                                   much as possible.

  avgPx                    String                  Average open price\
                                                   Under cross-margin mode, the entry price of expiry futures will
                                                   update at settlement to the last settlement price, and when the
                                                   position is opened or increased.

  nonSettleAvgPx           String                  Non-settlement entry price\
                                                   The non-settlement entry price only reflects the average price at
                                                   which the position is opened or increased.\
                                                   Applicable to `cross` `FUTURES` positions.

  markPx                   String                  Latest Mark price

  upl                      String                  Unrealized profit and loss calculated by mark price.

  uplRatio                 String                  Unrealized profit and loss ratio calculated by mark price.

  uplLastPx                String                  Unrealized profit and loss calculated by last price. Main usage is
                                                   showing, actual value is upl.

  uplRatioLastPx           String                  Unrealized profit and loss ratio calculated by last price.

  instId                   String                  Instrument ID, e.g. `BTC-USDT-SWAP`

  lever                    String                  Leverage\
                                                   Not applicable to `OPTION` and positions of cross margin mode
                                                   under `Portfolio margin`

  liqPx                    String                  Estimated liquidation price\
                                                   Not applicable to `OPTION`

  imr                      String                  Initial margin requirement, only applicable to `cross`.

  margin                   String                  Margin, can be added or reduced. Only applicable to `isolated`.

  mgnRatio                 String                  Maintenance margin ratio

  mmr                      String                  Maintenance margin requirement

  liab                     String                  Liabilities, only applicable to `MARGIN`.

  liabCcy                  String                  Liabilities currency, only applicable to `MARGIN`.

  interest                 String                  Interest. Undeducted interest that has been incurred.

  tradeId                  String                  Last trade ID

  optVal                   String                  Option Value, only applicable to `OPTION`.

  pendingCloseOrdLiabVal   String                  The amount of close orders of isolated margin liability.

  notionalUsd              String                  Notional value of positions in `USD`

  adl                      String                  Auto-deleveraging (ADL) indicator\
                                                   Divided into 5 levels, from 1 to 5, the smaller the number, the
                                                   weaker the adl intensity.\
                                                   Only applicable to `FUTURES/SWAP/OPTION`

  ccy                      String                  Currency used for margin

  last                     String                  Latest traded price

  idxPx                    String                  Latest underlying index price

  usdPx                    String                  Latest USD price of the `ccy` on the market, only applicable to
                                                   `OPTION`

  bePx                     String                  Breakeven price

  deltaBS                  String                  delta: Black-Scholes Greeks in dollars, only applicable to
                                                   `OPTION`

  deltaPA                  String                  delta: Greeks in coins, only applicable to `OPTION`

  gammaBS                  String                  gamma: Black-Scholes Greeks in dollars, only applicable to
                                                   `OPTION`

  gammaPA                  String                  gamma: Greeks in coins, only applicable to `OPTION`

  thetaBS                  String                  theta：Black-Scholes Greeks in dollars, only applicable to
                                                   `OPTION`

  thetaPA                  String                  theta：Greeks in coins, only applicable to `OPTION`

  vegaBS                   String                  vega：Black-Scholes Greeks in dollars, only applicable to `OPTION`

  vegaPA                   String                  vega：Greeks in coins, only applicable to `OPTION`

  spotInUseAmt             String                  Spot in use amount\
                                                   Applicable to `Portfolio margin`

  spotInUseCcy             String                  Spot in use unit, e.g. `BTC`\
                                                   Applicable to `Portfolio margin`

  clSpotInUseAmt           String                  User-defined spot risk offset amount\
                                                   Applicable to `Portfolio margin`

  maxSpotInUseAmt          String                  Max possible spot risk offset amount\
                                                   Applicable to `Portfolio margin`

  bizRefId                 String                  External business id, e.g. experience coupon id

  bizRefType               String                  External business type

  realizedPnl              String                  Realized profit and loss\
                                                   Only applicable to `FUTURES`/`SWAP`/`OPTION`\
                                                   `realizedPnl`=`pnl`+`fee`+`fundingFee`+`liqPenalty`+`settledPnl`

  settledPnl               String                  Accumulated settled profit and loss (calculated by settlement
                                                   price)\
                                                   Only applicable to `cross` `FUTURES`

  pnl                      String                  Accumulated pnl of closing order(s) (excluding the fee).

  fee                      String                  Accumulated fee\
                                                   Negative number represents the user transaction fee charged by the
                                                   platform.Positive number represents rebate.

  fundingFee               String                  Accumulated funding fee

  liqPenalty               String                  Accumulated liquidation penalty. It is negative when there is a
                                                   value.

  closeOrderAlgo           Array of objects        Close position algo orders attached to the position. This array
                                                   will have values only after you request \"Place algo order\" with
                                                   `closeFraction`=1.

  \> algoId                String                  Algo ID

  \> slTriggerPx           String                  Stop-loss trigger price.

  \> slTriggerPxType       String                  Stop-loss trigger price type.\
                                                   `last`: last price\
                                                   `index`: index price\
                                                   `mark`: mark price

  \> tpTriggerPx           String                  Take-profit trigger price.

  \> tpTriggerPxType       String                  Take-profit trigger price type.\
                                                   `last`: last price\
                                                   `index`: index price\
                                                   `mark`: mark price

  \> closeFraction         String                  Fraction of position to be closed when the algo order is
                                                   triggered.

  cTime                    String                  Creation time, Unix timestamp format in milliseconds, e.g.
                                                   `1597026383085`

  uTime                    String                  Latest time position was adjusted, Unix timestamp format in
                                                   milliseconds, e.g. `1597026383085`
  -------------------------------------------------------------------------------------------------------------------

As for portfolio margin account, the IMR and MMR of the position are
calculated in risk unit granularity, thus their values of the same risk
unit cross positions are the same.

### Get positions history {#trading-account-rest-api-get-positions-history}

Retrieve the updated position data for the last 3 months. Return in
reverse chronological order using utime. Getting positions history is
supported under Portfolio margin mode since **04:00 AM (UTC) on November
11, 2024**.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-positions-history-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-positions-history-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-positions-history-permission-read}

#### HTTP Request {#trading-account-rest-api-get-positions-history-http-request}

`GET /api/v5/account/positions-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/positions-history
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get positions history
result = accountAPI.get_positions_history()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-positions-history-request-parameters}

  -----------------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------------------------
  instType          String            No                Instrument type\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instId            String            No                Instrument ID, e.g. `BTC-USD-SWAP`

  mgnMode           String            No                Margin mode\
                                                        `cross` `isolated`

  type              String            No                The type of latest close position\
                                                        `1`: Close position
                                                        partially;`2`：Close
                                                        all;`3`：Liquidation;`4`：Partial
                                                        liquidation; `5`：ADL - position
                                                        not fully closed; `6`：ADL -
                                                        position fully closed\
                                                        It is the latest type if there are
                                                        several types for the same
                                                        position.

  posId             String            No                Position ID. There is attribute
                                                        expiration. The posId will be
                                                        expired if it is more than 30 days
                                                        after the last full close position,
                                                        then position will use new posId.

  after             String            No                Pagination of data to return
                                                        records earlier than the requested
                                                        `uTime`, Unix timestamp format in
                                                        milliseconds, e.g. `1597026383085`

  before            String            No                Pagination of data to return
                                                        records newer than the requested
                                                        `uTime`, Unix timestamp format in
                                                        milliseconds, e.g. `1597026383085`

  limit             String            No                Number of results per request. The
                                                        maximum is 100. The default is 100.
                                                        All records that have the same
                                                        `uTime` will be returned at the
                                                        current request
  -----------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "cTime": "1654177169995",
            "ccy": "BTC",
            "closeAvgPx": "29786.5999999789081085",
            "closeTotalPos": "1",
            "instId": "BTC-USD-SWAP",
            "instType": "SWAP",
            "lever": "10.0",
            "mgnMode": "cross",
            "openAvgPx": "29783.8999999995535393",
            "openMaxPos": "1",
            "realizedPnl": "0.001",
            "fee": "-0.0001",
            "fundingFee": "0",
            "liqPenalty": "0",
            "pnl": "0.0011",
            "pnlRatio": "0.000906447858888",
            "posId": "452587086133239818",
            "posSide": "long",
            "direction": "long",
            "triggerPx": "",
            "type": "1",
            "uTime": "1654177174419",
            "uly": "BTC-USD",
            "nonSettleAvgPx":"",
            "settledPnl":""
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-positions-history-response-parameters}

  ------------------------------------------------------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- ------------------------------------------------------------------
  instType                String                  Instrument type

  instId                  String                  Instrument ID

  mgnMode                 String                  Margin mode\
                                                  `cross` `isolated`

  type                    String                  The type of latest close position\
                                                  `1`：Close position partially;`2`：Close
                                                  all;`3`：Liquidation;`4`：Partial liquidation; `5`：ADL;\
                                                  It is the latest type if there are several types for the same
                                                  position.

  cTime                   String                  Created time of position

  uTime                   String                  Updated time of position

  openAvgPx               String                  Average price of opening position\
                                                  Under cross-margin mode, the entry price of expiry futures will
                                                  update at settlement to the last settlement price, and when the
                                                  position is opened or increased.

  nonSettleAvgPx          String                  Non-settlement entry price\
                                                  The non-settlement entry price only reflects the average price at
                                                  which the position is opened or increased.\
                                                  Only applicable to `cross` `FUTURES`

  closeAvgPx              String                  Average price of closing position

  posId                   String                  Position ID

  openMaxPos              String                  Max quantity of position

  closeTotalPos           String                  Position\'s cumulative closed volume

  realizedPnl             String                  Realized profit and loss\
                                                  Only applicable to `FUTURES`/`SWAP`/`OPTION`\
                                                  `realizedPnl`=`pnl`+`fee`+`fundingFee`+`liqPenalty`+`settledPnl`

  settledPnl              String                  Accumulated settled profit and loss (calculated by settlement
                                                  price)\
                                                  Only applicable to `cross` `FUTURES`

  pnlRatio                String                  Realized P&L ratio

  fee                     String                  Accumulated fee\
                                                  Negative number represents the user transaction fee charged by the
                                                  platform.Positive number represents rebate.

  fundingFee              String                  Accumulated funding fee

  liqPenalty              String                  Accumulated liquidation penalty. It is negative when there is a
                                                  value.

  pnl                     String                  Profit and loss (excluding the fee).

  posSide                 String                  Position mode side\
                                                  `long`: Hedge mode long\
                                                  `short`: Hedge mode short\
                                                  `net`: Net mode

  lever                   String                  Leverage

  direction               String                  Direction: `long` `short`\
                                                  Only applicable to `MARGIN/FUTURES/SWAP/OPTION`

  triggerPx               String                  trigger mark price. There is value when `type` is equal to `3`,
                                                  `4` or `5`. It is \"\" when `type` is equal to `1` or `2`

  uly                     String                  Underlying

  ccy                     String                  Currency used for margin
  ------------------------------------------------------------------------------------------------------------------

### Get account and position risk {#trading-account-rest-api-get-account-and-position-risk}

Get account and position risk

Obtain basic information about accounts and positions on the same time
snapshot

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-account-and-position-risk-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-account-and-position-risk-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-account-and-position-risk-permission-read}

#### HTTP Request {#trading-account-rest-api-get-account-and-position-risk-http-request}

`GET /api/v5/account/account-position-risk`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/account-position-risk
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account and position risk
result = accountAPI.get_account_position_risk()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-account-and-position-risk-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instType          String            No                Instrument type\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "data":[
        {
            "adjEq":"174238.6793649711331679",
            "balData":[
                {
                    "ccy":"BTC",
                    "disEq":"78846.7803721021362242",
                    "eq":"1.3863533369419636"
                },
                {
                    "ccy":"USDT",
                    "disEq":"73417.2495112863300127",
                    "eq":"73323.395564963177146"
                }
            ],
            "posData":[
                {
                    "baseBal": "0.4",
                    "ccy": "",
                    "instId": "BTC-USDT",
                    "instType": "MARGIN",
                    "mgnMode": "isolated",
                    "notionalCcy": "0",
                    "notionalUsd": "0",
                    "pos": "0",
                    "posCcy": "",
                    "posId": "310388685292318723",
                    "posSide": "net",
                    "quoteBal": "0"
                }
            ],
            "ts":"1620282889345"
        }
    ],
    "msg":""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-account-and-position-risk-response-parameters}

  -----------------------------------------------------------------------------
  **Parameters**          **Types**               **Description**
  ----------------------- ----------------------- -----------------------------
  ts                      String                  Update time of account
                                                  information, millisecond
                                                  format of Unix timestamp,
                                                  e.g. `1597026383085`

  adjEq                   String                  Adjusted / Effective equity
                                                  in `USD`\
                                                  Applicable to
                                                  `Multi-currency margin` and
                                                  `Portfolio margin`

  balData                 Array of objects        Detailed asset information in
                                                  all currencies

  \> ccy                  String                  Currency

  \> eq                   String                  Equity of currency

  \> disEq                String                  Discount equity of currency
                                                  in `USD`.

  posData                 Array of objects        Detailed position information
                                                  in all currencies

  \> instType             String                  Instrument type

  \> mgnMode              String                  Margin mode\
                                                  `cross`\
                                                  `isolated`

  \> posId                String                  Position ID

  \> instId               String                  Instrument ID, e.g.
                                                  `BTC-USDT-SWAP`

  \> pos                  String                  Quantity of positions
                                                  `contract`. In the isolated
                                                  margin mode, when doing
                                                  manual transfers, a position
                                                  with pos of `0` will be
                                                  generated after the deposit
                                                  is transferred

  \> baseBal              String                  ~~Base currency balance, only
                                                  applicable to `MARGIN`（Quick
                                                  Margin Mode）~~(Deprecated)

  \> quoteBal             String                  ~~Quote currency balance,
                                                  only applicable to
                                                  `MARGIN`（Quick Margin
                                                  Mode）~~(Deprecated)

  \> posSide              String                  Position side\
                                                  `long`\
                                                  `short`\
                                                  `net`
                                                  (`FUTURES`/`SWAP`/`OPTION`:
                                                  positive `pos` means long
                                                  position and negative `pos`
                                                  means short position.
                                                  `MARGIN`: `posCcy` being base
                                                  currency means long position,
                                                  `posCcy` being quote currency
                                                  means short position.)

  \> posCcy               String                  Position currency, only
                                                  applicable to `MARGIN`
                                                  positions.

  \> ccy                  String                  Currency used for margin

  \> notionalCcy          String                  Notional value of positions
                                                  in `coin`

  \> notionalUsd          String                  Notional value of positions
                                                  in `USD`
  -----------------------------------------------------------------------------

### Get bills details (last 7 days) {#trading-account-rest-api-get-bills-details-last-7-days}

Retrieve the bills of the account. The bill refers to all transaction
records that result in changing the balance of an account. Pagination is
supported, and the response is sorted with the most recent first. This
endpoint can retrieve data from the last 7 days.

#### Rate Limit: 5 requests per second {#trading-account-rest-api-get-bills-details-last-7-days-rate-limit-5-requests-per-second}

#### Rate limit rule: User ID {#trading-account-rest-api-get-bills-details-last-7-days-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-bills-details-last-7-days-permission-read}

#### HTTP Request {#trading-account-rest-api-get-bills-details-last-7-days-http-request}

`GET /api/v5/account/bills`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/bills

GET /api/v5/account/bills?instType=MARGIN
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get bills details (last 7 days)
result = accountAPI.get_account_bills()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-bills-details-last-7-days-request-parameters}

  -------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -------------------
  instType          String            No                Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`

  ccy               String            No                Bill currency

  mgnMode           String            No                Margin mode\
                                                        `isolated`\
                                                        `cross`

  ctType            String            No                Contract type\
                                                        `linear`\
                                                        `inverse`\
                                                        Only applicable to
                                                        `FUTURES`/`SWAP`

  type              String            No                Bill type\
                                                        `1`: Transfer\
                                                        `2`: Trade\
                                                        `3`: Delivery\
                                                        `4`: Forced
                                                        repayment\
                                                        `5`: Liquidation\
                                                        `6`: Margin
                                                        transfer\
                                                        `7`: Interest
                                                        deduction\
                                                        `8`: Funding fee\
                                                        `9`: ADL\
                                                        `10`: Clawback\
                                                        `11`: System token
                                                        conversion\
                                                        `12`: Strategy
                                                        transfer\
                                                        `13`: DDH\
                                                        `14`: Block trade\
                                                        `15`: Quick Margin\
                                                        `16`: Borrowing\
                                                        `22`: Repay\
                                                        `24`: Spread
                                                        trading\
                                                        `26`: Structured
                                                        products\
                                                        `27`: Convert\
                                                        `28`: Easy convert\
                                                        `29`: One-click
                                                        repay\
                                                        `30`: Simple trade\
                                                        `32`: Move
                                                        position\
                                                        `33`: Loans\
                                                        `34`: Settlement\
                                                        `250`: Copy trader
                                                        profit sharing
                                                        expenses\
                                                        `251`: Copy trader
                                                        profit sharing
                                                        refund

  subType           String            No                Bill subtype\
                                                        `1`: Buy\
                                                        `2`: Sell\
                                                        `3`: Open long\
                                                        `4`: Open short\
                                                        `5`: Close long\
                                                        `6`: Close short\
                                                        `9`: Interest
                                                        deduction for
                                                        Market loans\
                                                        `11`: Transfer in\
                                                        `12`: Transfer out\
                                                        `14`: Interest
                                                        deduction for VIP
                                                        loans\
                                                        `160`: Manual
                                                        margin increase\
                                                        `161`: Manual
                                                        margin decrease\
                                                        `162`: Auto margin
                                                        increase\
                                                        `114`: Forced
                                                        repayment buy\
                                                        `115`: Forced
                                                        repayment sell\
                                                        `118`: System token
                                                        conversion transfer
                                                        in\
                                                        `119`: System token
                                                        conversion transfer
                                                        out\
                                                        `100`: Partial
                                                        liquidation close
                                                        long\
                                                        `101`: Partial
                                                        liquidation close
                                                        short\
                                                        `102`: Partial
                                                        liquidation buy\
                                                        `103`: Partial
                                                        liquidation sell\
                                                        `104`: Liquidation
                                                        long\
                                                        `105`: Liquidation
                                                        short\
                                                        `106`: Liquidation
                                                        buy\
                                                        `107`: Liquidation
                                                        sell\
                                                        `108`: Clawback\
                                                        `110`: Liquidation
                                                        transfer in\
                                                        `111`: Liquidation
                                                        transfer out\
                                                        `125`: ADL close
                                                        long\
                                                        `126`: ADL close
                                                        short\
                                                        `127`: ADL buy\
                                                        `128`: ADL sell\
                                                        `131`: ddh buy\
                                                        `132`: ddh sell\
                                                        `170`:
                                                        Exercised(ITM buy
                                                        side)\
                                                        `171`: Counterparty
                                                        exercised(ITM sell
                                                        side)\
                                                        `172`:
                                                        Expired(Non-ITM buy
                                                        and sell side)\
                                                        `112`: Delivery
                                                        long (applicable to
                                                        `FUTURES`
                                                        expiration and
                                                        `SWAP` delisting)\
                                                        `113`: Delivery
                                                        short (applicable
                                                        to `FUTURES`
                                                        expiration and
                                                        `SWAP` delisting)\
                                                        `117`:
                                                        Delivery/Exercise
                                                        clawback\
                                                        `173`: Funding fee
                                                        expense\
                                                        `174`: Funding fee
                                                        income\
                                                        `200`:System
                                                        transfer in\
                                                        `201`: Manually
                                                        transfer in\
                                                        `202`: System
                                                        transfer out\
                                                        `203`: Manually
                                                        transfer out\
                                                        `204`: block trade
                                                        buy\
                                                        `205`: block trade
                                                        sell\
                                                        `206`: block trade
                                                        open long\
                                                        `207`: block trade
                                                        open short\
                                                        `208`: block trade
                                                        close long\
                                                        `209`: block trade
                                                        close short\
                                                        `210`: Manual
                                                        Borrowing of quick
                                                        margin\
                                                        `211`: Manual
                                                        Repayment of quick
                                                        margin\
                                                        `212`: Auto borrow
                                                        of quick margin\
                                                        `213`: Auto repay
                                                        of quick margin\
                                                        `220`: Transfer in
                                                        when using USDT to
                                                        buy OPTION\
                                                        `221`: Transfer out
                                                        when using USDT to
                                                        buy OPTION\
                                                        `16`: Repay
                                                        forcibly\
                                                        `17`: Repay
                                                        interest by
                                                        borrowing forcibly\
                                                        `224`: Repayment
                                                        transfer in\
                                                        `225`: Repayment
                                                        transfer out\
                                                        `236`: Easy convert
                                                        in\
                                                        `237`: Easy convert
                                                        out\
                                                        `250`: Profit
                                                        sharing expenses\
                                                        `251`: Profit
                                                        sharing refund\
                                                        `280`: SPOT profit
                                                        sharing expenses\
                                                        `281`: SPOT profit
                                                        sharing refund\
                                                        `282`: Spot profit
                                                        share income\
                                                        `283`: Asset
                                                        transfer for spot
                                                        copy trading\
                                                        `270`: Spread
                                                        trading buy\
                                                        `271`: Spread
                                                        trading sell\
                                                        `272`: Spread
                                                        trading open long\
                                                        `273`: Spread
                                                        trading open short\
                                                        `274`: Spread
                                                        trading close long\
                                                        `275`: Spread
                                                        trading close
                                                        short\
                                                        `280`: SPOT profit
                                                        sharing expenses\
                                                        `281`: SPOT profit
                                                        sharing refund\
                                                        `284`: Copy trade
                                                        automatic transfer
                                                        in\
                                                        `285`: Copy trade
                                                        manual transfer in\
                                                        `286`: Copy trade
                                                        automatic transfer
                                                        out\
                                                        `287`: Copy trade
                                                        manual transfer
                                                        out\
                                                        `290`: Crypto dust
                                                        auto-transfer out\
                                                        ~~`293`: Fixed loan
                                                        interest
                                                        deduction~~\
                                                        ~~`294`: Fixed loan
                                                        interest refund~~\
                                                        ~~`295`: Fixed loan
                                                        overdue penalty~~\
                                                        `296`: From
                                                        structured order
                                                        placements\
                                                        `297`: To
                                                        structured order
                                                        placements\
                                                        `298`: From
                                                        structured
                                                        settlements\
                                                        `299`: To
                                                        structured
                                                        settlements\
                                                        `306`: Manual
                                                        borrow\
                                                        `307`: Auto borrow\
                                                        `308`: Manual
                                                        repay\
                                                        `309`: Auto repay\
                                                        `312`: Auto offset\
                                                        `318`: Convert in\
                                                        `319`: Convert out\
                                                        `320`: Simple buy\
                                                        `321`: Simple sell\
                                                        `324`: Move
                                                        position buy\
                                                        `325`: Move
                                                        position sell\
                                                        `326`: Move
                                                        position open long\
                                                        `327`: Move
                                                        position open
                                                        short\
                                                        `328`: Move
                                                        position close
                                                        long\
                                                        `329`: Move
                                                        position close
                                                        short\
                                                        `332`: Margin
                                                        transfer in
                                                        isolated margin
                                                        position\
                                                        `333`: Margin
                                                        transfer out
                                                        isolated margin
                                                        position\
                                                        `334`: Margin loss
                                                        when closing
                                                        isolated margin
                                                        position\
                                                        `355`: Settlement
                                                        PnL\
                                                        `376`:
                                                        Collateralized
                                                        borrowing auto
                                                        conversion buy\
                                                        `377`:
                                                        Collateralized
                                                        borrowing auto
                                                        conversion sell\
                                                        `381`: Auto lend
                                                        interest transfer
                                                        in\
                                                        `372`: Bot airdrop
                                                        (transfer in)\
                                                        `373`: Bot airdrop
                                                        (transfer out)\
                                                        `374`: Bot airdrop
                                                        reclaim (transfer
                                                        in)\
                                                        `375`: Bot airdrop
                                                        reclaim (transfer
                                                        out)\
                                                        `381`: Auto earn
                                                        (auto lend)

  after             String            No                Pagination of data
                                                        to return records
                                                        earlier than the
                                                        requested bill ID.

  before            String            No                Pagination of data
                                                        to return records
                                                        newer than the
                                                        requested bill ID.

  begin             String            No                Filter with a begin
                                                        timestamp `ts`.
                                                        Unix timestamp
                                                        format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  end               String            No                Filter with an end
                                                        timestamp `ts`.
                                                        Unix timestamp
                                                        format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  limit             String            No                Number of results
                                                        per request. The
                                                        maximum is `100`.
                                                        The default is
                                                        `100`.
  -------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "bal": "8694.2179403378290202",
        "balChg": "0.0219338232210000",
        "billId": "623950854533513219",
        "ccy": "USDT",
        "clOrdId": "",
        "earnAmt": "",
        "earnApr": "",
        "execType": "T",
        "fee": "-0.000021955779",
        "fillFwdPx": "",
        "fillIdxPx": "27104.1",
        "fillMarkPx": "",
        "fillMarkVol": "",
        "fillPxUsd": "",
        "fillPxVol": "",
        "fillTime": "1695033476166",
        "from": "",
        "instId": "BTC-USDT",
        "instType": "SPOT",
        "interest": "0",
        "mgnMode": "isolated",
        "notes": "",
        "ordId": "623950854525124608",
        "pnl": "0",
        "posBal": "0",
        "posBalChg": "0",
        "px": "27105.9",
        "subType": "1",
        "sz": "0.021955779",
        "tag": "",
        "to": "",
        "tradeId": "586760148",
        "ts": "1695033476167",
        "type": "2"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-bills-details-last-7-days-response-parameters}

  ----------------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- ----------------------------
  instType                String                  Instrument type

  billId                  String                  Bill ID

  type                    String                  Bill type

  subType                 String                  Bill subtype

  ts                      String                  The time when the balance
                                                  complete update, Unix
                                                  timestamp format in
                                                  milliseconds,
                                                  e.g.`1597026383085`

  balChg                  String                  Change in balance amount at
                                                  the account level

  posBalChg               String                  Change in balance amount at
                                                  the position level

  bal                     String                  Balance at the account level

  posBal                  String                  Balance at the position
                                                  level

  sz                      String                  Quantity\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  it is fill quantity or
                                                  position quantity, the unit
                                                  is contract. The value is
                                                  always positive.\
                                                  For other scenarios. the
                                                  unit is account balance
                                                  currency(`ccy`).

  px                      String                  Price which related to
                                                  subType\

                                                  Trade filled price for

                                                  `1`: Buy `2`: Sell `3`: Open
                                                  long `4`: Open short `5`:
                                                  Close long `6`: Close short
                                                  `204`: block trade buy
                                                  `205`: block trade sell
                                                  `206`: block trade open long
                                                  `207`: block trade open
                                                  short `208`: block trade
                                                  close long `209`: block
                                                  trade close short `114`:
                                                  Forced repayment buy `115`:
                                                  Forced repayment sell\

                                                  Liquidation Price for

                                                  `100`: Partial liquidation
                                                  close long `101`: Partial
                                                  liquidation close short
                                                  `102`: Partial liquidation
                                                  buy `103`: Partial
                                                  liquidation sell `104`:
                                                  Liquidation long `105`:
                                                  Liquidation short `106`:
                                                  Liquidation buy `107`:
                                                  Liquidation sell `16`: Repay
                                                  forcibly `17`: Repay
                                                  interest by borrowing
                                                  forcibly `110`: Liquidation
                                                  transfer in `111`:
                                                  Liquidation transfer out\

                                                  Delivery price for

                                                  `112`: Delivery long `113`:
                                                  Delivery short\

                                                  Exercise price for

                                                  `170`: Exercised `171`:
                                                  Counterparty exercised
                                                  `172`: Expired OTM\

                                                  Mark price for

                                                  `173`: Funding fee expense
                                                  `174`: Funding fee income

  ccy                     String                  Account balance currency

  pnl                     String                  Profit and loss

  fee                     String                  Fee\
                                                  Negative number represents
                                                  the user transaction fee
                                                  charged by the platform.\
                                                  Positive number represents
                                                  rebate.\
                                                  [Trading fee rule](/en/fees)

  earnAmt                 String                  Auto earn amount\
                                                  Only applicable when type is
                                                  381

  earnApr                 String                  Auto earn APR\
                                                  Only applicable when type is
                                                  381

  mgnMode                 String                  Margin mode\
                                                  `isolated` `cross` `cash`\
                                                  When bills are not generated
                                                  by trading, the field
                                                  returns \"\"

  instId                  String                  Instrument ID, e.g.
                                                  `BTC-USDT`

  ordId                   String                  Order ID\
                                                  Return order ID when the
                                                  type is `2`/`5`/`9`\
                                                  Return \"\" when there is no
                                                  order.

  execType                String                  Liquidity taker or maker\
                                                  `T`: taker\
                                                  `M`: maker

  from                    String                  The remitting account\
                                                  `6`: Funding account\
                                                  `18`: Trading account\
                                                  Only applicable to
                                                  `transfer`. When bill type
                                                  is not `transfer`, the field
                                                  returns \"\".

  to                      String                  The beneficiary account\
                                                  `6`: Funding account\
                                                  `18`: Trading account\
                                                  Only applicable to
                                                  `transfer`. When bill type
                                                  is not `transfer`, the field
                                                  returns \"\".

  notes                   String                  Notes

  interest                String                  Interest

  tag                     String                  Order tag

  fillTime                String                  Last filled time

  tradeId                 String                  Last traded ID

  clOrdId                 String                  Client Order ID as assigned
                                                  by the client\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all numbers,
                                                  or all letters of up to 32
                                                  characters.

  fillIdxPx               String                  Index price at the moment of
                                                  trade execution\
                                                  For cross currency spot
                                                  pairs, it returns
                                                  baseCcy-USDT index price.
                                                  For example, for LTC-ETH,
                                                  this field returns the index
                                                  price of LTC-USDT.

  fillMarkPx              String                  Mark price when filled\
                                                  Applicable to
                                                  FUTURES/SWAP/OPTIONS, return
                                                  \"\" for other instrument
                                                  types

  fillPxVol               String                  Implied volatility when
                                                  filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillPxUsd               String                  Options price when filled,
                                                  in the unit of USD\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillMarkVol             String                  Mark volatility when filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillFwdPx               String                  Forward price when filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types
  ----------------------------------------------------------------------------

**Funding Fee expense (subType = 173)**\
You may refer to \"pnl\" for the fee payment

### Get bills details (last 3 months) {#trading-account-rest-api-get-bills-details-last-3-months}

Retrieve the account's bills. The bill refers to all transaction records
that result in changing the balance of an account. Pagination is
supported, and the response is sorted with most recent first. This
endpoint can retrieve data from the last 3 months.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-bills-details-last-3-months-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-bills-details-last-3-months-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-bills-details-last-3-months-permission-read}

#### HTTP Request {#trading-account-rest-api-get-bills-details-last-3-months-http-request}

`GET /api/v5/account/bills-archive`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/bills-archive

GET /api/v5/account/bills-archive?instType=MARGIN
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get bills details (last 3 months)
result = accountAPI.get_account_bills_archive()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-bills-details-last-3-months-request-parameters}

  -------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -------------------
  instType          String            No                Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`

  ccy               String            No                Bill currency

  mgnMode           String            No                Margin mode\
                                                        `isolated`\
                                                        `cross`

  ctType            String            No                Contract type\
                                                        `linear`\
                                                        `inverse`\
                                                        Only applicable to
                                                        `FUTURES`/`SWAP`

  type              String            No                Bill type\
                                                        `1`: Transfer\
                                                        `2`: Trade\
                                                        `3`: Delivery\
                                                        `4`: Forced
                                                        repayment\
                                                        `5`: Liquidation\
                                                        `6`: Margin
                                                        transfer\
                                                        `7`: Interest
                                                        deduction\
                                                        `8`: Funding fee\
                                                        `9`: ADL\
                                                        `10`: Clawback\
                                                        `11`: System token
                                                        conversion\
                                                        `12`: Strategy
                                                        transfer\
                                                        `13`: DDH\
                                                        `14`: Block trade\
                                                        `15`: Quick Margin\
                                                        `16`: Borrowing\
                                                        `22`: Repay\
                                                        `24`: Spread
                                                        trading\
                                                        `26`: Structured
                                                        products\
                                                        `27`: Convert\
                                                        `28`: Easy convert\
                                                        `29`: One-click
                                                        repay\
                                                        `30`: Simple trade\
                                                        `32`: Move
                                                        position\
                                                        `33`: Loans\
                                                        `34`: Settlement\
                                                        `250`: Copy trader
                                                        profit sharing
                                                        expenses\
                                                        `251`: Copy trader
                                                        profit sharing
                                                        refund

  subType           String            No                Bill subtype\
                                                        `1`: Buy\
                                                        `2`: Sell\
                                                        `3`: Open long\
                                                        `4`: Open short\
                                                        `5`: Close long\
                                                        `6`: Close short\
                                                        `9`: Interest
                                                        deduction for
                                                        Market loans\
                                                        `11`: Transfer in\
                                                        `12`: Transfer out\
                                                        `14`: Interest
                                                        deduction for VIP
                                                        loans\
                                                        `160`: Manual
                                                        margin increase\
                                                        `161`: Manual
                                                        margin decrease\
                                                        `162`: Auto margin
                                                        increase\
                                                        `114`: Forced
                                                        repayment buy\
                                                        `115`: Forced
                                                        repayment sell\
                                                        `118`: System token
                                                        conversion transfer
                                                        in\
                                                        `119`: System token
                                                        conversion transfer
                                                        out\
                                                        `100`: Partial
                                                        liquidation close
                                                        long\
                                                        `101`: Partial
                                                        liquidation close
                                                        short\
                                                        `102`: Partial
                                                        liquidation buy\
                                                        `103`: Partial
                                                        liquidation sell\
                                                        `104`: Liquidation
                                                        long\
                                                        `105`: Liquidation
                                                        short\
                                                        `106`: Liquidation
                                                        buy\
                                                        `107`: Liquidation
                                                        sell\
                                                        `108`: Clawback\
                                                        `110`: Liquidation
                                                        transfer in\
                                                        `111`: Liquidation
                                                        transfer out\
                                                        `125`: ADL close
                                                        long\
                                                        `126`: ADL close
                                                        short\
                                                        `127`: ADL buy\
                                                        `128`: ADL sell\
                                                        `131`: ddh buy\
                                                        `132`: ddh sell\
                                                        `170`:
                                                        Exercised(ITM buy
                                                        side)\
                                                        `171`: Counterparty
                                                        exercised(ITM sell
                                                        side)\
                                                        `172`:
                                                        Expired(Non-ITM buy
                                                        and sell side)\
                                                        `112`: Delivery
                                                        long (applicable to
                                                        `FUTURES`
                                                        expiration and
                                                        `SWAP` delisting)\
                                                        `113`: Delivery
                                                        short (applicable
                                                        to `FUTURES`
                                                        expiration and
                                                        `SWAP` delisting)\
                                                        `117`:
                                                        Delivery/Exercise
                                                        clawback\
                                                        `173`: Funding fee
                                                        expense\
                                                        `174`: Funding fee
                                                        income\
                                                        `200`:System
                                                        transfer in\
                                                        `201`: Manually
                                                        transfer in\
                                                        `202`: System
                                                        transfer out\
                                                        `203`: Manually
                                                        transfer out\
                                                        `204`: block trade
                                                        buy\
                                                        `205`: block trade
                                                        sell\
                                                        `206`: block trade
                                                        open long\
                                                        `207`: block trade
                                                        open short\
                                                        `208`: block trade
                                                        close long\
                                                        `209`: block trade
                                                        close short\
                                                        `210`: Manual
                                                        Borrowing of quick
                                                        margin\
                                                        `211`: Manual
                                                        Repayment of quick
                                                        margin\
                                                        `212`: Auto borrow
                                                        of quick margin\
                                                        `213`: Auto repay
                                                        of quick margin\
                                                        `220`: Transfer in
                                                        when using USDT to
                                                        buy OPTION\
                                                        `221`: Transfer out
                                                        when using USDT to
                                                        buy OPTION\
                                                        `16`: Repay
                                                        forcibly\
                                                        `17`: Repay
                                                        interest by
                                                        borrowing forcibly\
                                                        `224`: Repayment
                                                        transfer in\
                                                        `225`: Repayment
                                                        transfer out\
                                                        `236`: Easy convert
                                                        in\
                                                        `237`: Easy convert
                                                        out\
                                                        `250`: Profit
                                                        sharing expenses\
                                                        `251`: Profit
                                                        sharing refund\
                                                        `280`: SPOT profit
                                                        sharing expenses\
                                                        `281`: SPOT profit
                                                        sharing refund\
                                                        `282`: Spot profit
                                                        share income\
                                                        `283`: Asset
                                                        transfer for spot
                                                        copy trading\
                                                        `270`: Spread
                                                        trading buy\
                                                        `271`: Spread
                                                        trading sell\
                                                        `272`: Spread
                                                        trading open long\
                                                        `273`: Spread
                                                        trading open short\
                                                        `274`: Spread
                                                        trading close long\
                                                        `275`: Spread
                                                        trading close
                                                        short\
                                                        `280`: SPOT profit
                                                        sharing expenses\
                                                        `281`: SPOT profit
                                                        sharing refund\
                                                        `284`: Copy trade
                                                        automatic transfer
                                                        in\
                                                        `285`: Copy trade
                                                        manual transfer in\
                                                        `286`: Copy trade
                                                        automatic transfer
                                                        out\
                                                        `287`: Copy trade
                                                        manual transfer
                                                        out\
                                                        `290`: Crypto dust
                                                        auto-transfer out\
                                                        ~~`293`: Fixed loan
                                                        interest
                                                        deduction~~\
                                                        ~~`294`: Fixed loan
                                                        interest refund~~\
                                                        ~~`295`: Fixed loan
                                                        overdue penalty~~\
                                                        `296`: From
                                                        structured order
                                                        placements\
                                                        `297`: To
                                                        structured order
                                                        placements\
                                                        `298`: From
                                                        structured
                                                        settlements\
                                                        `299`: To
                                                        structured
                                                        settlements\
                                                        `306`: Manual
                                                        borrow\
                                                        `307`: Auto borrow\
                                                        `308`: Manual
                                                        repay\
                                                        `309`: Auto repay\
                                                        `312`: Auto offset\
                                                        `318`: Convert in\
                                                        `319`: Convert out\
                                                        `320`: Simple buy\
                                                        `321`: Simple sell\
                                                        `324`: Move
                                                        position buy\
                                                        `325`: Move
                                                        position sell\
                                                        `326`: Move
                                                        position open long\
                                                        `327`: Move
                                                        position open
                                                        short\
                                                        `328`: Move
                                                        position close
                                                        long\
                                                        `329`: Move
                                                        position close
                                                        short\
                                                        `332`: Margin
                                                        transfer in
                                                        isolated margin
                                                        position\
                                                        `333`: Margin
                                                        transfer out
                                                        isolated margin
                                                        position\
                                                        `334`: Margin loss
                                                        when closing
                                                        isolated margin
                                                        position\
                                                        `355`: Settlement
                                                        PnL\
                                                        `376`:
                                                        Collateralized
                                                        borrowing auto
                                                        conversion buy\
                                                        `377`:
                                                        Collateralized
                                                        borrowing auto
                                                        conversion sell\
                                                        `381`: Auto lend
                                                        interest transfer
                                                        in\
                                                        `372`: Bot airdrop
                                                        (transfer in)\
                                                        `373`: Bot airdrop
                                                        (transfer out)\
                                                        `374`: Bot airdrop
                                                        reclaim (transfer
                                                        in)\
                                                        `375`: Bot airdrop
                                                        reclaim (transfer
                                                        out)\
                                                        `381`: Auto earn
                                                        (auto lend)

  after             String            No                Pagination of data
                                                        to return records
                                                        earlier than the
                                                        requested bill ID.

  before            String            No                Pagination of data
                                                        to return records
                                                        newer than the
                                                        requested bill ID.

  begin             String            No                Filter with a begin
                                                        timestamp `ts`.
                                                        Unix timestamp
                                                        format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  end               String            No                Filter with an end
                                                        timestamp `ts`.
                                                        Unix timestamp
                                                        format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  limit             String            No                Number of results
                                                        per request. The
                                                        maximum is `100`.
                                                        The default is
                                                        `100`.
  -------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "bal": "8694.2179403378290202",
        "balChg": "0.0219338232210000",
        "billId": "623950854533513219",
        "ccy": "USDT",
        "clOrdId": "",
        "earnAmt": "",
        "earnApr": "",
        "execType": "T",
        "fee": "-0.000021955779",
        "fillFwdPx": "",
        "fillIdxPx": "27104.1",
        "fillMarkPx": "",
        "fillMarkVol": "",
        "fillPxUsd": "",
        "fillPxVol": "",
        "fillTime": "1695033476166",
        "from": "",
        "instId": "BTC-USDT",
        "instType": "SPOT",
        "interest": "0",
        "mgnMode": "isolated",
        "notes": "",
        "ordId": "623950854525124608",
        "pnl": "0",
        "posBal": "0",
        "posBalChg": "0",
        "px": "27105.9",
        "subType": "1",
        "sz": "0.021955779",
        "tag": "",
        "to": "",
        "tradeId": "586760148",
        "ts": "1695033476167",
        "type": "2"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-bills-details-last-3-months-response-parameters}

  ----------------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- ----------------------------
  instType                String                  Instrument type

  billId                  String                  Bill ID

  type                    String                  Bill type

  subType                 String                  Bill subtype

  ts                      String                  The time when the balance
                                                  complete update, Unix
                                                  timestamp format in
                                                  milliseconds,
                                                  e.g.`1597026383085`

  balChg                  String                  Change in balance amount at
                                                  the account level

  posBalChg               String                  Change in balance amount at
                                                  the position level

  bal                     String                  Balance at the account level

  posBal                  String                  Balance at the position
                                                  level

  sz                      String                  Quantity\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  it is fill quantity or
                                                  position quantity, the unit
                                                  is contract. The value is
                                                  always positive.\
                                                  For other scenarios. the
                                                  unit is account balance
                                                  currency(`ccy`).

  px                      String                  Price which related to
                                                  subType\

                                                  Trade filled price for

                                                  `1`: Buy `2`: Sell `3`: Open
                                                  long `4`: Open short `5`:
                                                  Close long `6`: Close short
                                                  `204`: block trade buy
                                                  `205`: block trade sell
                                                  `206`: block trade open long
                                                  `207`: block trade open
                                                  short `208`: block trade
                                                  close long `209`: block
                                                  trade close short `114`:
                                                  Forced repayment buy `115`:
                                                  Forced repayment sell\

                                                  Liquidation Price for

                                                  `100`: Partial liquidation
                                                  close long `101`: Partial
                                                  liquidation close short
                                                  `102`: Partial liquidation
                                                  buy `103`: Partial
                                                  liquidation sell `104`:
                                                  Liquidation long `105`:
                                                  Liquidation short `106`:
                                                  Liquidation buy `107`:
                                                  Liquidation sell `16`: Repay
                                                  forcibly `17`: Repay
                                                  interest by borrowing
                                                  forcibly `110`: Liquidation
                                                  transfer in `111`:
                                                  Liquidation transfer out\

                                                  Delivery price for

                                                  `112`: Delivery long `113`:
                                                  Delivery short\

                                                  Exercise price for

                                                  `170`: Exercised `171`:
                                                  Counterparty exercised
                                                  `172`: Expired OTM\

                                                  Mark price for

                                                  `173`: Funding fee expense
                                                  `174`: Funding fee income

  ccy                     String                  Account balance currency

  pnl                     String                  Profit and loss

  fee                     String                  Fee\
                                                  Negative number represents
                                                  the user transaction fee
                                                  charged by the platform.\
                                                  Positive number represents
                                                  rebate.\
                                                  [Trading fee rule](/en/fees)

  earnAmt                 String                  Auto earn amount\
                                                  Only applicable when type is
                                                  381

  earnApr                 String                  Auto earn APR\
                                                  Only applicable when type is
                                                  381

  mgnMode                 String                  Margin mode\
                                                  `isolated` `cross` `cash`\
                                                  When bills are not generated
                                                  by trading, the field
                                                  returns \"\"

  instId                  String                  Instrument ID, e.g.
                                                  `BTC-USDT`

  ordId                   String                  Order ID\
                                                  Return order ID when the
                                                  type is `2`/`5`/`9`\
                                                  Return \"\" when there is no
                                                  order.

  execType                String                  Liquidity taker or maker\
                                                  `T`: taker `M`: maker

  from                    String                  The remitting account\
                                                  `6`: Funding account\
                                                  `18`: Trading account\
                                                  Only applicable to
                                                  `transfer`. When bill type
                                                  is not `transfer`, the field
                                                  returns \"\".

  to                      String                  The beneficiary account\
                                                  `6`: Funding account\
                                                  `18`: Trading account\
                                                  Only applicable to
                                                  `transfer`. When bill type
                                                  is not `transfer`, the field
                                                  returns \"\".

  notes                   String                  Notes

  interest                String                  Interest

  tag                     String                  Order tag

  fillTime                String                  Last filled time

  tradeId                 String                  Last traded ID

  clOrdId                 String                  Client Order ID as assigned
                                                  by the client\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all numbers,
                                                  or all letters of up to 32
                                                  characters.

  fillIdxPx               String                  Index price at the moment of
                                                  trade execution\
                                                  For cross currency spot
                                                  pairs, it returns
                                                  baseCcy-USDT index price.
                                                  For example, for LTC-ETH,
                                                  this field returns the index
                                                  price of LTC-USDT.

  fillMarkPx              String                  Mark price when filled\
                                                  Applicable to
                                                  FUTURES/SWAP/OPTIONS, return
                                                  \"\" for other instrument
                                                  types

  fillPxVol               String                  Implied volatility when
                                                  filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillPxUsd               String                  Options price when filled,
                                                  in the unit of USD\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillMarkVol             String                  Mark volatility when filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types

  fillFwdPx               String                  Forward price when filled\
                                                  Only applicable to options;
                                                  return \"\" for other
                                                  instrument types
  ----------------------------------------------------------------------------

**Funding Fee expense (subType = 173)**\
You may refer to \"pnl\" for the fee payment

### Apply bills details (since 2021) {#trading-account-rest-api-apply-bills-details-since-2021}

Apply for bill data since 1 February, 2021 except for the current
quarter.

#### Rate Limit：12 requests per day {#trading-account-rest-api-apply-bills-details-since-2021-rate-limit-12-requests-per-day}

#### Rate limit rule: User ID {#trading-account-rest-api-apply-bills-details-since-2021-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-apply-bills-details-since-2021-permission-read}

#### HTTP Request {#trading-account-rest-api-apply-bills-details-since-2021-http-request}

`POST /api/v5/account/bills-history-archive`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/bills-history-archive
body
{
    "year":"2023",
    "quarter":"Q1"
}
```
:::

#### Request Parameters {#trading-account-rest-api-apply-bills-details-since-2021-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ------------------------------------------------
  year        String   Yes        4 digits year
  quarter     String   Yes        Quarter, valid value is `Q1`, `Q2`, `Q3`, `Q4`

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "result": "true",
            "ts": "1646892328000"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-apply-bills-details-since-2021-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  result                  String                  Whether there is
                                                  already a download link
                                                  for this section\
                                                  `true`: Existed, can
                                                  check from \"Get bills
                                                  details (since
                                                  2021)\".\
                                                  `false`: Does not exist
                                                  and is generating, can
                                                  check the download link
                                                  after 2 hours\
                                                  The data of file is in
                                                  reverse chronological
                                                  order using `billId`.

  ts                      String                  The first request time
                                                  when the server
                                                  receives. Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`
  -----------------------------------------------------------------------

The rule introduction, only applicable to the file generated after 11
October, 2024\
1. Taking 2024 Q2 as an example. The date range are \[2024-07-01,
2024-10-01). The begin date is included, The end date is excluded.\
2. The data of file is in reverse chronological order using \`billId\`

Check the file link from the \"Get bills details (since 2021)\" endpoint
in 2 hours to allow for data generation.\
During peak demand, data generation may take longer. If the file link is
still unavailable after 3 hours, reach out to customer support for
assistance.

It is only applicable to the data from the unified account.

### Get bills details (since 2021) {#trading-account-rest-api-get-bills-details-since-2021}

Apply for bill data since 1 February, 2021 except for the current
quarter.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-bills-details-since-2021-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-bills-details-since-2021-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-bills-details-since-2021-permission-read}

#### HTTP Request {#trading-account-rest-api-get-bills-details-since-2021-http-request}

`GET /api/v5/account/bills-history-archive`

> Response Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/bills-history-archive?year=2023&quarter=Q4
```
:::

#### Request Parameters {#trading-account-rest-api-get-bills-details-since-2021-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ------------------------------------------------
  year        String   Yes        4 digits year
  quarter     String   Yes        Quarter, valid value is `Q1`, `Q2`, `Q3`, `Q4`

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "fileHref": "http://xxx",
            "state": "finished",
            "ts": "1646892328000"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-bills-details-since-2021-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  fileHref                String                  Download file link.\
                                                  The expiration of every
                                                  link is 5 and a half
                                                  hours. If you already
                                                  apply the files for the
                                                  same quarter, then it
                                                  don't need to apply
                                                  again within 30 days.

  ts                      String                  The first request time
                                                  when the server
                                                  receives. Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  state                   String                  Download link status\
                                                  \"finished\"
                                                  \"ongoing\" \"failed\":
                                                  Failed, please apply
                                                  again
  -----------------------------------------------------------------------

It is only applicable to the data from the unified account.

#### Field descriptions in the decompressed CSV file {#trading-account-rest-api-get-bills-details-since-2021-field-descriptions-in-the-decompressed-csv-file}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instType                String                  Instrument type

  billId                  String                  Bill ID

  subType                 String                  Bill subtype

  ts                      String                  The time when the
                                                  balance complete
                                                  update, Unix timestamp
                                                  format in milliseconds,
                                                  e.g.`1597026383085`

  balChg                  String                  Change in balance
                                                  amount at the account
                                                  level

  posBalChg               String                  Change in balance
                                                  amount at the position
                                                  level

  bal                     String                  Balance at the account
                                                  level

  posBal                  String                  Balance at the position
                                                  level

  sz                      String                  Quantity

  px                      String                  Price which related to
                                                  subType\

                                                  Trade filled price for

                                                  `1`: Buy `2`: Sell `3`:
                                                  Open long `4`: Open
                                                  short `5`: Close long
                                                  `6`: Close short `204`:
                                                  block trade buy `205`:
                                                  block trade sell `206`:
                                                  block trade open long
                                                  `207`: block trade open
                                                  short `208`: block
                                                  trade close long `209`:
                                                  block trade close short
                                                  `114`: Forced repayment
                                                  buy `115`: Forced
                                                  repayment sell\

                                                  Liquidation Price for

                                                  `100`: Partial
                                                  liquidation close long
                                                  `101`: Partial
                                                  liquidation close short
                                                  `102`: Partial
                                                  liquidation buy `103`:
                                                  Partial liquidation
                                                  sell `104`: Liquidation
                                                  long `105`: Liquidation
                                                  short `106`:
                                                  Liquidation buy `107`:
                                                  Liquidation sell `16`:
                                                  Repay forcibly `17`:
                                                  Repay interest by
                                                  borrowing forcibly
                                                  `110`: Liquidation
                                                  transfer in `111`:
                                                  Liquidation transfer
                                                  out\

                                                  Delivery price for

                                                  `112`: Delivery long
                                                  `113`: Delivery short\

                                                  Exercise price for

                                                  `170`: Exercised `171`:
                                                  Counterparty exercised
                                                  `172`: Expired OTM\

                                                  Mark price for

                                                  `173`: Funding fee
                                                  expense `174`: Funding
                                                  fee income

  ccy                     String                  Account balance
                                                  currency

  pnl                     String                  Profit and loss

  fee                     String                  Fee\
                                                  Negative number
                                                  represents the user
                                                  transaction fee charged
                                                  by the platform.\
                                                  Positive number
                                                  represents rebate.\
                                                  [Trading fee
                                                  rule](/en/fees)

  mgnMode                 String                  Margin mode\
                                                  `isolated` `cross`
                                                  `cash`\
                                                  When bills are not
                                                  generated by trading,
                                                  the field returns \"\"

  instId                  String                  Instrument ID, e.g.
                                                  `BTC-USDT`

  ordId                   String                  Order ID\
                                                  Return order ID when
                                                  the type is
                                                  `2`/`5`/`9`\
                                                  Return \"\" when there
                                                  is no order.

  execType                String                  Liquidity taker or
                                                  maker\
                                                  `T`: taker `M`: maker

  interest                String                  Interest

  tag                     String                  Order tag

  fillTime                String                  Last filled time

  tradeId                 String                  Last traded ID

  clOrdId                 String                  Client Order ID as
                                                  assigned by the client\
                                                  A combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.

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

  fillMarkPx              String                  Mark price when filled\
                                                  Applicable to
                                                  FUTURES/SWAP/OPTIONS,
                                                  return \"\" for other
                                                  instrument types

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
  -----------------------------------------------------------------------

### Get account configuration {#trading-account-rest-api-get-account-configuration}

Retrieve current account configuration.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-account-configuration-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-account-configuration-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-account-configuration-permission-read}

#### HTTP Request {#trading-account-rest-api-get-account-configuration-http-request}

`GET /api/v5/account/config`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/config
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve current account configuration
result = accountAPI.get_account_config()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-account-configuration-request-parameters}

none

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLv": "2",
            "acctStpMode": "cancel_maker",
            "autoLoan": false,
            "ctIsoMode": "automatic",
            "enableSpotBorrow": false,
            "greeksType": "PA",
            "feeType": "0",
            "ip": "",
            "type": "0",
            "kycLv": "3",
            "label": "v5 test",
            "level": "Lv1",
            "levelTmp": "",
            "liquidationGear": "-1",
            "mainUid": "44705892343619584",
            "mgnIsoMode": "automatic",
            "opAuth": "1",
            "perm": "read_only,withdraw,trade",
            "posMode": "long_short_mode",
            "roleType": "0",
            "spotBorrowAutoRepay": false,
            "spotOffsetType": "",
            "spotRoleType": "0",
            "spotTraderInsts": [],
            "traderInsts": [],
            "uid": "44705892343619584",
            "settleCcy": "USDC",
            "settleCcyList": ["USD", "USDC", "USDG"]
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-account-configuration-response-parameters}

  --------------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- --------------------------------
  uid                     String                  Account ID of current request.

  mainUid                 String                  Main Account ID of current
                                                  request.\
                                                  The current request account is
                                                  main account if uid = mainUid.\
                                                  The current request account is
                                                  sub-account if uid != mainUid.

  acctLv                  String                  Account mode\
                                                  `1`: Spot mode\
                                                  `2`: Futures mode\
                                                  `3`: Multi-currency margin\
                                                  `4`: Portfolio margin

  acctStpMode             String                  Account self-trade prevention
                                                  mode\
                                                  `cancel_maker`\
                                                  `cancel_taker`\
                                                  `cancel_both`\
                                                  The default value is
                                                  `cancel_maker`. Users can log in
                                                  to the webpage through the
                                                  master account to modify this
                                                  configuration

  posMode                 String                  Position mode\
                                                  `long_short_mode`: long/short,
                                                  only applicable to
                                                  `FUTURES`/`SWAP`\
                                                  `net_mode`: net

  autoLoan                Boolean                 Whether to borrow coins
                                                  automatically\
                                                  `true`: borrow coins
                                                  automatically\
                                                  `false`: not borrow coins
                                                  automatically

  greeksType              String                  Current display type of Greeks\
                                                  `PA`: Greeks in coins\
                                                  `BS`: Black-Scholes Greeks in
                                                  dollars

  feeType                 String                  Fee type\
                                                  `0`: fee is charged in the
                                                  currency you receive from the
                                                  trade\
                                                  `1`: fee is always charged in
                                                  the quote currency of the
                                                  trading pair

  level                   String                  The user level of the current
                                                  real trading volume on the
                                                  platform, e.g `Lv1`, which means
                                                  regular user level.

  levelTmp                String                  Temporary experience user level
                                                  of special users, e.g `Lv1`

  ctIsoMode               String                  Contract isolated margin trading
                                                  settings\
                                                  `automatic`: Auto transfers\
                                                  `autonomy`: Manual transfers

  mgnIsoMode              String                  Margin isolated margin trading
                                                  settings\
                                                  `auto_transfers_ccy`: New auto
                                                  transfers, enabling both base
                                                  and quote currency as the margin
                                                  for isolated margin trading\
                                                  `automatic`: Auto transfers\
                                                  `quick_margin`: Quick Margin
                                                  Mode (For new accounts,
                                                  including subaccounts, some
                                                  defaults will be `automatic`,
                                                  and others will be
                                                  `quick_margin`)

  spotOffsetType          String                  ~~Risk offset type\
                                                  `1`: Spot-Derivatives(USDT) to
                                                  be offsetted\
                                                  `2`: Spot-Derivatives(Coin) to
                                                  be offsetted\
                                                  `3`: Only derivatives to be
                                                  offsetted\
                                                  Only applicable to
                                                  `Portfolio margin`~~\
                                                  (Deprecated)

  roleType                String                  Role type\
                                                  `0`: General user\
                                                  `1`: Leading trader\
                                                  `2`: Copy trader

  traderInsts             Array of strings        Leading trade instruments, only
                                                  applicable to Leading trader

  spotRoleType            String                  SPOT copy trading role type.\
                                                  `0`: General user；`1`: Leading
                                                  trader；`2`: Copy trader

  spotTraderInsts         Array of strings        Spot lead trading instruments,
                                                  only applicable to lead trader

  opAuth                  String                  Whether the optional trading was
                                                  activated\
                                                  `0`: not activate\
                                                  `1`: activated

  kycLv                   String                  Main account KYC level\
                                                  `0`: No verification\
                                                  `1`: level 1 completed\
                                                  `2`: level 2 completed\
                                                  `3`: level 3 completed\
                                                  If the request originates from a
                                                  subaccount, kycLv is the KYC
                                                  level of the main account.\
                                                  If the request originates from
                                                  the main account, kycLv is the
                                                  KYC level of the current
                                                  account.

  label                   String                  API key note of current request
                                                  API key. No more than 50 letters
                                                  (case sensitive) or numbers,
                                                  which can be pure letters or
                                                  pure numbers.

  ip                      String                  IP addresses that linked with
                                                  current API key, separate with
                                                  commas if more than one, e.g.
                                                  `117.37.203.58,117.37.203.57`.
                                                  It is an empty string \"\" if
                                                  there is no IP bonded.

  perm                    String                  The permission of the current
                                                  requesting API key or Access
                                                  token\
                                                  `read_only`: Read\
                                                  `trade`: Trade\
                                                  `withdraw`: Withdraw

  liquidationGear         String                  The maintenance margin ratio
                                                  level of liquidation alert\
                                                  `3` and `-1` means that you will
                                                  get hourly liquidation alerts on
                                                  app and channel \"Position risk
                                                  warning\" when your margin level
                                                  drops to or below 300%. `-1` is
                                                  the initial value which has the
                                                  same effect as `-3`\
                                                  `0` means that there is not
                                                  alert

  enableSpotBorrow        Boolean                 Whether borrow is allowed or not
                                                  in `Spot mode`\
                                                  `true`: Enabled\
                                                  `false`: Disabled

  spotBorrowAutoRepay     Boolean                 Whether auto-repay is allowed or
                                                  not in `Spot mode`\
                                                  `true`: Enabled\
                                                  `false`: Disabled

  type                    String                  Account type\
                                                  `0`: Main account\
                                                  `1`: Standard sub-account\
                                                  `2`: Managed trading
                                                  sub-account\
                                                  `5`: Custody trading
                                                  sub-account - Copper\
                                                  `9`: Managed trading
                                                  sub-account - Copper\
                                                  `12`: Custody trading
                                                  sub-account - Komainu

  settleCcy               String                  Current account\'s USD-margined
                                                  contract settle currency

  settleCcyList           String                  Current account\'s USD-margined
                                                  contract settle currency list,
                                                  like \[\"USD\", \"USDC\",
                                                  \"USDG\"\].
  --------------------------------------------------------------------------------

### Set position mode {#trading-account-rest-api-set-position-mode}

Futures mode and Multi-currency mode: `FUTURES` and `SWAP` support both
`long/short` mode and `net` mode. In `net` mode, users can only have
positions in one direction; In `long/short` mode, users can hold
positions in long and short directions.\
Portfolio margin mode: `FUTURES` and `SWAP` only support `net` mode

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-position-mode-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-position-mode-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-position-mode-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-position-mode-http-request}

`POST /api/v5/account/set-position-mode`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-position-mode
body
{
    "posMode":"long_short_mode"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Set position mode
result = accountAPI.set_position_mode(
    posMode="long_short_mode"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-set-position-mode-request-parameters}

  --------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- --------------------
  posMode           String            Yes               Position mode\
                                                        `long_short_mode`:
                                                        long/short, only
                                                        applicable to
                                                        `FUTURES`/`SWAP`\
                                                        `net_mode`: net

  --------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "posMode": "long_short_mode"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-position-mode-response-parameters}

  Parameter   Type     Description
  ----------- -------- ---------------
  posMode     String   Position mode

Portfolio margin account only supports net mode

### Set leverage {#trading-account-rest-api-set-leverage}

\
There are 10 different scenarios for leverage setting:\
\
1. Set leverage for `MARGIN` instruments under `isolated-margin` trade
mode at pairs level.\
2. Set leverage for `MARGIN` instruments under `cross-margin` trade mode
and Spot mode (enabled borrow) at currency level.\
3. Set leverage for `MARGIN` instruments under `cross-margin` trade mode
and Futures mode account mode at pairs level.\
4. Set leverage for `MARGIN` instruments under `cross-margin` trade mode
and Multi-currency margin at currency level.\
5. Set leverage for `MARGIN` instruments under `cross-margin` trade mode
and Portfolio margin at currency level.\
6. Set leverage for `FUTURES` instruments under `cross-margin` trade
mode at underlying level.\
7. Set leverage for `FUTURES` instruments under `isolated-margin` trade
mode and buy/sell position mode at contract level.\
8. Set leverage for `FUTURES` instruments under `isolated-margin` trade
mode and long/short position mode at contract and position side level.\
9. Set leverage for `SWAP` instruments under `cross-margin` trade at
contract level.\
10. Set leverage for `SWAP` instruments under `isolated-margin` trade
mode and buy/sell position mode at contract level.\
11. Set leverage for `SWAP` instruments under `isolated-margin` trade
mode and long/short position mode at contract and position side level.\
\

Note that the request parameter `posSide` is only required when margin
mode is isolated in long/short position mode for FUTURES/SWAP
instruments (see scenario 8 and 11 above).\
Please refer to the request examples on the right for each case.\

#### Rate limit: 20 requests per 2 seconds {#trading-account-rest-api-set-leverage-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-leverage-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-leverage-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-leverage-http-request}

`POST /api/v5/account/set-leverage`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# 1. Set leverage for `MARGIN` instruments under `isolated-margin` trade mode at pairs level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT",
    "lever":"5",
    "mgnMode":"isolated"
}

# 2. Set leverage for `MARGIN` instruments under `cross-margin` trade mode and Spot mode (enabled borrow) at currency level.
POST /api/v5/account/set-leverage
body
{
    "ccy":"BTC",
    "lever":"5",
    "mgnMode":"cross"
}

# 3. Set leverage for `MARGIN` instruments under `cross-margin` trade mode and Futures mode account mode at pairs level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT",
    "lever":"5",
    "mgnMode":"cross"
}

# 4. Set leverage for `MARGIN` instruments under `cross-margin` trade mode and Multi-currency margin at currency level.
POST /api/v5/account/set-leverage
body
{
    "ccy":"BTC",
    "lever":"5",
    "mgnMode":"cross"
}

# 5. Set leverage for `MARGIN` instruments under `cross-margin` trade mode and Portfolio margin at currency level.
POST /api/v5/account/set-leverage
body
{
    "ccy":"BTC",
    "lever":"5",
    "mgnMode":"cross"
}

# 6. Set leverage for `FUTURES` instruments under `cross-margin` trade mode at underlying level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-200802",
    "lever":"5",
    "mgnMode":"cross"
}

# 7. Set leverage for `FUTURES` instruments under `isolated-margin` trade mode and buy/sell order placement mode at contract level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-200802",
    "lever":"5",
    "mgnMode":"isolated"
}

# 8. Set leverage for `FUTURES` instruments under `isolated-margin` trade mode and long/short order placement mode at contract and position side level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-200802",
    "lever":"5",
    "posSide":"long",
    "mgnMode":"isolated"
}

# 9. Set leverage for `SWAP` instruments under `cross-margin` trade at contract level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-SWAP",
    "lever":"5",
    "mgnMode":"cross"
}

# 10. Set leverage for `SWAP` instruments under `isolated-margin` trade mode and buy/sell order placement mode at contract level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-SWAP",
    "lever":"5",
    "mgnMode":"isolated"
}

# 11. Set leverage for `SWAP` instruments under `isolated-margin` trade mode and long/short order placement mode at contract and position side level.
POST /api/v5/account/set-leverage
body
{
    "instId":"BTC-USDT-SWAP",
    "lever":"5",
    "posSide":"long",
    "mgnMode":"isolated"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Set leverage for MARGIN instruments under isolated-margin trade mode at pairs level.
result = accountAPI.set_leverage(
    instId="BTC-USDT",
    lever="5",
    mgnMode="isolated"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-set-leverage-request-parameters}

  ----------------------------------------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ----------------------------------------------------------
  instId            String            Conditional       Instrument ID\
                                                        Only applicable to `cross` `FUTURES` `SWAP` of
                                                        `Spot mode`/`Multi-currency margin`/`Portfolio margin`,
                                                        `cross` `MARGIN``FUTURES``SWAP` and `isolated` position.\
                                                        And required in applicable scenarios.

  ccy               String            Conditional       Currency used for margin, used for the leverage setting
                                                        for the currency in auto borrow.\
                                                        Only applicable to `cross` `MARGIN` of
                                                        `Spot mode`/`Multi-currency margin`/`Portfolio margin`.\
                                                        And required in applicable scenarios.

  lever             String            Yes               Leverage

  mgnMode           String            Yes               Margin mode\
                                                        `isolated` `cross`\
                                                        Can only be `cross` if `ccy` is passed.

  posSide           String            Conditional       Position side\
                                                        `long` `short`\
                                                        Only required when margin mode is `isolated` in
                                                        `long/short` mode for `FUTURES`/`SWAP`.
  ----------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "lever": "30",
      "mgnMode": "isolated",
      "instId": "BTC-USDT-SWAP",
      "posSide": "long"
    }
  ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-leverage-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  lever                   String                  Leverage

  mgnMode                 String                  Margin mode\
                                                  `cross` `isolated`

  instId                  String                  Instrument ID

  posSide                 String                  Position side
  -----------------------------------------------------------------------

When setting leverage for \`cross\` \`FUTURES\`/\`SWAP\` at the
underlying level, pass in any instId and mgnMode(\`cross\`).

Leverage cannot be adjusted for the cross positions of Expiry Futures
and Perpetual Futures under the portfolio margin account.

### Get maximum order quantity {#trading-account-rest-api-get-maximum-order-quantity}

The maximum quantity to buy or sell. It corresponds to the \"sz\" from
placement.

Under the Portfolio Margin account, the calculation of the maximum
buy/sell amount or open amount is not supported under the cross mode of
derivatives.

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-maximum-order-quantity-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-maximum-order-quantity-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-maximum-order-quantity-permission-read}

#### HTTP Request {#trading-account-rest-api-get-maximum-order-quantity-http-request}

`GET /api/v5/account/max-size`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/max-size?instId=BTC-USDT&tdMode=isolated
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get maximum buy/sell amount or open amount
result = accountAPI.get_max_order_size(
    instId="BTC-USDT",
    tdMode="isolated"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-maximum-order-quantity-request-parameters}

  -----------------------------------------------------------------------------
  **Parameter**     **Type**          Required          Description
  ----------------- ----------------- ----------------- -----------------------
  instId            String            Yes               Single instrument or
                                                        multiple instruments
                                                        (no more than 5) in the
                                                        smae instrument type
                                                        separated with comma,
                                                        e.g.
                                                        `BTC-USDT,ETH-USDT`

  tdMode            String            Yes               Trade mode\
                                                        `cross`\
                                                        `isolated`\
                                                        `cash`\
                                                        `spot_isolated`: only
                                                        applicable to
                                                        `Futures mode`.

  ccy               String            Conditional       Currency used for
                                                        margin\
                                                        Applicable to
                                                        `isolated` `MARGIN` and
                                                        `cross` `MARGIN` orders
                                                        in `Futures mode`.

  px                String            No                Price\
                                                        When the price is not
                                                        specified, it will be
                                                        calculated according to
                                                        the current limit price
                                                        for `FUTURES` and
                                                        `SWAP`, the last traded
                                                        price for other
                                                        instrument types.\
                                                        The parameter will be
                                                        ignored when multiple
                                                        instruments are
                                                        specified.

  leverage          String            No                Leverage for
                                                        instrument\
                                                        The default is current
                                                        leverage\
                                                        Only applicable to
                                                        `MARGIN/FUTURES/SWAP`

  tradeQuoteCcy     String            No                The quote currency used
                                                        for trading. Only
                                                        applicable to `SPOT`.\
                                                        The default value is
                                                        the quote currency of
                                                        the `instId`, for
                                                        example: for `BTC-USD`,
                                                        the default is `USD`.
  -----------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "ccy": "BTC",
        "instId": "BTC-USDT",
        "maxBuy": "0.0500695098559788",
        "maxSell": "64.4798671570072269"
  }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-maximum-order-quantity-response-parameters}

  -----------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------------
  instId                  String                  Instrument ID

  ccy                     String                  Currency used for margin

  maxBuy                  String                  `SPOT`/`MARGIN`: The maximum
                                                  quantity in base currency
                                                  that you can buy\
                                                  The cross-margin order under
                                                  `Futures mode` mode, quantity
                                                  of coins is based on base
                                                  currency.\
                                                  `FUTURES`/`SWAP`/`OPTIONS`:
                                                  The maximum quantity of
                                                  contracts that you can buy

  maxSell                 String                  `SPOT`/`MARGIN`: The maximum
                                                  quantity in quote currency
                                                  that you can sell\
                                                  The cross-margin order under
                                                  `Futures mode` mode, quantity
                                                  of coins is based on base
                                                  currency.\
                                                  `FUTURES`/`SWAP`/`OPTIONS`:
                                                  The maximum quantity of
                                                  contracts that you can sell
  -----------------------------------------------------------------------------

### Get maximum available balance/equity {#trading-account-rest-api-get-maximum-available-balance-equity}

Available balance for isolated margin positions and SPOT, available
equity for cross margin positions.

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-maximum-available-balance-equity-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-maximum-available-balance-equity-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-maximum-available-balance-equity-permission-read}

#### HTTP Request {#trading-account-rest-api-get-maximum-available-balance-equity-http-request}

`GET /api/v5/account/max-avail-size`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Query maximum available transaction amount when cross MARGIN BTC-USDT use BTC as margin
GET /api/v5/account/max-avail-size?instId=BTC-USDT&tdMode=cross&ccy=BTC

# Query maximum available transaction amount for SPOT BTC-USDT
GET /api/v5/account/max-avail-size?instId=BTC-USDT&tdMode=cash
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get maximum available transaction amount for SPOT BTC-USDT
result = accountAPI.get_max_avail_size(
    instId="BTC-USDT",
    tdMode="cash"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-maximum-available-balance-equity-request-parameters}

  ---------------------------------------------------------------------------
  **Parameter**     **Type**          Required          Description
  ----------------- ----------------- ----------------- ---------------------
  instId            String            Yes               Single instrument or
                                                        multiple instruments
                                                        (no more than 5)
                                                        separated with comma,
                                                        e.g.
                                                        `BTC-USDT,ETH-USDT`

  ccy               String            Conditional       Currency used for
                                                        margin\
                                                        Applicable to
                                                        `isolated` `MARGIN`
                                                        and `cross` `MARGIN`
                                                        in `Futures mode`.

  tdMode            String            Yes               Trade mode\
                                                        `cross`\
                                                        `isolated`\
                                                        `cash`\
                                                        `spot_isolated`: only
                                                        applicable to
                                                        `Futures mode`

  reduceOnly        Boolean           No                Whether to reduce
                                                        position only\
                                                        Only applicable to
                                                        `MARGIN`

  px                String            No                The price of closing
                                                        position.\
                                                        Only applicable to
                                                        reduceOnly `MARGIN`.

  tradeQuoteCcy     String            No                The quote currency
                                                        used for trading.
                                                        Only applicable to
                                                        `SPOT`.\
                                                        The default value is
                                                        the quote currency of
                                                        the `instId`, for
                                                        example: for
                                                        `BTC-USD`, the
                                                        default is `USD`.
  ---------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instId": "BTC-USDT",
      "availBuy": "100",
      "availSell": "1"
    }
  ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-maximum-available-balance-equity-response-parameters}

  **Parameter**   **Type**   **Description**
  --------------- ---------- ------------------------------------------
  instId          String     Instrument ID
  availBuy        String     Maximum available balance/equity to buy
  availSell       String     Maximum available balance/equity to sell

In the case of SPOT/MARGIN, availBuy is in the quote currency, and
availSell is in the base currency.\
In the case of MARGIN with cross tdMode, both availBuy and availSell are
in the currency passed in **ccy**.

### Increase/decrease margin {#trading-account-rest-api-increase-decrease-margin}

Increase or decrease the margin of the isolated position. Margin
reduction may result in the change of the actual leverage.

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-increase-decrease-margin-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-increase-decrease-margin-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-increase-decrease-margin-permission-trade}

#### HTTP Request {#trading-account-rest-api-increase-decrease-margin-http-request}

`POST /api/v5/account/position/margin-balance`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/position/margin-balance
body
{
    "instId":"BTC-USDT-200626",
    "posSide":"short",
    "type":"add",
    "amt":"1"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Increase margin
result = accountAPI.adjustment_margin(
    instId="BTC-USDT-SWAP",
    posSide="short",
    type= "add",
    amt="1"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-increase-decrease-margin-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instId            String            Yes               Instrument ID

  posSide           String            Yes               Position side,
                                                        the default is
                                                        `net`\
                                                        `long`\
                                                        `short`\
                                                        `net`

  type              String            Yes               `add`: add
                                                        margin\
                                                        `reduce`: reduce
                                                        margin

  amt               String            Yes               Amount to be
                                                        increased or
                                                        decreased.

  ccy               String            Conditional       Currency\
                                                        Applicable to
                                                        `isolated`
                                                        `MARGIN` orders
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
            "amt": "0.3",
            "ccy": "BTC",
            "instId": "BTC-USDT",
            "leverage": "",
            "posSide": "net",
            "type": "add"
        }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-increase-decrease-margin-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instId                  String                  Instrument ID

  posSide                 String                  Position side, `long`
                                                  `short`

  amt                     String                  Amount to be increase
                                                  or decrease

  type                    String                  `add`: add margin\
                                                  `reduce`: reduce margin

  leverage                String                  Real leverage after the
                                                  margin adjustment

  ccy                     String                  Currency
  -----------------------------------------------------------------------

Manual transfer mode\
The value of the margin initially assigned to the isolated position must
be greater than or equal to 10,000 USDT, and a position will be created
on the account.

### Get leverage {#trading-account-rest-api-get-leverage}

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-leverage-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-leverage-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-leverage-permission-read}

#### HTTP Request {#trading-account-rest-api-get-leverage-http-request}

`GET /api/v5/account/leverage-info`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/leverage-info?instId=BTC-USDT-SWAP&mgnMode=cross
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get leverage
result = accountAPI.get_leverage(
    instId="BTC-USDT-SWAP",
    mgnMode="cross"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-leverage-request-parameters}

  ----------------------------------------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ----------------------------------------------------------
  instId            String            Conditional       Instrument ID\
                                                        Single instrument ID or multiple instrument IDs (no more
                                                        than 20) separated with comma

  ccy               String            Conditional       Currency，used for getting leverage of currency level.\
                                                        Applicable to `cross` `MARGIN` of
                                                        `Spot mode`/`Multi-currency margin`/`Portfolio margin`.\
                                                        Supported single currency or multiple currencies (no more
                                                        than 20) separated with comma.

  mgnMode           String            Yes               Margin mode\
                                                        `cross` `isolated`
  ----------------------------------------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "ccy":"",
        "instId": "BTC-USDT-SWAP",
        "mgnMode": "cross",
        "posSide": "long",
        "lever": "10"
    },{
        "ccy":"",
        "instId": "BTC-USDT-SWAP",
        "mgnMode": "cross",
        "posSide": "short",
        "lever": "10"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-leverage-response-parameters}

  ---------------------------------------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ---------------------------------------------------------
  instId                  String                  Instrument ID

  ccy                     String                  Currency，used for getting leverage of currency level.\
                                                  Applicable to `cross` `MARGIN` of
                                                  `Spot mode`/`Multi-currency margin`/`Portfolio margin`.

  mgnMode                 String                  Margin mode

  posSide                 String                  Position side\
                                                  `long`\
                                                  `short`\
                                                  `net`\
                                                  In `long/short` mode, the leverage in both directions
                                                  `long`/`short` will be returned.

  lever                   String                  Leverage
  ---------------------------------------------------------------------------------------------------------

Leverage cannot be enquired for the cross positions of Expiry Futures
and Perpetual Futures under the portfolio margin account.

### Get leverage estimated info {#trading-account-rest-api-get-leverage-estimated-info}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-leverage-estimated-info-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-leverage-estimated-info-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-leverage-estimated-info-permission-read}

#### HTTP Request {#trading-account-rest-api-get-leverage-estimated-info-http-request}

`GET /api/v5/account/adjust-leverage-info`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/adjust-leverage-info?instType=MARGIN&mgnMode=isolated&lever=3&instId=BTC-USDT
```
:::

#### Request Parameters {#trading-account-rest-api-get-leverage-estimated-info-request-parameters}

  -------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -------------------------
  instType          String            Yes               Instrument type\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`

  mgnMode           String            Yes               Margin mode\
                                                        `isolated`\
                                                        `cross`

  lever             String            Yes               Leverage

  instId            String            Conditional       Instrument ID, e.g.
                                                        BTC-USDT\
                                                        It is required for these
                                                        scenarioes: `SWAP` and
                                                        `FUTURES`, Margin
                                                        isolation, Margin cross
                                                        in `Futures mode`.

  ccy               String            Conditional       Currency used for margin,
                                                        e.g. BTC\
                                                        It is required for
                                                        isolated margin and cross
                                                        margin in `Futures mode`,
                                                        `Multi-currency margin`
                                                        and `Portfolio margin`

  posSide           String            No                posSide\
                                                        `net`: The default value\
                                                        `long`\
                                                        `short`
  -------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "estAvailQuoteTrans": "",
            "estAvailTrans": "1.1398040558348279",
            "estLiqPx": "",
            "estMaxAmt": "10.6095865868904898",
            "estMgn": "0.0701959441651721",
            "estQuoteMaxAmt": "176889.6871254563042714",
            "estQuoteMgn": "",
            "existOrd": false,
            "maxLever": "10",
            "minLever": "0.01"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-leverage-estimated-info-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  estAvailQuoteTrans      String                  The estimated margin(in
                                                  quote currency) can be
                                                  transferred out under
                                                  the corresponding
                                                  leverage\
                                                  For cross, it is the
                                                  maximum quantity that
                                                  can be transferred from
                                                  the trading account.\
                                                  For isolated, it is the
                                                  maximum quantity that
                                                  can be transferred from
                                                  the isolated position\
                                                  Only applicable to
                                                  `MARGIN`

  estAvailTrans           String                  The estimated margin
                                                  can be transferred out
                                                  under the corresponding
                                                  leverage.\
                                                  For cross, it is the
                                                  maximum quantity that
                                                  can be transferred from
                                                  the trading account.\
                                                  For isolated, it is the
                                                  maximum quantity that
                                                  can be transferred from
                                                  the isolated position\
                                                  The unit is base
                                                  currency for `MARGIN`\
                                                  It is not applicable to
                                                  the scenario when
                                                  increasing leverage for
                                                  isolated position under
                                                  `FUTURES` and `SWAP`

  estLiqPx                String                  The estimated
                                                  liquidation price under
                                                  the corresponding
                                                  leverage. Only return
                                                  when there is a
                                                  position.

  estMgn                  String                  The estimated margin
                                                  needed by position
                                                  under the corresponding
                                                  leverage.\
                                                  For the `MARGIN`
                                                  position, it is margin
                                                  in base currency

  estQuoteMgn             String                  The estimated margin
                                                  (in quote currency)
                                                  needed by position
                                                  under the corresponding
                                                  leverage

  estMaxAmt               String                  For `MARGIN`, it is the
                                                  estimated maximum loan
                                                  in base currency under
                                                  the corresponding
                                                  leverage\
                                                  For `SWAP` and
                                                  `FUTURES`, it is the
                                                  estimated maximum
                                                  quantity of contracts
                                                  that can be opened
                                                  under the corresponding
                                                  leverage

  estQuoteMaxAmt          String                  The `MARGIN` estimated
                                                  maximum loan in quote
                                                  currency under the
                                                  corresponding leverage.

  existOrd                Boolean                 Whether there is
                                                  pending orders\
                                                  `true`\
                                                  `false`

  maxLever                String                  Maximum leverage

  minLever                String                  Minimum leverage
  -----------------------------------------------------------------------

### Get the maximum loan of instrument {#trading-account-rest-api-get-the-maximum-loan-of-instrument}

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-the-maximum-loan-of-instrument-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-the-maximum-loan-of-instrument-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-the-maximum-loan-of-instrument-permission-read}

#### HTTP Request {#trading-account-rest-api-get-the-maximum-loan-of-instrument-http-request}

`GET /api/v5/account/max-loan`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Max loan of cross `MARGIN` for currencies of trading pair in `Spot mode` (enabled borrowing)
GET  /api/v5/account/max-loan?instId=BTC-USDT&mgnMode=cross

# Max loan for currency in `Spot mode` (enabled borrowing)
GET  /api/v5/account/max-loan?ccy=USDT&mgnMode=cross

# Max loan of isolated `MARGIN` in `Futures mode`
GET  /api/v5/account/max-loan?instId=BTC-USDT&mgnMode=isolated

# Max loan of cross `MARGIN` in `Futures mode` (Margin Currency is BTC)
GET  /api/v5/account/max-loan?instId=BTC-USDT&mgnMode=cross&mgnCcy=BTC

# Max loan of cross `MARGIN` in `Multi-currency margin`
GET  /api/v5/account/max-loan?instId=BTC-USDT&mgnMode=cross
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Max loan of cross MARGIN in Futures mode (Margin Currency is BTC)
result = accountAPI.get_max_loan(
    instId="BTC-USDT",
    mgnMode="cross",
    mgnCcy="BTC"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-the-maximum-loan-of-instrument-request-parameters}

  ---------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------
  mgnMode           String            Yes               Margin mode\
                                                        `isolated` `cross`

  instId            String            Conditional       Single instrument or
                                                        multiple instruments
                                                        (no more than 5)
                                                        separated with comma,
                                                        e.g.
                                                        `BTC-USDT,ETH-USDT`

  ccy               String            Conditional       Currency\
                                                        Applicable to get Max
                                                        loan of manual borrow
                                                        for the currency in
                                                        `Spot mode` (enabled
                                                        borrowing)

  mgnCcy            String            Conditional       Margin currency\
                                                        Applicable to
                                                        `isolated` `MARGIN`
                                                        and `cross` `MARGIN`
                                                        in `Futures mode`.

  tradeQuoteCcy     String            No                The quote currency
                                                        for trading. Only
                                                        applicable to
                                                        `SPOT`.\
                                                        The default value is
                                                        the quote currency of
                                                        `instId`, e.g. `USD`
                                                        for `BTC-USD`.
  ---------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "instId": "BTC-USDT",
      "mgnMode": "isolated",
      "mgnCcy": "",
      "maxLoan": "0.1",
      "ccy": "BTC",
      "side": "sell"
    },
    {
      "instId": "BTC-USDT",
      "mgnMode": "isolated",
      "mgnCcy": "",
      "maxLoan": "0.2",
      "ccy": "USDT",
      "side": "buy"
    }
  ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-the-maximum-loan-of-instrument-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  instId                  String                  Instrument ID

  mgnMode                 String                  Margin mode

  mgnCcy                  String                  Margin currency

  maxLoan                 String                  Max loan

  ccy                     String                  Currency

  side                    String                  Order side\
                                                  `buy` `sell`
  -----------------------------------------------------------------------

### Get fee rates {#trading-account-rest-api-get-fee-rates}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-fee-rates-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-fee-rates-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-fee-rates-permission-read}

#### HTTP Request {#trading-account-rest-api-get-fee-rates-http-request}

`GET /api/v5/account/trade-fee`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Query trade fee rate of SPOT BTC-USDT
GET /api/v5/account/trade-fee?instType=SPOT&instId=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get trading fee rates of current account
result = accountAPI.get_fee_rates(
    instType="SPOT",
    instId="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-fee-rates-request-parameters}

  ---------------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ---------------------------
  instType          String            Yes               Instrument type\
                                                        `SPOT`\
                                                        `MARGIN`\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instId            String            No                Instrument ID, e.g.
                                                        `BTC-USDT`\
                                                        Applicable to
                                                        `SPOT`/`MARGIN`

  instFamily        String            No                Instrument family, e.g.
                                                        `BTC-USD`\
                                                        Applicable to
                                                        `FUTURES`/`SWAP`/`OPTION`

  ruleType          String            No                Trading rule types\
                                                        `normal`: normal trading\
                                                        `pre_market`: pre-market
                                                        trading\
                                                        ruleType can not be passed
                                                        through together with
                                                        instId/instFamily
  ---------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [{
    "category": "1", //Deprecated
    "delivery": "",
    "exercise": "",
    "instType": "SPOT",
    "level": "lv1",
    "maker": "-0.0008",
    "makerU": "",
    "makerUSDC": "",
    "taker": "-0.001",
    "takerU": "",
    "takerUSDC": "",
    "ruleType": "normal",
    "ts": "1608623351857",
    "fiat": []
  }
  ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-fee-rates-response-parameters}

  ----------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ----------------------------
  level                   String                  Fee rate Level

  taker                   String                  For `SPOT`/`MARGIN`, it is
                                                  taker fee rate of the USDT
                                                  trading pairs.\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  it is the fee rate of
                                                  crypto-margined contracts

  maker                   String                  For `SPOT`/`MARGIN`, it is
                                                  maker fee rate of the USDT
                                                  trading pairs.\
                                                  For
                                                  `FUTURES`/`SWAP`/`OPTION`,
                                                  it is the fee rate of
                                                  crypto-margined contracts

  takerU                  String                  Taker fee rate of
                                                  USDT-margined contracts,
                                                  only applicable to
                                                  `FUTURES`/`SWAP`

  makerU                  String                  Maker fee rate of
                                                  USDT-margined contracts,
                                                  only applicable to
                                                  `FUTURES`/`SWAP`

  delivery                String                  Delivery fee rate

  exercise                String                  Fee rate for exercising the
                                                  option

  instType                String                  Instrument type

  takerUSDC               String                  For `SPOT`/`MARGIN`, it is
                                                  taker fee rate of the
                                                  USDⓈ&Crypto trading pairs.\
                                                  For `FUTURES`/`SWAP`, it is
                                                  the fee rate of
                                                  USDC-margined contracts

  makerUSDC               String                  For `SPOT`/`MARGIN`, it is
                                                  maker fee rate of the
                                                  USDⓈ&Crypto trading pairs.\
                                                  For `FUTURES`/`SWAP`, it is
                                                  the fee rate of
                                                  USDC-margined contracts

  ruleType                String                  Trading rule types\
                                                  `normal`: normal trading\
                                                  `pre_market`: pre-market
                                                  trading

  ts                      String                  Data return time, Unix
                                                  timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  category                String                  Currency category. Note:
                                                  this parameter is already
                                                  deprecated

  fiat                    Array of objects        Details of fiat fee rate

  \> ccy                  String                  Fiat currency.

  \> taker                String                  Taker fee rate

  \> maker                String                  Maker fee rate
  ----------------------------------------------------------------------------

Remarks:\
The fee rate like maker and taker: positive number, which means the rate
of rebate; negative number, which means the rate of commission.

USDⓈ represent the stablecoin besides USDT and USDC

The Open API will not reflect zero-fee trading. For zero-fee pairs,
please refer to <https://www.okx.com/fees> .

### Get interest accrued data {#trading-account-rest-api-get-interest-accrued-data}

Get the interest accrued data for the past year

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-interest-accrued-data-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-interest-accrued-data-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-interest-accrued-data-permission-read}

#### HTTP Request {#trading-account-rest-api-get-interest-accrued-data-http-request}

`GET /api/v5/account/interest-accrued`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/interest-accrued
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get interest accrued data
result = accountAPI.get_interest_accrued()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-interest-accrued-data-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  type              String            No                Loan type\
                                                        `2`: Market
                                                        loans\
                                                        Default is `2`

  ccy               String            No                Loan currency,
                                                        e.g. `BTC`\
                                                        Only applicable
                                                        to
                                                        `Market loans`\
                                                        Only applicable
                                                        to`MARGIN`

  instId            String            No                Instrument ID,
                                                        e.g. `BTC-USDT`\
                                                        Only applicable
                                                        to `Market loans`

  mgnMode           String            No                Margin mode\
                                                        `cross`\
                                                        `isolated`\
                                                        Only applicable
                                                        to `Market loans`

  after             String            No                Pagination of
                                                        data to return
                                                        records earlier
                                                        than the
                                                        requested
                                                        timestamp, Unix
                                                        timestamp format
                                                        in milliseconds,
                                                        e.g.
                                                        `1597026383085`

  before            String            No                Pagination of
                                                        data to return
                                                        records newer
                                                        than the
                                                        requested, Unix
                                                        timestamp format
                                                        in milliseconds,
                                                        e.g.
                                                        `1597026383085`

  limit             String            No                Number of results
                                                        per request. The
                                                        maximum is `100`.
                                                        The default is
                                                        `100`.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "ccy": "USDT",
            "instId": "",
            "interest": "0.0003960833333334",
            "interestRate": "0.0000040833333333",
            "liab": "97",
            "totalLiab": "",
            "interestFreeLiab": "",
            "mgnMode": "",
            "ts": "1637312400000",
            "type": "1"
        },
        {
            "ccy": "USDT",
            "instId": "",
            "interest": "0.0004083333333334",
            "interestRate": "0.0000040833333333",
            "liab": "100",
            "mgnMode": "",
            "ts": "1637049600000",
            "type": "1"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-interest-accrued-data-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  type                    String                  Loan type\
                                                  `2`: Market loans

  ccy                     String                  Loan currency, e.g.
                                                  `BTC`

  instId                  String                  Instrument ID, e.g.
                                                  `BTC-USDT`\
                                                  Only applicable to
                                                  `Market loans`

  mgnMode                 String                  Margin mode\
                                                  `cross`\
                                                  `isolated`

  interest                String                  Interest

  interestRate            String                  Interest rate (in hour)

  liab                    String                  Liability

  totalLiab               String                  Total liability for
                                                  current account

  interestFreeLiab        String                  Interest-free liability
                                                  for current account

  ts                      String                  Timestamp for interest
                                                  accrued, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`
  -----------------------------------------------------------------------

### Get interest rate {#trading-account-rest-api-get-interest-rate}

Get the user\'s current leveraged currency borrowing market interest
rate

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-interest-rate-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-interest-rate-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-interest-rate-permission-read}

#### HTTP Request {#trading-account-rest-api-get-interest-rate-http-request}

`GET /api/v5/account/interest-rate`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/interest-rate
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get the user's current leveraged currency borrowing interest rate
result = accountAPI.get_interest_rate()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-interest-rate-request-parameters}

  **Parameters**   **Types**   **Required**   **Description**
  ---------------- ----------- -------------- ----------------------
  ccy              String      No             Currency, e.g. `BTC`

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data":[
        {
            "ccy":"BTC",
            "interestRate":"0.0001"
        },
        {
            "ccy":"LTC",
            "interestRate":"0.0003"
        }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-interest-rate-response-parameters}

  Parameter      Type     Description
  -------------- -------- ----------------------
  interestRate   String   hourly interest rate
  ccy            String   currency

### Set fee type {#trading-account-rest-api-set-fee-type}

Set the fee type.

fee type selection is only effective for Spot.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-fee-type-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-fee-type-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-fee-type-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-fee-type-http-request}

`POST /api/v5/account/set-fee-type`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-fee-type
body
{
    "feeType":"0"
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-fee-type-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  feeType           String            Yes               Fee type\
                                                        `0`: fee is
                                                        charged in the
                                                        currency you
                                                        receive from the
                                                        trade (default)\
                                                        `1`: fee is
                                                        always charged in
                                                        the quote
                                                        currency of the
                                                        trading pair
                                                        (only effective
                                                        for Spot)

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "feeType": "0"
        }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-fee-type-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  feeType                 String                  Fee type\
                                                  `0`: fee is charged in
                                                  the currency you
                                                  receive from the trade\
                                                  `1`: fee is always
                                                  charged in the quote
                                                  currency of the trading
                                                  pair

  -----------------------------------------------------------------------

### Set greeks (PA/BS) {#trading-account-rest-api-set-greeks-pa-bs}

Set the display type of Greeks.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-greeks-pa-bs-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-greeks-pa-bs-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-greeks-pa-bs-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-greeks-pa-bs-http-request}

`POST /api/v5/account/set-greeks`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-greeks
body
{
    "greeksType":"PA"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Set greeks (PA/BS)
result = accountAPI.set_greeks(greeksType="PA")
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-set-greeks-pa-bs-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  greeksType        String            Yes               Display type of
                                                        Greeks.\
                                                        `PA`: Greeks in
                                                        coins\
                                                        `BS`:
                                                        Black-Scholes
                                                        Greeks in dollars

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "greeksType": "PA"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-greeks-pa-bs-response-parameters}

  Parameter    Type     Description
  ------------ -------- -------------------------
  greeksType   String   Display type of Greeks.

### Isolated margin trading settings {#trading-account-rest-api-isolated-margin-trading-settings}

You can set the currency margin and futures/perpetual Isolated margin
trading mode

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-isolated-margin-trading-settings-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-isolated-margin-trading-settings-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-isolated-margin-trading-settings-permission-trade}

#### HTTP Request {#trading-account-rest-api-isolated-margin-trading-settings-http-request}

`POST /api/v5/account/set-isolated-mode`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-isolated-mode
body
{
    "isoMode":"automatic",
    "type":"MARGIN"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Isolated margin trading settings
result = accountAPI.set_isolated_mode(
    isoMode="automatic",
    type="MARGIN"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-isolated-margin-trading-settings-request-parameters}

  -----------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------------
  isoMode           String            Yes               Isolated margin trading
                                                        settings\
                                                        `auto_transfers_ccy`:
                                                        New auto transfers,
                                                        enabling both base and
                                                        quote currency as the
                                                        margin for isolated
                                                        margin trading. Only
                                                        applicable to
                                                        `MARGIN`.\
                                                        `automatic`: Auto
                                                        transfers

  type              String            Yes               Instrument type\
                                                        `MARGIN`\
                                                        `CONTRACTS`
  -----------------------------------------------------------------------------

When there are positions and pending orders in the current account, the
margin transfer mode from position to position cannot be adjusted.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "isoMode": "automatic"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-isolated-margin-trading-settings-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  isoMode                 String                  Isolated margin trading
                                                  settings\
                                                  `automatic`: Auto
                                                  transfers

  -----------------------------------------------------------------------

CONTRACTS\
Auto transfers: Automatically occupy and release the margin when opening
and closing positions

MARGIN\
Auto transfers: Automatically borrow and return coins when opening and
closing positions

### Get maximum withdrawals {#trading-account-rest-api-get-maximum-withdrawals}

Retrieve the maximum transferable amount from trading account to funding
account. If no currency is specified, the transferable amount of all
owned currencies will be returned.

#### Rate Limit: 20 requests per 2 seconds {#trading-account-rest-api-get-maximum-withdrawals-rate-limit-20-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-maximum-withdrawals-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-maximum-withdrawals-permission-read}

#### HTTP Request {#trading-account-rest-api-get-maximum-withdrawals-http-request}

`GET /api/v5/account/max-withdrawal`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/max-withdrawal
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get maximum withdrawals
result = accountAPI.get_max_withdrawal()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-maximum-withdrawals-request-parameters}

  Parameter   Type     Required   Description
  ----------- -------- ---------- ---------------------------------------------------------------------------------------------------------
  ccy         String   No         Single currency or multiple currencies (no more than 20) separated with comma, e.g. `BTC` or `BTC,ETH`.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
            "ccy": "BTC",
            "maxWd": "124",
            "maxWdEx": "125",
            "spotOffsetMaxWd": "",
            "spotOffsetMaxWdEx": ""
        },
        {
            "ccy": "ETH",
            "maxWd": "10",
            "maxWdEx": "12",
            "spotOffsetMaxWd": "",
            "spotOffsetMaxWdEx": ""
        }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-maximum-withdrawals-response-parameters}

  ---------------------------------------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ---------------------------------------------------------
  ccy                     String                  Currency

  maxWd                   String                  Max withdrawal (excluding borrowed assets under
                                                  `Spot mode`/`Multi-currency margin`/`Portfolio margin`)

  maxWdEx                 String                  Max withdrawal (including borrowed assets under
                                                  `Spot mode`/`Multi-currency margin`/`Portfolio margin`)

  spotOffsetMaxWd         String                  Max withdrawal under Spot-Derivatives risk offset mode
                                                  (excluding borrowed assets under `Portfolio margin`)\
                                                  Applicable to `Portfolio margin`

  spotOffsetMaxWdEx       String                  Max withdrawal under Spot-Derivatives risk offset mode
                                                  (including borrowed assets under `Portfolio margin`)\
                                                  Applicable to `Portfolio margin`
  ---------------------------------------------------------------------------------------------------------

### Get account risk state {#trading-account-rest-api-get-account-risk-state}

Only applicable to Portfolio margin account

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-account-risk-state-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-account-risk-state-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-account-risk-state-permission-read}

#### HTTP Request {#trading-account-rest-api-get-account-risk-state-http-request}

`GET /api/v5/account/risk-state`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/risk-state
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get account risk state
result = accountAPI.get_account_position_risk()
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
            "atRisk": false,
            "atRiskIdx": [],
            "atRiskMgn": [],
            "ts": "1635745078794"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-account-risk-state-response-parameters}

  -----------------------------------------------------------------------
  **Parameters**          **Types**               **Description**
  ----------------------- ----------------------- -----------------------
  atRisk                  Boolean                 Account risk status in
                                                  auto-borrow mode\
                                                  true: the account is
                                                  currently in a specific
                                                  risk state\
                                                  false: the account is
                                                  currently not in a
                                                  specific risk state

  atRiskIdx               Array of strings        derivatives risk unit
                                                  list

  atRiskMgn               Array of strings        margin risk unit list

  ts                      String                  Unix timestamp format
                                                  in milliseconds,
                                                  e.g.`1597026383085`
  -----------------------------------------------------------------------

### Get borrow interest and limit {#trading-account-rest-api-get-borrow-interest-and-limit}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-borrow-interest-and-limit-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-borrow-interest-and-limit-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-borrow-interest-and-limit-permission-read}

#### HTTP Request {#trading-account-rest-api-get-borrow-interest-and-limit-http-request}

`GET /api/v5/account/interest-limits`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/interest-limits?ccy=BTC
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get borrow interest and limit
result = accountAPI.get_interest_limits(
    ccy="BTC"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-borrow-interest-and-limit-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  type              String            No                Loan type\
                                                        `2`: Market
                                                        loans\
                                                        Default is `2`

  ccy               String            No                Loan currency,
                                                        e.g. `BTC`
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "debt": "0.85893159114900247077000000000000",
            "interest": "0.00000000000000000000000000000000",
            "loanAlloc": "",
            "nextDiscountTime": "1729490400000",
            "nextInterestTime": "1729490400000",
            "records": [
                {
                    "availLoan": "",
                    "avgRate": "",
                    "ccy": "BTC",
                    "interest": "0",
                    "loanQuota": "175.00000000",
                    "posLoan": "",
                    "rate": "0.0000276",
                    "surplusLmt": "175.00000000",
                    "surplusLmtDetails": {},
                    "usedLmt": "0.00000000",
                    "usedLoan": "",
                    "interestFreeLiab": "",
                    "potentialBorrowingAmt": ""
                }
            ]
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-borrow-interest-and-limit-response-parameters}

  -------------------------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -------------------------------------
  debt                    String                  Current debt in `USD`

  interest                String                  Current interest in `USD`, the unit
                                                  is `USD`\
                                                  Only applicable to `Market loans`

  nextDiscountTime        String                  Next deduct time, Unix timestamp
                                                  format in milliseconds, e.g.
                                                  `1597026383085`

  nextInterestTime        String                  Next accrual time, Unix timestamp
                                                  format in milliseconds, e.g.
                                                  `1597026383085`

  loanAlloc               String                  VIP Loan allocation for the current
                                                  trading account\
                                                  1. The unit is percent(%). Range is
                                                  \[0, 100\]. Precision is 0.01%\
                                                  2. If master account did not assign
                                                  anything, then \"0\"\
                                                  3. \"\" if shared between master and
                                                  sub-account

  records                 Array of objects        Details for currencies

  \> ccy                  String                  Loan currency, e.g. `BTC`

  \> rate                 String                  Current daily rate

  \> loanQuota            String                  Borrow limit of master account\
                                                  If loan allocation has been assigned,
                                                  then it is the borrow limit of the
                                                  current trading account

  \> surplusLmt           String                  Available amount across all
                                                  sub-accounts\
                                                  If loan allocation has been assigned,
                                                  then it is the available amount to
                                                  borrow by the current trading account

  \> usedLmt              String                  Borrowed amount for current account\
                                                  If loan allocation has been assigned,
                                                  then it is the borrowed amount by the
                                                  current trading account

  \> interest             String                  Interest to be deducted\
                                                  Only applicable to `Market loans`

  \> interestFreeLiab     String                  Interest-free liability for current
                                                  account

  \>                      String                  Potential borrowing amount for
  potentialBorrowingAmt                           current account

  \> surplusLmtDetails    Object                  ~~The details of available amount
                                                  across all sub-accounts\
                                                  The value of `surplusLmt` is the
                                                  minimum value within this array. It
                                                  can help you judge the reason that
                                                  `surplusLmt` is not enough.\
                                                  Only applicable to
                                                  `VIP loans`~~Deprecated

  \>\>                    String                  ~~Total remaining quota for master
  allAcctRemainingQuota                           account and sub-accounts~~ Deprecated

  \>\>                    String                  ~~The remaining quota for the current
  curAcctRemainingQuota                           account.\
                                                  Only applicable to the case in which
                                                  the sub-account is assigned the loan
                                                  allocation~~Deprecated

  \>\> platRemainingQuota String                  ~~Remaining quota for the platform.\
                                                  The format like \"600\" will be
                                                  returned when it is more than
                                                  `curAcctRemainingQuota` or
                                                  `allAcctRemainingQuota`~~Deprecated

  \> posLoan              String                  ~~Frozen amount for current account
                                                  (Within the locked quota)\
                                                  Only applicable to
                                                  `VIP loans`~~Deprecated

  \> availLoan            String                  ~~Available amount for current
                                                  account (Within the locked quota)\
                                                  Only applicable to
                                                  `VIP loans`~~Deprecated

  \> usedLoan             String                  ~~Borrowed amount for current
                                                  account\
                                                  Only applicable to
                                                  `VIP loans`~~Deprecated

  \> avgRate              String                  ~~Average (hour) interest of already
                                                  borrowed coin\
                                                  only applicable to
                                                  `VIP loans`~~Deprecated
  -------------------------------------------------------------------------------------

### Manual borrow / repay {#trading-account-rest-api-manual-borrow-repay}

Only applicable to `Spot mode` (enabled borrowing)

#### Rate Limit: 1 request per 3 seconds {#trading-account-rest-api-manual-borrow-repay-rate-limit-1-request-per-3-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-manual-borrow-repay-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-manual-borrow-repay-permission-trade}

#### HTTP Request {#trading-account-rest-api-manual-borrow-repay-http-request}

`POST /api/v5/account/spot-manual-borrow-repay`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/spot-manual-borrow-repay
body
{
    "ccy":"USDT",
    "side":"borrow",
    "amt":"100"
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1
accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.spot_manual_borrow_repay(ccy="USDT", side="borrow", amt= "1")
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-manual-borrow-repay-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  ccy               String            Yes               Currency, e.g.
                                                        `BTC`

  side              String            Yes               Side\
                                                        `borrow`\
                                                        `repay`

  amt               String            Yes               Amount
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "ccy":"USDT",
            "side":"borrow",
            "amt":"100"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-manual-borrow-repay-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  ccy                     String                  Currency, e.g. `BTC`

  side                    String                  Side\
                                                  `borrow`\
                                                  `repay`

  amt                     String                  Actual amount
  -----------------------------------------------------------------------

### Set auto repay {#trading-account-rest-api-set-auto-repay}

Only applicable to `Spot mode` (enabled borrowing)

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-auto-repay-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-auto-repay-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-auto-repay-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-auto-repay-http-request}

`POST /api/v5/account/set-auto-repay`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-auto-repay
body
{
    "autoRepay": true
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1
accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.set_auto_repay(autoRepay=True)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-set-auto-repay-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  autoRepay         Boolean           Yes               Whether auto
                                                        repay is allowed
                                                        or not under
                                                        `Spot mode`\
                                                        `true`: Enable
                                                        auto repay\
                                                        `false`: Disable
                                                        auto repay

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "autoRepay": true
        }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-auto-repay-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  autoRepay               Boolean                 Whether auto repay is
                                                  allowed or not under
                                                  `Spot mode`\
                                                  `true`: Enable auto
                                                  repay\
                                                  `false`: Disable auto
                                                  repay

  -----------------------------------------------------------------------

### Get borrow/repay history {#trading-account-rest-api-get-borrow-repay-history}

Retrieve the borrow/repay history under `Spot mode`

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-borrow-repay-history-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-borrow-repay-history-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-borrow-repay-history-permission-read}

#### HTTP Request {#trading-account-rest-api-get-borrow-repay-history-http-request}

`GET /api/v5/account/spot-borrow-repay-history`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/spot-borrow-repay-history
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"   # Production trading:0 , demo trading:1
accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.spot_borrow_repay_history(ccy="USDT", type="auto_borrow")
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-borrow-repay-history-request-parameters}

  ------------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- ------------------
  ccy               String            No                Currency, e.g.
                                                        `BTC`

  type              String            No                Event type\
                                                        `auto_borrow`\
                                                        `auto_repay`\
                                                        `manual_borrow`\
                                                        `manual_repay`

  after             String            No                Pagination of data
                                                        to return records
                                                        earlier than the
                                                        requested `ts`
                                                        (included), Unix
                                                        timestamp format
                                                        in milliseconds,
                                                        e.g.
                                                        `1597026383085`

  before            String            No                Pagination of data
                                                        to return records
                                                        newer than the
                                                        requested
                                                        `ts`(included),
                                                        Unix timestamp
                                                        format in
                                                        milliseconds, e.g.
                                                        `1597026383085`

  limit             String            No                Number of results
                                                        per request. The
                                                        maximum is 100.
                                                        The default is
                                                        100.
  ------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "accBorrowed": "0",
            "amt": "6764.802661157592",
            "ccy": "USDT",
            "ts": "1725330976644",
            "type": "auto_repay"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-borrow-repay-history-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  ccy                     String                  Currency, e.g. `BTC`

  type                    String                  Event type\
                                                  `auto_borrow`\
                                                  `auto_repay`\
                                                  `manual_borrow`\
                                                  `manual_repay`

  amt                     String                  Amount

  accBorrowed             String                  Accumulated borrow
                                                  amount

  ts                      String                  Timestamp for the
                                                  event, Unix timestamp
                                                  format in milliseconds,
                                                  e.g. `1597026383085`
  -----------------------------------------------------------------------

### Position builder (new) {#trading-account-rest-api-position-builder-new}

Calculates portfolio margin information for virtual position/assets or
current position of the user.\
You can add up to 200 virtual positions and 200 virtual assets in one
request.

#### Rate Limit: 2 requests per 2 seconds {#trading-account-rest-api-position-builder-new-rate-limit-2-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-position-builder-new-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-position-builder-new-permission-read}

#### HTTP Request {#trading-account-rest-api-position-builder-new-http-request}

`POST /api/v5/account/position-builder`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Both real and virtual positions and assets are calculated
POST /api/v5/account/position-builder
body
{
    "inclRealPosAndEq": false,
    "simPos":[
         {
            "pos":"-10",
            "instId":"BTC-USDT-SWAP",
            "avgPx":"100000"
         },
         {
            "pos":"10",
            "instId":"LTC-USDT-SWAP",
            "avgPx":"8000"
         }
    ],
    "simAsset":[
        {
            "ccy": "USDT",
            "amt": "100"
        }
    ],
    "greeksType":"CASH"
}


# Only existing real positions are calculated
POST /api/v5/account/position-builder
body
{
   "inclRealPosAndEq":true
}


# Only virtual positions are calculated
POST /api/v5/account/position-builder
body
{
    "acctLv": "4",
    "inclRealPosAndEq": false,
    "simPos":[
        {
            "pos":"10",
            "instId":"BTC-USDT-SWAP",
            "avgPx":"100000"
        },
        {
            "pos":"10",
            "instId":"LTC-USDT-SWAP",
            "avgPx":"8000"
        }
    ]
}

# Switch to Multi-currency margin mode
POST /api/v5/account/position-builder
body
{
    "acctLv": "3",
    "lever":"10",
    "simPos":[
        {
            "pos":"10",
            "instId":"BTC-USDT-SWAP",
            "avgPx":"100000",
            "lever":"5"
        },
        {
            "pos":"10",
            "instId":"LTC-USDT-SWAP",
            "avgPx":"8000"
        }
    ]
}
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

result = accountAPI.position_builder(
    inclRealPosAndEq=True,
    simPos=[
        {
            "pos": "10",
            "instId": "BTC-USDT-SWAP"
        },
        {
            "pos": "10",
            "instId": "LTC-USDT-SWAP"
        }
    ]
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-position-builder-new-request-parameters}

  ----------------------------------------------------------------------------------
  Parameter          Type              Required          Description
  ------------------ ----------------- ----------------- ---------------------------
  acctLv             String            No                Switch to account mode\
                                                         `3`: Multi-currency margin\
                                                         `4`: Portfolio margin\
                                                         The default is `4`

  inclRealPosAndEq   Boolean           No                Whether import existing
                                                         positions and assets\
                                                         The default is `true`

  lever              String            No                Cross margin leverage in
                                                         Multi-currency margin mode,
                                                         the default is `1`.\
                                                         If the allowed leverage is
                                                         exceeded, set according to
                                                         the maximum leverage.\
                                                         Only applicable to
                                                         `Multi-currency margin`

  simPos             Array of objects  No                List of simulated positions

  \> instId          String            Yes               Instrument ID, e.g.
                                                         `BTC-USDT-SWAP`\
                                                         Applicable to
                                                         `SWAP`/`FUTURES`/`OPTION`

  \> pos             String            Yes               Quantity of positions

  \> avgPx           String            Yes               Average open price

  \> lever           String            No                leverage\
                                                         Only applicable to
                                                         `Multi-currency margin`\
                                                         The default is `1`\
                                                         If the allowed leverage is
                                                         exceeded, set according to
                                                         the maximum leverage.

  simAsset           Array of objects  No                List of simulated assets\
                                                         When `inclRealPosAndEq` is
                                                         `true`, only real assets
                                                         are considered and virtual
                                                         assets are ignored

  \> ccy             String            Yes               Currency, e.g. `BTC`

  \> amt             String            Yes               Currency amount

  greeksType         String            No                Greeks type\
                                                         `BS`: Black-Scholes Model
                                                         Greeks\
                                                         `PA`: Crypto Greeks\
                                                         `CASH`: Empirical Greeks\
                                                         The default is `BS`

  idxVol             String            No                Price volatility
                                                         percentage, indicating what
                                                         this price change means
                                                         towards each of the values.
                                                         In decimal form, range
                                                         -0.99 \~ 1, in 0.01
                                                         increment.\
                                                         Default 0
  ----------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLever": "-0.1364949794742562",
            "assets": [
                {
                    "availEq": "0",
                    "borrowImr": "0",
                    "borrowMmr": "",
                    "ccy": "BTC",
                    "spotInUse": "0"
                },
                {
                    "availEq": "0",
                    "borrowImr": "0",
                    "borrowMmr": "",
                    "ccy": "LTC",
                    "spotInUse": "0"
                },
                {
                    "availEq": "0",
                    "borrowImr": "0",
                    "borrowMmr": "",
                    "ccy": "USDC",
                    "spotInUse": "0"
                },
                {
                    "availEq": "-78589.37",
                    "borrowImr": "7855.32188898",
                    "borrowMmr": "",
                    "ccy": "USDT",
                    "spotInUse": "0"
                }
            ],
            "borrowMmr": "1571.064377796",
            "derivMmr": "1375.4837063088003",
            "eq": "-78553.21888979999",
            "marginRatio": "-25.95365779811705",
            "positions": [],
            "riskUnitData": [
                {
                    "delta": "-9704.903689800001",
                    "gamma": "0",
                    "imrBf": "",
                    "imr": "1538.9669514070802",
                    "mmrBf": "",
                    "mmr": "1183.8207318516002",
                    "mr1": "1164.4109244719994",
                    "mr1FinalResult": {
                        "pnl": "-1164.4109244719994",
                        "spotShock": "0.12",
                        "volShock": "up"
                    },
                    "mr1Scenarios": {
                        "volSame": {
                            "0": "0",
                            "0.08": "-776.2739496480004",
                            "-0.08": "776.2739496480004",
                            "0.04": "-388.1369748240002",
                            "0.12": "-1164.4109244719994",
                            "-0.12": "1164.4109244719994",
                            "-0.04": "388.1369748240002"
                        },
                        "volShockDown": {
                            "0": "0",
                            "0.08": "-776.2739496480004",
                            "-0.08": "776.2739496480004",
                            "0.04": "-388.1369748240002",
                            "0.12": "-1164.4109244719994",
                            "-0.12": "1164.4109244719994",
                            "-0.04": "388.1369748240002"
                        },
                        "volShockUp": {
                            "0": "0",
                            "0.08": "-776.2739496480004",
                            "-0.08": "776.2739496480004",
                            "0.04": "-388.1369748240002",
                            "0.12": "-1164.4109244719994",
                            "-0.12": "1164.4109244719994",
                            "-0.04": "388.1369748240002"
                        }
                    },
                    "mr2": "0",
                    "mr3": "0",
                    "mr4": "19.4098073796",
                    "mr5": "0",
                    "mr6": "1164.4109244720003",
                    "mr6FinalResult": {
                        "pnl": "-2328.8218489440005",
                        "spotShock": "0.24"
                    },
                    "mr7": "43.67206660410001",
                    "mr8": "1571.064377796",
                    "mr9": "0",
                    "portfolios": [
                        {
                            "amt": "-10",
                            "avgPx": "100000",
                            "delta": "-9704.903689800001",
                            "floatPnl": "290.6300000000003",
                            "gamma": "0",
                            "instId": "BTC-USDT-SWAP",
                            "instType": "SWAP",
                            "isRealPos": false,
                            "markPxBf": "",
                            "markPx": "97093.7",
                            "notionalUsd": "9703.22",
                            "posSide": "net",
                            "theta": "0",
                            "vega": "0"
                        }
                    ],
                    "riskUnit": "BTC",
                    "theta": "0",
                    "upl": "290.49631020000027",
                    "vega": "0"
                },
                {
                    "delta": "1019.5308",
                    "gamma": "0",
                    "imrBf": "",
                    "imr": "249.16186679436",
                    "mmrBf": "",
                    "mmr": "191.6629744572",
                    "mr1": "183.50672805719995",
                    "mr1FinalResult": {
                        "pnl": "-183.50672805719995",
                        "spotShock": "-0.18",
                        "volShock": "up"
                    },
                    "mr1Scenarios": {
                        "volSame": {
                            "0": "0",
                            "-0.06": "-61.168909352399936",
                            "0.06": "61.168909352399936",
                            "-0.18": "-183.50672805719995",
                            "0.18": "183.50672805719995",
                            "0.12": "122.33781870480001",
                            "-0.12": "-122.33781870480001"
                        },
                        "volShockDown": {
                            "0": "0",
                            "-0.06": "-61.168909352399936",
                            "0.06": "61.168909352399936",
                            "-0.18": "-183.50672805719995",
                            "0.18": "183.50672805719995",
                            "0.12": "122.33781870480001",
                            "-0.12": "-122.33781870480001"
                        },
                        "volShockUp": {
                            "0": "0",
                            "-0.06": "-61.168909352399936",
                            "0.06": "61.168909352399936",
                            "-0.18": "-183.50672805719995",
                            "0.18": "183.50672805719995",
                            "0.12": "122.33781870480001",
                            "-0.12": "-122.33781870480001"
                        }
                    },
                    "mr2": "0",
                    "mr3": "0",
                    "mr4": "8.1562464",
                    "mr5": "0",
                    "mr6": "183.5067280572",
                    "mr6FinalResult": {
                        "pnl": "-367.0134561144",
                        "spotShock": "-0.36"
                    },
                    "mr7": "7.1367156",
                    "mr8": "1571.064377796",
                    "mr9": "0",
                    "portfolios": [
                        {
                            "amt": "10",
                            "avgPx": "8000",
                            "delta": "1019.5308",
                            "floatPnl": "-78980",
                            "gamma": "0",
                            "instId": "LTC-USDT-SWAP",
                            "instType": "SWAP",
                            "isRealPos": false,
                            "markPxBf": "",
                            "markPx": "102",
                            "notionalUsd": "1018.9",
                            "posSide": "net",
                            "theta": "0",
                            "vega": "0"
                        }
                    ],
                    "riskUnit": "LTC",
                    "theta": "0",
                    "upl": "-78943.6692",
                    "vega": "0"
                }
            ],
            "totalImr": "9643.45070718144",
            "totalMmr": "2946.5480841048",
            "ts": "1736936801642",
            "upl": "-78653.1728898"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-position-builder-new-response-parameters}

  ----------------------------------------------------------------------------
  **Parameters**          **Types**               **Description**
  ----------------------- ----------------------- ----------------------------
  eq                      String                  Adjusted equity (`USD`) for
                                                  the account

  totalMmr                String                  Total MMR (`USD`) for the
                                                  account

  totalImr                String                  Total IMR (`USD`) for the
                                                  account

  borrowMmr               String                  Borrow MMR (`USD`) for the
                                                  account

  derivMmr                String                  Derivatives MMR (`USD`) for
                                                  the account

  marginRatio             String                  Cross maintenance margin
                                                  ratio for the account

  upl                     String                  UPL for the account

  acctLever               String                  Leverage of the account

  ts                      String                  Update time for the account,
                                                  Unix timestamp format in
                                                  milliseconds, e.g.
                                                  `1597026383085`

  assets                  Array of objects        Asset info

  \> ccy                  String                  Currency, e.g. `BTC`

  \> availEq              String                  Currency equity

  \> spotInUse            String                  Spot in use

  \> borrowMmr            String                  ~~Borrowing MMR
                                                  (`USD`)~~(Deprecated)

  \> borrowImr            String                  Borrowing IMR (`USD`)

  riskUnitData            Array of objects        Risk unit info

  \> riskUnit             String                  Risk unit, e.g. `BTC`

  \> mmrBf                String                  Risk unit MMR before
                                                  volatility (`USD`)\
                                                  Return \"\" if users don\'t
                                                  pass in idxVol

  \> mmr                  String                  Risk unit MMR (`USD`)

  \> imrBf                String                  Risk unit IMR before
                                                  volatility (`USD`)\
                                                  Return \"\" if users don\'t
                                                  pass in idxVol

  \> imr                  String                  Risk unit IMR (`USD`)

  \> upl                  String                  Risk unit UPL (`USD`)

  \> mr1                  String                  Stress testing value of spot
                                                  and volatility (all
                                                  derivatives, and spot
                                                  trading in spot-derivatives
                                                  risk offset mode)

  \> mr2                  String                  Stress testing value of time
                                                  value of money (TVM) (for
                                                  options)

  \> mr3                  String                  Stress testing value of
                                                  volatility span (for
                                                  options)

  \> mr4                  String                  Stress testing value of
                                                  basis (for all derivatives)

  \> mr5                  String                  Stress testing value of
                                                  interest rate risk (for
                                                  options)

  \> mr6                  String                  Stress testing value of
                                                  extremely volatile markets
                                                  (for all derivatives, and
                                                  spot trading in
                                                  spot-derivatives risk offset
                                                  mode)

  \> mr7                  String                  Stress testing value of
                                                  position reduction cost (for
                                                  all derivatives)

  \> mr8                  String                  Borrowing MMR/IMR

  \> mr9                  String                  USDT-USDC-USD hedge risk

  \> mr1Scenarios         Object                  MR1 scenario analysis

  \>\> volShockDown       Object                  When volatility shocks down,
                                                  the P&L of stress tests
                                                  under different price
                                                  volatility ratios, format in
                                                  {`change`: `value`,\...}\
                                                  `change`: price volatility
                                                  ratio (in percentage), e.g.
                                                  `0.01` representing `1%`\
                                                  `value`: P&L under stress
                                                  tests, measured in `USD`\
                                                  e.g.
                                                  {\"-0.15\":\"-2333.23\",
                                                  \...}

  \>\> volSame            Object                  When volatility keeps the
                                                  same, the P&L of stress
                                                  tests under different price
                                                  volatility ratios, format in
                                                  {`change`: `value`,\...}\
                                                  `change`: price volatility
                                                  ratio (in percentage), e.g.
                                                  `0.01` representing `1%`\
                                                  `value`: P&L under stress
                                                  tests, measured in `USD`\
                                                  e.g.
                                                  {\"-0.15\":\"-2333.23\",
                                                  \...}

  \>\> volShockUp         Object                  When volatility shocks up,
                                                  the P&L of stress tests
                                                  under different price
                                                  volatility ratios, format in
                                                  {`change`: `value`,\...}\
                                                  `change`: price volatility
                                                  ratio (in percentage), e.g.
                                                  `0.01` representing `1%`\
                                                  `value`: P&L under stress
                                                  tests, measured in `USD`\
                                                  e.g.
                                                  {\"-0.15\":\"-2333.23\",
                                                  \...}

  \> mr1FinalResult       Object                  MR1 worst-case scenario

  \>\> pnl                String                  MR1 stress P&L (`USD`)

  \>\> spotShock          String                  MR1 worst-case scenario spot
                                                  shock (in percentage), e.g.
                                                  `0.01` representing `1%`

  \>\> volShock           String                  MR1 worst-case scenario
                                                  volatility shock\
                                                  `down`: volatility shock
                                                  down\
                                                  `unchange`: volatility
                                                  unchanged\
                                                  `up`: volatility shock up

  \> mr6FinalResult       Object                  MR6 scenario analysis

  \>\> pnl                String                  MR6 stress P&L (`USD`)

  \>\> spotShock          String                  MR6 worst-case scenario spot
                                                  shock (in percentage), e.g.
                                                  `0.01` representing `1%`

  \> delta                String                  (Risk unit) The rate of
                                                  change in the contract's
                                                  price with respect to
                                                  changes in the underlying
                                                  asset's price.\
                                                  When the price of the
                                                  underlying changes by x, the
                                                  option's price changes by
                                                  delta multiplied by x.

  \> gamma                String                  (Risk unit) The rate of
                                                  change in the delta with
                                                  respect to changes in the
                                                  underlying price.\
                                                  When the price of the
                                                  underlying changes by x%,
                                                  the option's delta changes
                                                  by gamma multiplied by x%.

  \> theta                String                  (Risk unit) The change in
                                                  contract price each day
                                                  closer to expiry.

  \> vega                 String                  (Risk unit) The change of
                                                  the option price when
                                                  underlying volatility
                                                  increases by 1%.

  \> portfolios           Array of objects        Portfolios info\
                                                  Only applicable to
                                                  `Portfolio margin`

  \>\> instId             String                  Instrument ID, e.g.
                                                  `BTC-USDT-SWAP`

  \>\> instType           String                  Instrument type\
                                                  `SPOT`\
                                                  `SWAP`\
                                                  `FUTURES`\
                                                  `OPTION`

  \>\> amt                String                  When `instType` is `SPOT`,
                                                  it represents spot in use.\
                                                  When `instType` is
                                                  `SWAP`/`FUTURES`/`OPTION`,
                                                  it represents position
                                                  amount.

  \>\> posSide            String                  Position side\
                                                  `long`\
                                                  `short`\
                                                  `net`

  \>\> avgPx              String                  Average open price

  \>\> markPxBf           String                  Mark price before price
                                                  volatility\
                                                  Return \"\" if users don\'t
                                                  pass in idxVol

  \>\> markPx             String                  Mark price

  \>\> floatPnl           String                  Float P&L

  \>\> notionalUsd        String                  Notional in `USD`

  \>\> delta              String                  When `instType` is `SPOT`,
                                                  it represents asset amount.\
                                                  When `instType` is
                                                  `SWAP`/`FUTURES`/`OPTION`,
                                                  it represents the rate of
                                                  change in the contract's
                                                  price with respect to
                                                  changes in the underlying
                                                  asset's price (by Instrument
                                                  ID).

  \>\> gamma              String                  The rate of change in the
                                                  delta with respect to
                                                  changes in the underlying
                                                  price (by Instrument ID).\
                                                  When `instType` is `SPOT`,
                                                  it will return \"\".

  \>\> theta              String                  The change in contract price
                                                  each day closer to expiry
                                                  (by Instrument ID).\
                                                  When `instType` is `SPOT`,
                                                  it will return \"\".

  \>\> vega               String                  The change of the option
                                                  price when underlying
                                                  volatility increases by 1%
                                                  (by Instrument ID).\
                                                  When `instType` is `SPOT`,
                                                  it will return \"\".

  \>\> isRealPos          Boolean                 Whether it is a real
                                                  position\
                                                  If `instType` is
                                                  `SWAP`/`FUTURES`/`OPTION`,
                                                  it is a valid parameter,
                                                  else it will return `false`

  positions               Array of objects        Position info\
                                                  Only applicable to
                                                  `Multi-currency margin`

  \> instId               String                  Instrument ID, e.g.
                                                  `BTC-USDT-SWAP`

  \> instType             String                  Instrument type\
                                                  `SPOT`\
                                                  `SWAP`\
                                                  `FUTURES`\
                                                  `OPTION`

  \> amt                  String                  When `instType` is `SPOT`,
                                                  it represents spot in use.\
                                                  When `instType` is
                                                  `SWAP`/`FUTURES`/`OPTION`,
                                                  it represents position
                                                  amount.

  \> posSide              String                  Position side\
                                                  `long`\
                                                  `short`\
                                                  `net`

  \> avgPx                String                  Average open price

  \> markPxBf             String                  Mark price before price
                                                  volatility\
                                                  Return \"\" if users don\'t
                                                  pass in idxVol

  \> markPx               String                  Mark price

  \> floatPnl             String                  Float P&L

  \> imrBf                String                  IMR before price volatility

  \> imr                  String                  IMR

  \> mgnRatio             String                  Maintenance margin ratio

  \> lever                String                  Leverage

  \> notionalUsd          String                  Notional in `USD`

  \> isRealPos            Boolean                 Whether it is a real
                                                  position\
                                                  If `instType` is
                                                  `SWAP`/`FUTURES`/`OPTION`,
                                                  it is a valid parameter,
                                                  else it will return `false`
  ----------------------------------------------------------------------------

### Position builder trend graph {#trading-account-rest-api-position-builder-trend-graph}

#### Rate limit: 1 request per 5 seconds {#trading-account-rest-api-position-builder-trend-graph-rate-limit-1-request-per-5-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-position-builder-trend-graph-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-position-builder-trend-graph-permission-read}

#### HTTP Request {#trading-account-rest-api-position-builder-trend-graph-http-request}

`POST /api/v5/account/position-builder-graph`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
{
   "inclRealPosAndEq":false,
   "simPos":[
      {
         "pos":"-10",
         "instId":"BTC-USDT-SWAP",
         "avgPx":"100000"
      },
      {
         "pos":"10",
         "instId":"LTC-USDT-SWAP",
         "avgPx":"8000"
      }
   ],
   "simAsset":[
      {
         "ccy":"USDT",
         "amt":"100"
      }
   ],
   "greeksType":"CASH",
   "type":"mmr",
   "mmrConfig":{
      "acctLv":"3",
      "lever":"1"
   }
}
```
:::

#### Request Parameters {#trading-account-rest-api-position-builder-trend-graph-request-parameters}

  ----------------------------------------------------------------------------------
  **Parameter**      **Type**          **Required**      **Description**
  ------------------ ----------------- ----------------- ---------------------------
  inclRealPosAndEq   Boolean           No                Whether to import existing
                                                         positions and assets\
                                                         The default is `true`

  simPos             Array of objects  No                List of simulated positions

  \> instId          String            Yes               Instrument ID, e.g.
                                                         `BTC-USDT-SWAP`\
                                                         Applicable to
                                                         `SWAP`/`FUTURES`/`OPTION`

  \> pos             String            Yes               Quantity of positions

  \> avgPx           String            Yes               Average open price

  \> lever           String            No                leverage\
                                                         Only applicable to
                                                         `Multi-currency margin`\
                                                         The default is `1`\
                                                         If the allowed leverage is
                                                         exceeded, set according to
                                                         the maximum leverage.

  simAsset           Array of objects  No                List of simulated assets\
                                                         When `inclRealPosAndEq` is
                                                         `true`, only real assets
                                                         are considered and virtual
                                                         assets are ignored

  \> ccy             String            Yes               Currency, e.g. `BTC`

  \> amt             String            Yes               Currency amount

  type               String            Yes               Trending graph type\
                                                         `mmr`

  mmrConfig          Object            Yes               MMR configuration

  \> acctLv          String            No                Switch to account mode\
                                                         `3`: Multi-currency margin\
                                                         `4`: Portfolio margin

  \> lever           String            No                Cross margin leverage in
                                                         Multi-currency margin mode,
                                                         the default is `1`.\
                                                         If the allowed leverage is
                                                         exceeded, set according to
                                                         the maximum leverage.\
                                                         Only applicable to
                                                         `Multi-currency margin`
  ----------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
         {
            "type": "mmr",
            "mmrData": [
               ......
               {
                     "mmr": "1415.0254039225917",
                     "mmrRatio": "-47.45603627655477",
                     "shockFactor": "-0.94"
               },
               {
                     "mmr": "1417.732491243024",
                     "mmrRatio": "-47.436684685735386",
                     "shockFactor": "-0.93"
               }
               ......
            ]
         }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-position-builder-trend-graph-response-parameters}

  -----------------------------------------------------------------------
  **Parameters**          **Types**               **Description**
  ----------------------- ----------------------- -----------------------
  type                    String                  Graph type\
                                                  `mmr`

  mmrData                 Array                   Array of mmrData\
                                                  Return data in
                                                  shockFactor ascending
                                                  order

  \> shockFactor          String                  Price change ratio,
                                                  data range -1 to 1.

  \> mmr                  String                  Mmr at specific price

  \> mmrRatio             String                  Maintenance margin
                                                  ratio at specific price
  -----------------------------------------------------------------------

### Set risk offset amount {#trading-account-rest-api-set-risk-offset-amount}

Set risk offset amount. This does not represent the actual spot risk
offset amount. Only applicable to Portfolio Margin Mode.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-set-risk-offset-amount-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-risk-offset-amount-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-risk-offset-amount-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-risk-offset-amount-http-request}

`POST /api/v5/account/set-riskOffset-amt`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Set spot risk offset amount
POST /api/v5/account/set-riskOffset-amt
body
{
   "ccy": "BTC",
   "clSpotInUseAmt": "0.5"
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-risk-offset-amount-request-parameters}

  Parameter        Type     Required   Description
  ---------------- -------- ---------- ------------------------------------------
  ccy              String   Yes        Currency
  clSpotInUseAmt   String   Yes        Spot risk offset amount defined by users

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
   "code": "0",
   "msg": "",
   "data": [
      {
         "ccy": "BTC",
         "clSpotInUseAmt": "0.5"
      }
   ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-risk-offset-amount-response-parameters}

  Parameters       Types    Description
  ---------------- -------- ------------------------------------------
  ccy              String   Currency
  clSpotInUseAmt   String   Spot risk offset amount defined by users

### Get Greeks {#trading-account-rest-api-get-greeks}

Retrieve a greeks list of all assets in the account.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-greeks-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-greeks-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-greeks-permission-read}

#### HTTP Request {#trading-account-rest-api-get-greeks-http-request}

`GET /api/v5/account/greeks`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Get the greeks of all assets in the account
GET /api/v5/account/greeks

# Get the greeks of BTC assets in the account
GET /api/v5/account/greeks?ccy=BTC
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Retrieve a greeks list of all assets in the account
result = accountAPI.get_greeks()
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-greeks-request-parameters}

  **Parameters**   **Types**   **Required**   **Description**
  ---------------- ----------- -------------- ------------------------------
  ccy              String      No             Single currency, e.g. `BTC`.

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "data":[
        {
           "thetaBS": "",
           "thetaPA":"",
           "deltaBS":"",
           "deltaPA":"",
           "gammaBS":"",
           "gammaPA":"",
           "vegaBS":"",
           "vegaPA":"",
           "ccy":"BTC",
           "ts":"1620282889345"
        }
    ],
    "msg":""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-greeks-response-parameters}

  **Parameters**   **Types**   **Description**
  ---------------- ----------- -----------------------------------------------------------------------------------
  deltaBS          String      delta: Black-Scholes Greeks in dollars
  deltaPA          String      delta: Greeks in coins
  gammaBS          String      gamma: Black-Scholes Greeks in dollars, only applicable to OPTION
  gammaPA          String      gamma: Greeks in coins, only applicable to OPTION
  thetaBS          String      theta: Black-Scholes Greeks in dollars, only applicable to `OPTION`
  thetaPA          String      theta: Greeks in coins, only applicable to `OPTION`
  vegaBS           String      vega: Black-Scholes Greeks in dollars, only applicable to `OPTION`
  vegaPA           String      vega：Greeks in coins, only applicable to `OPTION`
  ccy              String      Currency
  ts               String      Time of getting Greeks, Unix timestamp format in milliseconds, e.g. 1597026383085

### Get PM position limitation {#trading-account-rest-api-get-pm-position-limitation}

Retrieve cross position limitation of SWAP/FUTURES/OPTION under
Portfolio margin mode.

#### Rate Limit: 10 requests per 2 seconds {#trading-account-rest-api-get-pm-position-limitation-rate-limit-10-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-pm-position-limitation-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-pm-position-limitation-permission-read}

#### HTTP Request {#trading-account-rest-api-get-pm-position-limitation-http-request}

`GET /api/v5/account/position-tiers`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Query limitation of BTC-USDT
GET /api/v5/account/position-tiers?instType=SWAP&uly=BTC-USDT
```
:::

::: highlight
``` {.highlight .python .tab-python}
import okx.Account as Account

# API initialization
apikey = "YOUR_API_KEY"
secretkey = "YOUR_SECRET_KEY"
passphrase = "YOUR_PASSPHRASE"

flag = "1"  # Production trading:0 , demo trading:1

accountAPI = Account.AccountAPI(apikey, secretkey, passphrase, False, flag)

# Get PM position limitation
result = accountAPI.get_account_position_tiers(
    instType="SWAP",
    uly="BTC-USDT"
)
print(result)
```
:::

#### Request Parameters {#trading-account-rest-api-get-pm-position-limitation-request-parameters}

  -----------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- -----------------
  instType          String            Yes               Instrument type\
                                                        `SWAP`\
                                                        `FUTURES`\
                                                        `OPTION`

  instFamily        String            Yes               Single instrument
                                                        family or
                                                        instrument
                                                        families (no more
                                                        than 5) separated
                                                        with comma.
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "data": [
    {
      "instFamily": "BTC-USDT",
      "maxSz": "10000",
      "posType": "",
      "uly": "BTC-USDT"
    }
  ],
  "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-pm-position-limitation-response-parameters}

  ---------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- ---------------------------
  uly                     String                  Underlying\
                                                  Applicable to
                                                  `FUTURES`/`SWAP`/`OPTION`

  instFamily              String                  Instrument family\
                                                  Applicable to
                                                  `FUTURES`/`SWAP`/`OPTION`

  maxSz                   String                  Max number of positions

  posType                 String                  Limitation of position
                                                  type, only applicable to
                                                  cross `OPTION` under
                                                  portfolio margin mode\
                                                  `1`: Contracts of pending
                                                  orders and open positions
                                                  for all derivatives
                                                  instruments. `2`: Contracts
                                                  of pending orders for all
                                                  derivatives instruments.
                                                  `3`: Pending orders for all
                                                  derivatives instruments.
                                                  `4`: Contracts of pending
                                                  orders and open positions
                                                  for all derivatives
                                                  instruments on the same
                                                  side. `5`: Pending orders
                                                  for one derivatives
                                                  instrument. `6`: Contracts
                                                  of pending orders and open
                                                  positions for one
                                                  derivatives instrument.
                                                  `7`: Contracts of one
                                                  pending order.
  ---------------------------------------------------------------------------

### Activate option {#trading-account-rest-api-activate-option}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-activate-option-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-activate-option-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-activate-option-permission-trade}

#### HTTP Request {#trading-account-rest-api-activate-option-http-request}

`POST /api/v5/account/activate-option`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/activate-option
```
:::

#### Request Parameters {#trading-account-rest-api-activate-option-request-parameters}

None

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "ts": "1600000000000"
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-activate-option-response-parameters}

  Parameter   Type     Description
  ----------- -------- -----------------
  ts          String   Activation time

### Set auto loan {#trading-account-rest-api-set-auto-loan}

Only applicable to `Multi-currency margin` and `Portfolio margin`

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-auto-loan-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-auto-loan-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-auto-loan-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-auto-loan-http-request}

`POST /api/v5/account/set-auto-loan`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-auto-loan
body
{
    "autoLoan":true,
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-auto-loan-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  autoLoan          Boolean           No                Whether to
                                                        automatically
                                                        make loans\
                                                        Valid values are
                                                        `true`, `false`\
                                                        The default is
                                                        `true`

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [{
        "autoLoan": true
    }]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-auto-loan-response-parameters}

  Parameter   Type      Description
  ----------- --------- -------------------------------------
  autoLoan    Boolean   Whether to automatically make loans

### Preset account mode switch {#trading-account-rest-api-preset-account-mode-switch}

Pre-set the required information for account mode switching. When
switching from `Portfolio margin mode` back to `Futures mode` /
`Multi-currency margin mode`, and if there are existing cross-margin
contract positions, it is mandatory to pre-set leverage.

If the user does not follow the required settings, they will receive an
error message during the pre-check or when setting the account mode.

#### Rate limit: 5 requests per 2 seconds {#trading-account-rest-api-preset-account-mode-switch-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-preset-account-mode-switch-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-preset-account-mode-switch-permission-trade}

#### HTTP Request {#trading-account-rest-api-preset-account-mode-switch-http-request}

`POST /api/v5/account/account-level-switch-preset`

> Request example

::: highlight
``` {.highlight .shell .tab-shell}
# 1. Futures mode -> Multi-currency margin mode
POST /api/v5/account/account-level-switch-preset
{
    "acctLv": "3"
}

# 2. Multi-currency margin mode -> Futures mode
POST /api/v5/account/account-level-switch-preset
{
    "acctLv": "2"
}

# 3. Portfolio margin mode -> Futures mode/Multi-currency margin mode, the user have cross-margin contract position and lever is required
POST /api/v5/account/account-level-switch-preset
{
    "acctLv": "2",
    "lever": "10"
}

# 4. Portfolio margin mode -> Futures mode/Multi-currency margin mode, the user doesn't have cross-margin contract position and lever is not required
POST /api/v5/account/account-level-switch-preset
{
    "acctLv": "3"
}
```
:::

#### Request parameters {#trading-account-rest-api-preset-account-mode-switch-request-parameters}

  -------------------------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- -------------------------------
  acctLv            String            Yes               Account mode\
                                                        `2`: Futures mode\
                                                        `3`: Multi-currency margin
                                                        code\
                                                        `4`: Portfolio margin mode

  lever             String            Optional          Leverage\
                                                        Required when switching from
                                                        Portfolio margin mode to
                                                        `Futures mode` or
                                                        `Multi-currency margin mode`,
                                                        and the user holds cross-margin
                                                        positions.

  riskOffsetType    String            Optional          ~~Risk offset type\
                                                        `1`: Spot-derivatives (USDT)
                                                        risk offset\
                                                        `2`: Spot-derivatives (Crypto)
                                                        risk offset\
                                                        `3`: Derivatives only mode\
                                                        `4`: Spot-derivatives (USDC)
                                                        risk offset\
                                                        Applicable when switching from
                                                        Futures mode or Multi-currency
                                                        margin mode to Portfolio margin
                                                        mode.~~(Deprecated)
  -------------------------------------------------------------------------------------

> Response example 1. Futures mode -\> Multi-currency margin mode

::: highlight
``` {.highlight .json .tab-json}
{
    "acctLv": "3",
    "curAcctLv": "2",
    "lever": "",
    "riskOffsetType": ""
}
```
:::

> Response example 2. Multi-currency margin mode -\> Futures mode

::: highlight
``` {.highlight .json .tab-json}
{
    "acctLv": "2",
    "curAcctLv": "3",
    "lever": "",
    "riskOffsetType": ""
}
```
:::

> Response example 3. Portfolio margin mode -\> Futures
> mode/Multi-currency margin mode

::: highlight
``` {.highlight .json .tab-json}
{
    "acctLv": "2",
    "curAcctLv": "4",
    "lever": "10",
    "riskOffsetType": ""
}
```
:::

> Response example 4. Portfolio margin mode -\> Futures
> mode/Multi-currency margin mode

::: highlight
``` {.highlight .json .tab-json}
{
    "acctLv": "3",
    "curAcctLv": "4",
    "lever": "",
    "riskOffsetType": ""
}
```
:::

#### Response parameters {#trading-account-rest-api-preset-account-mode-switch-response-parameters}

  **Parameter**    **Type**   **Description**
  ---------------- ---------- -----------------------------------------------------
  curAcctLv        String     Current account mode
  acctLv           String     Account mode after switch
  lever            String     The leverage user preset for cross-margin positions
  riskOffsetType   String     ~~The risk offset type user preset~~(Deprecated)

\
lever: When switching from Portfolio margin mode to Futures mode or
Multi-currency margin mode, if the user holds cross-margin positions,
this parameter must be provided; otherwise, error code 50014 will occur.
The maximum allowable value for this parameter is determined by the
smallest maximum leverage based on current position sizes under the
target mode. For example, if a user in PM mode holds three cross-margin
positions, with maximum allowable leverage of 20x, 50x, and 100x
respectively, the maximum leverage it can set is 20x.

### Precheck account mode switch {#trading-account-rest-api-precheck-account-mode-switch}

Retrieve precheck information for account mode switching.

#### Rate limit: 5 requests per 2 seconds {#trading-account-rest-api-precheck-account-mode-switch-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-precheck-account-mode-switch-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-precheck-account-mode-switch-permission-read}

#### HTTP Request {#trading-account-rest-api-precheck-account-mode-switch-http-request}

`GET /api/v5/account/set-account-switch-precheck`

> Request example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/set-account-switch-precheck?acctLv=3
```
:::

#### Request parameters {#trading-account-rest-api-precheck-account-mode-switch-request-parameters}

  -----------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- -----------------
  acctLv            String            Yes               Account mode\
                                                        `1`: Spot mode\
                                                        `2`: Futures
                                                        mode\
                                                        `3`:
                                                        Multi-currency
                                                        margin code\
                                                        `4`: Portfolio
                                                        margin mode

  -----------------------------------------------------------------------

> Response example. Futures mode-\>Portfolio margin mode, need to finish
> the Q&A on web or mobile first

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "51070",
    "data": [],
    "msg": "You do not meet the requirements for switching to this account mode. Please upgrade the account mode on the OKX website or App"
}
```
:::

> Response example. Futures mode-\>Portfolio margin mode, unmatched
> information. sCode 1

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLv": "3",
            "curAcctLv": "1",
            "mgnAft": null,
            "mgnBf": null,
            "posList": [],
            "posTierCheck": [],
            "riskOffsetType": "",
            "sCode": "1",
            "unmatchedInfoCheck": [
                {
                    "posList": [],
                    "totalAsset": "",
                    "type": "repay_borrowings"
                }
            ]
        }
    ],
    "msg": ""
}
```
:::

> Response example. Portfolio margin mode-\>Multi-currency margin code,
> the user has cross-margin positions but doesn\'t preset leverage.
> sCode 3

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLv": "3",
            "curAcctLv": "4",
            "mgnAft": null,
            "mgnBf": null,
            "posList": [
                {
                    "lever": "50",
                    "posId": "2005456500916518912"
                },
                {
                    "lever": "10",
                    "posId": "2005456108363218944"
                },
                {
                    "lever": "100",
                    "posId": "2005456332909477888"
                },
                {
                    "lever": "1",
                    "posId": "2005456415990251520"
                }
            ],
            "posTierCheck": [],
            "riskOffsetType": "",
            "sCode": "3",
            "unmatchedInfoCheck": []
        }
    ],
    "msg": ""
}
```
:::

> Response example. Portfolio margin mode-\>Multi-currency margin code,
> the user finishes the leverage setting to 10, and passes the position
> tier an margin check. sCode 0.

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLv": "3",
            "curAcctLv": "4",
            "mgnAft": {
                "acctAvailEq": "106002.2061970689",
                "details": [],
                "mgnRatio": "148.1652396878421"
            },
            "mgnBf": {
                "acctAvailEq": "77308.89735228613",
                "details": [],
                "mgnRatio": "4.460069474634038"
            },
            "posList": [
                {
                    "lever": "50",
                    "posId": "2005456500916518912"
                },
                {
                    "lever": "50",
                    "posId": "2005456108363218944"
                },
                {
                    "lever": "50",
                    "posId": "2005456332909477888"
                },
                {
                    "lever": "50",
                    "posId": "2005456415990251520"
                }
            ],
            "posTierCheck": [],
            "riskOffsetType": "",
            "sCode": "0",
            "unmatchedInfoCheck": []
        }
    ],
    "msg": ""
}
```
:::

#### Response parameters {#trading-account-rest-api-precheck-account-mode-switch-response-parameters}

  --------------------------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- --------------------------------------
  sCode                   String                  Check code\
                                                  `0`: pass all checks\
                                                  `1`: unmatched information\
                                                  `3`: leverage setting is not finished\
                                                  `4`: position tier or margin check is
                                                  not passed

  curAcctLv               String                  Account mode\
                                                  `1`: Spot mode\
                                                  `2`: Futures mode\
                                                  `3`: Multi-currency margin code\
                                                  `4`: Portfolio margin mode\
                                                  Applicable to all scenarios

  acctLv                  String                  Account mode\
                                                  `1`: Spot mode\
                                                  `2`: Futures mode\
                                                  `3`: Multi-currency margin code\
                                                  `4`: Portfolio margin mode\
                                                  Applicable to all scenarios

  riskOffsetType          String                  ~~Risk offset type\
                                                  `1`: Spot-derivatives (USDT) risk
                                                  offset\
                                                  `2`: Spot-derivatives (Crypto) risk
                                                  offset\
                                                  `3`: Derivatives only mode\
                                                  `4`: Spot-derivatives (USDC) risk
                                                  offset\
                                                  Applicable when acctLv is `4`, return
                                                  \"\" for other scenarios\
                                                  If the user preset before, it will use
                                                  the user\'s specified value; if not,
                                                  the default value `3` will be
                                                  applied~~(Deprecated)

  unmatchedInfoCheck      Array of objects        Unmatched information list\
                                                  Applicable when sCode is `1`,
                                                  indicating there is unmatched
                                                  information; return \[\] for other
                                                  scenarios

  \>\> type               String                  Unmatched information type\
                                                  `asset_validation`: asset validation\
                                                  `pending_orders`: order book pending
                                                  orders\
                                                  `pending_algos`: pending algo orders
                                                  and trading bots, such as iceberg,
                                                  recurring buy and twap\
                                                  `isolated_margin`: isolated margin
                                                  (quick margin and manual transfers)\
                                                  `isolated_contract`: isolated contract
                                                  (manual transfers)\
                                                  `contract_long_short`: contract
                                                  positions in hedge mode\
                                                  `cross_margin`: cross margin
                                                  positions\
                                                  `cross_option_buyer`: cross options
                                                  buyer\
                                                  `isolated_option`: isolated options
                                                  (only applicable to spot mode)\
                                                  `growth_fund`: positions with trial
                                                  funds\
                                                  `all_positions`: all positions\
                                                  `spot_lead_copy_only_simple_single`:
                                                  copy trader and customize lead trader
                                                  can only use spot mode or Futures
                                                  mode\
                                                  `stop_spot_custom`: spot customize
                                                  copy trading\
                                                  `stop_futures_custom`: contract
                                                  customize copy trading\
                                                  `lead_portfolio`: lead trader can not
                                                  switch to portfolio margin mode\
                                                  `futures_smart_sync`: you can not
                                                  switch to spot mode when having smart
                                                  contract sync\
                                                  `vip_fixed_loan`: vip loan\
                                                  `repay_borrowings`: borrowings\
                                                  `compliance_restriction`: due to
                                                  compliance restrictions, margin
                                                  trading services are unavailable\
                                                  `compliance_kyc2`: Due to compliance
                                                  restrictions, margin trading services
                                                  are unavailable. If you are not a
                                                  resident of this region, please
                                                  complete kyc2 identity verification.

  \>\> totalAsset         String                  Total assets\
                                                  Only applicable when type is
                                                  `asset_validation`, return \"\" for
                                                  other scenarios

  \>\> posList            Array of strings        Unmatched position list (posId)\
                                                  Applicable when type is related to
                                                  positions, return \[\] for other
                                                  scenarios

  posList                 Array of objects        Cross margin contract position list\
                                                  Applicable when curAcctLv is `4`,
                                                  acctLv is `2/3` and user has cross
                                                  margin contract positions\
                                                  Applicable when sCode is `0/3/4`

  \> posId                String                  Position ID

  \> lever                String                  Leverage of cross margin contract
                                                  positions after switch

  posTierCheck            Array of objects        Cross margin contract positions that
                                                  don\'t pass the position tier check\
                                                  Only applicable when sCode is `4`

  \> instFamily           String                  Instrument family

  \> instType             String                  Instrument type\
                                                  `SWAP`\
                                                  `FUTURES`\
                                                  `OPTION`

  \> pos                  String                  Quantity of position

  \> lever                String                  Leverage

  \> maxSz                String                  If acctLv is `2/3`, it refers to the
                                                  maximum position size allowed at the
                                                  current leverage. If acctLv is `4`, it
                                                  refers to the maximum position limit
                                                  for cross-margin positions under the
                                                  PM mode.

  mgnBf                   Object                  The margin related information before
                                                  switching account mode\
                                                  Applicable when sCode is `0/4`, return
                                                  null for other scenarios

  \> acctAvailEq          String                  Account available equity in USD\
                                                  Applicable when curAcctLv is `3/4`,
                                                  return \"\" for other scenarios

  \> mgnRatio             String                  Maintenance Margin ratio in USD\
                                                  Applicable when curAcctLv is `3/4`,
                                                  return \"\" for other scenarios

  \> details              Array of objects        Detailed information\
                                                  Only applicable when curAcctLv is `2`,
                                                  return \"\" for other scenarios

  \>\> ccy                String                  Currency

  \>\> availEq            String                  Available equity of currency

  \>\> mgnRatio           String                  Maintenance margin ratio of currency

  mgnAft                  Object                  The margin related information after
                                                  switching account mode\
                                                  Applicable when sCode is `0/4`, return
                                                  null for other scenarios

  \> acctAvailEq          String                  Account available equity in USD\
                                                  Applicable when acctLv is `3/4`,
                                                  return \"\" for other scenarios

  \> mgnRatio             String                  Maintenance margin ratio in USD\
                                                  Applicable when acctLv is `3/4`,
                                                  return \"\" for other scenarios

  \> details              Array of objects        Detailed information\
                                                  Only applicable when acctLv is `2`,
                                                  return \"\" for other scenarios

  \>\> ccy                String                  Currency

  \>\> availEq            String                  Available equity of currency

  \>\> mgnRatio           String                  Maintenance margin ratio of currency
  --------------------------------------------------------------------------------------

### Set account mode {#trading-account-rest-api-set-account-mode}

You need to set on the Web/App for the first set of every account mode.
If users plan to switch account modes while holding positions, they
should first call the preset endpoint to conduct necessary settings,
then call the precheck endpoint to get unmatched information, margin
check, and other related information, and finally call the account mode
switch endpoint to switch account modes.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-account-mode-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-account-mode-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-account-mode-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-account-mode-http-request}

`POST /api/v5/account/set-account-level`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-account-level
body
{
    "acctLv":"1"
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-account-mode-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  acctLv            String            Yes               Account mode\
                                                        `1`: Spot mode\
                                                        `2`: Futures
                                                        mode\
                                                        `3`:
                                                        Multi-currency
                                                        margin code\
                                                        `4`: Portfolio
                                                        margin mode

  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "data": [
        {
            "acctLv": "1"
        }
    ],
    "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-account-mode-response-parameters}

  Parameter   Type     Description
  ----------- -------- --------------
  acctLv      String   Account mode

### Set collateral assets {#trading-account-rest-api-set-collateral-assets}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-set-collateral-assets-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-collateral-assets-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-collateral-assets-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-collateral-assets-http-request}

`POST /api/v5/account/set-collateral-assets`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
# Set all assets to be collateral
POST /api/v5/account/set-collateral-assets
body
{
    "type":"all",
    "collateralEnabled":true
}


# Set custom assets to be non-collateral
POST /api/v5/account/set-collateral-assets
body
{
    "type":"custom",
    "ccyList":["BTC","ETH"],
    "collateralEnabled":false
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-collateral-assets-request-parameters}

  ------------------------------------------------------------------------------
  Parameter           Type              Required          Description
  ------------------- ----------------- ----------------- ----------------------
  type                String            true              Type\
                                                          `all`\
                                                          `custom`

  collateralEnabled   Boolean           true              Whether or not set the
                                                          assets to be
                                                          collateral\
                                                          `true`: Set to be
                                                          collateral\
                                                          `false`: Set to be
                                                          non-collateral

  ccyList             Array of strings  conditional       Currency list, e.g.
                                                          \[\"BTC\",\"ETH\"\]\
                                                          If type=`custom`, the
                                                          parameter is required.
  ------------------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data" :[
      {
        "type":"all",
        "ccyList":["BTC","ETH"],
        "collateralEnabled":false
      }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-collateral-assets-response-parameters}

  -----------------------------------------------------------------------
  Parameter               Type                    Description
  ----------------------- ----------------------- -----------------------
  type                    String                  Type\
                                                  `all`\
                                                  `custom`

  collateralEnabled       Boolean                 Whether or not set the
                                                  assets to be
                                                  collateral\
                                                  `true`: Set to be
                                                  collateral\
                                                  `false`: Set to be
                                                  non-collateral

  ccyList                 Array of strings        Currency list, e.g.
                                                  \[\"BTC\",\"ETH\"\]
  -----------------------------------------------------------------------

### Get collateral assets {#trading-account-rest-api-get-collateral-assets}

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-collateral-assets-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-collateral-assets-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-collateral-assets-permission-read}

#### HTTP Request {#trading-account-rest-api-get-collateral-assets-http-request}

`GET /api/v5/account/collateral-assets`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/collateral-assets
```
:::

#### Request Parameters {#trading-account-rest-api-get-collateral-assets-request-parameters}

  **Parameters**      **Types**   **Required**   **Description**
  ------------------- ----------- -------------- -------------------------------------------------------------------------------------------------------------
  ccy                 String      No             Single currency or multiple currencies (no more than 20) separated with comma, e.g. \"BTC\" or \"BTC,ETH\".
  collateralEnabled   Boolean     No             Whether or not to be a collateral asset

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data" :[
          {
            "ccy":"BTC",
            "collateralEnabled": true
          },
          {
            "ccy":"ETH",
            "collateralEnabled": false
          }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-collateral-assets-response-parameters}

  **Parameter**       **Type**   **Description**
  ------------------- ---------- -----------------------------------------
  ccy                 String     Currency, e.g. `BTC`
  collateralEnabled   Boolean    Whether or not to be a collateral asset

### Reset MMP Status {#trading-account-rest-api-reset-mmp-status}

You can unfreeze by this endpoint once MMP is triggered.\

Only applicable to Option in Portfolio Margin mode, and MMP privilege is
required.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-reset-mmp-status-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-reset-mmp-status-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-reset-mmp-status-permission-trade}

#### HTTP Request {#trading-account-rest-api-reset-mmp-status-http-request}

`POST /api/v5/account/mmp-reset`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/mmp-reset
body
{
    "instType":"OPTION",
    "instFamily":"BTC-USD"
}
```
:::

#### Request Parameters {#trading-account-rest-api-reset-mmp-status-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instType          String            No                Instrument type\
                                                        `OPTION`\
                                                        The default is
                                                        \`OPTION

  instFamily        String            Yes               Instrument family
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

#### Response Parameters {#trading-account-rest-api-reset-mmp-status-response-parameters}

  Parameter   Type      Description
  ----------- --------- ---------------------------------------
  result      Boolean   Result of the request `true`, `false`

### Set MMP {#trading-account-rest-api-set-mmp}

This endpoint is used to set MMP configure\

Only applicable to Option in Portfolio Margin mode, and MMP privilege is
required.

\
What is MMP?\
Market Maker Protection (MMP) is an automated mechanism for market
makers to pull their quotes when their executions exceed a certain
threshold(\`qtyLimit\`) within a certain time frame(\`timeInterval\`).
Once mmp is triggered, any pre-existing mmp pending orders(\`mmp\` and
\`mmp_and_post_only\` orders) will be automatically canceled, and new
orders tagged as MMP will be rejected for a specific
duration(\`frozenInterval\`), or until manual reset by makers.\
\
How to enable MMP?\
Please send an email to institutional@okx.com or contact your business
development (BD) manager to apply for MMP. The initial threshold will be
upon your request.

#### Rate Limit: 2 requests per 10 seconds {#trading-account-rest-api-set-mmp-rate-limit-2-requests-per-10-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-mmp-rate-limit-rule-user-id}

#### Permission: Trade {#trading-account-rest-api-set-mmp-permission-trade}

#### HTTP Request {#trading-account-rest-api-set-mmp-http-request}

`POST /api/v5/account/mmp-config`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/mmp-config
body
{
    "instFamily":"BTC-USD",
    "timeInterval":"5000",
    "frozenInterval":"2000",
    "qtyLimit": "100"
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-mmp-request-parameters}

  -----------------------------------------------------------------------
  Parameter         Type              Required          Description
  ----------------- ----------------- ----------------- -----------------
  instFamily        String            Yes               Instrument family

  timeInterval      String            Yes               Time window (ms).
                                                        MMP interval
                                                        where monitoring
                                                        is done\
                                                        \"0\" means
                                                        disable MMP

  frozenInterval    String            Yes               Frozen period
                                                        (ms).\
                                                        \"0\" means the
                                                        trade will remain
                                                        frozen until you
                                                        request \"Reset
                                                        MMP Status\" to
                                                        unfrozen

  qtyLimit          String            Yes               Trade qty limit
                                                        in number of
                                                        contracts\
                                                        Must be \> 0
  -----------------------------------------------------------------------

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "msg": "",
  "data": [
    {
        "frozenInterval":"2000",
        "instFamily":"BTC-USD",
        "qtyLimit": "100",
        "timeInterval":"5000"
    }
  ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-mmp-response-parameters}

  Parameter        Type     Description
  ---------------- -------- ---------------------------------------------------------
  instFamily       String   Instrument family
  timeInterval     String   Time window (ms). MMP interval where monitoring is done
  frozenInterval   String   Frozen period (ms).
  qtyLimit         String   Trade qty limit in number of contracts

### GET MMP Config {#trading-account-rest-api-get-mmp-config}

This endpoint is used to get MMP configure information\

Only applicable to Option in Portfolio Margin mode, and MMP privilege is
required.

#### Rate Limit: 5 requests per 2 seconds {#trading-account-rest-api-get-mmp-config-rate-limit-5-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-get-mmp-config-rate-limit-rule-user-id}

#### Permission: Read {#trading-account-rest-api-get-mmp-config-permission-read}

#### HTTP Request {#trading-account-rest-api-get-mmp-config-http-request}

`GET /api/v5/account/mmp-config`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
GET /api/v5/account/mmp-config?instFamily=BTC-USD
```
:::

#### Request Parameters {#trading-account-rest-api-get-mmp-config-request-parameters}

  Parameter    Type     Required   Description
  ------------ -------- ---------- -------------------
  instFamily   String   No         Instrument Family

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
  "code": "0",
  "data": [
    {
      "frozenInterval": "2000",
      "instFamily": "ETH-USD",
      "mmpFrozen": true,
      "mmpFrozenUntil": "1000",
      "qtyLimit": "10",
      "timeInterval": "5000"
    }
  ],
  "msg": ""
}
```
:::

#### Response Parameters {#trading-account-rest-api-get-mmp-config-response-parameters}

  **Parameter**    **Type**   **Description**
  ---------------- ---------- ----------------------------------------------------------------------------------------------------------------------------------------
  instFamily       String     Instrument Family
  mmpFrozen        Boolean    Whether MMP is currently triggered. `true` or `false`
  mmpFrozenUntil   String     If frozenInterval is configured and mmpFrozen = True, it is the time interval (in ms) when MMP is no longer triggered, otherwise \"\".
  timeInterval     String     Time window (ms). MMP interval where monitoring is done
  frozenInterval   String     Frozen period (ms). If it is \"0\", the trade will remain frozen until manually reset and `mmpFrozenUntil` will be \"\".
  qtyLimit         String     Trade qty limit in number of contracts

### Move positions {#trading-account-rest-api-move-positions}

Only applicable to users with a trading level greater than or equal to
VIP5, and can only be called through the API Key of the master account.
Users can check their trading level through the fee details table on the
[My trading fees](https://www.okx.com/balance/fee) page.\

To move positions between different accounts under the same master
account. Each source account can trigger up to fifteen move position
requests every 24 hours. There is no limitation to the destination
account to receive positions. Refer to the \"Things to note\" part for
more details.

#### Rate limit: 1 request per second {#trading-account-rest-api-move-positions-rate-limit-1-request-per-second}

#### Rate limit rule: Master account User ID {#trading-account-rest-api-move-positions-rate-limit-rule-master-account-user-id}

#### HTTP Request {#trading-account-rest-api-move-positions-http-request}

`POST /api/v5/account/move-positions`

> Request example

::: highlight
``` {.highlight .shell .tab-shell}
{
   "fromAcct":"0",
   "toAcct":"test",
   "legs":[
      {
         "from":{
            "posId":"2065471111340792832",
            "side":"sell",
            "sz":"1"
         },
         "to":{
            "posSide":"net",
            "tdMode":"cross"
         }
      },
      {
         "from":{
            "posId":"2063111180412153856",
            "side":"sell",
            "sz":"1"
         },
         "to":{
            "posSide":"net",
            "tdMode":"cross"
         }
      }
   ],
   "clientId":"test"
}
```
:::

#### Request parameters {#trading-account-rest-api-move-positions-request-parameters}

  ----------------------------------------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- ----------------------------------------------
  fromAcct          String            Yes               Source account name. If it\'s a master
                                                        account, it should be \"0\"

  toAcct            String            Yes               Destination account name. If it\'s a master
                                                        account, it should be \"0\"

  legs              Array of Objects  Yes               An array of objects containing details of each
                                                        position to be moved

  \>from            Object            yes               Details of the position in the source account

  \>\>posId         String            Yes               Position ID in the source account

  \>\>sz            String            Yes               Number of contracts.

  \>\>side          String            Yes               Trade side from the perspective of source
                                                        account\
                                                        `buy`\
                                                        `sell`

  \>to              Object            Yes               Details of the configuration of the
                                                        destination account

  \>\>tdMode        String            No                Trading mode in the destination account.\
                                                        `cross`\
                                                        `isolated`\
                                                        If not provided, tdMode will take the default
                                                        values as shown below:\
                                                        Buy options in
                                                        `Futures mode`/`Multi-currency margin mode`:
                                                        `isolated`\
                                                        Other cases: `cross`

  \>\>posSide       String            No                Position side\
                                                        `net`\
                                                        `long`\
                                                        `short`\
                                                        This parameter is not mandatory if the
                                                        destination sub-account is in **net** mode. If
                                                        you pass it through, the only valid value is
                                                        `net`.It can only be `long` or `short` if the
                                                        destination sub-account is in long/short mode.
                                                        If not specified, destination account in
                                                        long/short mode always open new positions.

  \>\>ccy           String            No                Margin currency in destination accountOnly
                                                        applicable to cross margin positions in
                                                        `Futures mode`.

  clientId          String            Yes               Client-supplied ID. A combination of
                                                        case-sensitive alphanumerics, all numbers, or
                                                        all letters of up to 32 characters.
  ----------------------------------------------------------------------------------------------------

> Response example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "clientId": "test",
            "blockTdId": "2065832911119076864",
            "state": "filled",
            "ts": "1734069018526",
            "fromAcct": "0",
            "toAcct": "test",
            "legs": [
                {
                    "from": {
                        "posId": "2065471111340792832",
                        "instId": "BTC-USD-SWAP",
                        "px": "100042.7",
                        "side": "sell",
                        "sz": "1",
                        "sCode": "0",
                        "sMsg": ""
                    },
                    "to": {
                        "instId": "BTC-USD-SWAP",
                        "px": "100042.7",
                        "side": "buy",
                        "sz": "1",
                        "tdMode": "cross",
                        "posSide": "net",
                        "ccy": "",
                        "sCode": "0",
                        "sMsg": ""
                    }
                },
                {
                    "from": {
                        "posId": "2063111180412153856",
                        "instId": "BTC-USDT-SWAP",
                        "px": "100008.1",
                        "side": "sell",
                        "sz": "1",
                        "sCode": "0",
                        "sMsg": ""
                    },
                    "to": {
                        "instId": "BTC-USDT-SWAP",
                        "px": "100008.1",
                        "side": "buy",
                        "sz": "1",
                        "tdMode": "cross",
                        "posSide": "net",
                        "ccy": "",
                        "sCode": "0",
                        "sMsg": ""
                    }
                }
            ]
        }
    ]
}
```
:::

> Response example:failure

::: highlight
``` {.highlight .json .tab-json}
// The destination account position mode (net/longShort) is not matched with the posSide field
{
    "code": "51000",
    "msg": "Incorrect type of posSide (leg with Instrument Id [BTC-USD-SWAP])",
    "data": []
}

// The BTC amount in the destination account is not enough to open the position.
{
    "code": "51008",
    "msg": "Order failed. Insufficient BTC margin in account",
    "data": []
}
```
:::

#### Response parameters {#trading-account-rest-api-move-positions-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  code                    String                  The result code, `0`
                                                  means success

  msg                     String                  The error message,
                                                  empty if the code is 0

  blockTdId               String                  Block trade ID

  clientId                String                  Client-supplied ID

  state                   String                  Status of the order
                                                  `filled`, `failed`

  fromAcct                String                  Source account name

  toAcct                  String                  Destination account
                                                  name

  legs                    Array                   An array of objects
                                                  containing details of
                                                  each position to be
                                                  moved

  \>from                  Object                  Object describing the
                                                  \"from\" leg

  \>\>instId              String                  Instrument ID

  \>\>posId               String                  Position ID

  \>\>px                  String                  Transfer price,
                                                  typically a 60-minute
                                                  TWAP of the mark price

  \>\>side                String                  Direction of the leg in
                                                  the source account\
                                                  `buy`\
                                                  `sell`

  \>\>sz                  String                  Number of Contracts

  \>\>sCode               String                  The code of the event
                                                  execution result, 0
                                                  means success

  \>\>sMsg                String                  Rejection message if
                                                  the request is
                                                  unsuccessful

  \>to                    Object                  Object describing the
                                                  \"to\" leg

  \>\>instId              String                  Instrument ID

  \>\> side               String                  Trade side of the trade
                                                  in the destination
                                                  account

  \>\>posSide             String                  Position side of the
                                                  trade in the
                                                  destination account

  \>\>tdMode              String                  Trade mode

  \>\>px                  String                  Transfer price,
                                                  typically a 60-minute
                                                  TWAP of the mark price

  \>\>ccy                 String                  Margin currency

  \>\>sCode               String                  The code of the event
                                                  execution result, 0
                                                  means success

  \>\>sMsg                String                  Rejection message if
                                                  the request is
                                                  unsuccessful

  ts                      String                  Unix timestamp in
                                                  milliseconds indicating
                                                  when the transfer
                                                  request was processed
  -----------------------------------------------------------------------

#### Things to note {#trading-account-rest-api-move-positions-things-to-note}

1.  Only applicable to users with a trading level greater than or equal
    to VIP5, and can only be called through the API Key of the master
    account.
2.  The source and destination accounts for move positions must be
    accounts under the same master account and they must be different.
3.  For source account, a maximum of fifteen move position requests can
    be triggered within a 24-hour period. There is no limitation to the
    destination account to receive positions. Only successful requests
    are counted toward this limit.
4.  The maximum number of legs per move position request is 30.
5.  No move position fee will be charged at this time.
6.  Moving positions is not supported in margin trading now.
7.  The move position price is determined by the TWAP (Time-Weighted
    Average Price) of the mark price over the past 60 minutes, using the
    closing mark price per minute. If the symbol is newly listed and a
    60-minute TWAP is unavailable, the move position will be rejected
    with error code 70065
8.  The move position will share the same price limit as those in the
    order book. The move position will fail if the 60-minute mark price
    TWAP is outside of the price limit.
9.  For the source account, move positions must be conducted in a
    reduce-only manner. You must choose the opposite side of your
    current position and specify a size equal to or smaller than your
    existing position size. The system will also process move position
    requests in a best-effort reduce-only manner.
10. The side field of source account leg (from) should be `sell` if you
    are holding a long position while the side of destination account
    leg (to) should be `buy`, vice versa for a short position.
11. The posSide field of destination account (to) should be `net` if
    it\'s in one-way mode; `long`/`short` if it\'s in hedge mode. If in
    hedge mode, you need to specify `long`/`short` to decide whether to
    close current positions or open reverse positions. Otherwise, it
    will always open new positions.
    1.  Open long: buy and open long (side: buy; posSide: long)
    2.  Open short: sell and open short (side: sell; posSide: short)
    3.  Close long: sell and close long (side: sell; posSide: long)
    4.  Close short: buy and close short (side: buy; posSide: short)
12. Historical records of move positions can be fetched from the *Get
    move positions history* endpoint but only for pending or successful
    requests.
13. Move positions operation counting example.

  Transfer done within the day   Account A count (total)   Account B count (total)   Account C count (total)   Account D count (total)
  ------------------------------ ------------------------- ------------------------- ------------------------- -------------------------
  Account A to Account B         1                         0                         0                         0
  Account B to Account C         1                         1                         0                         0
  Account B to Account D         1                         2                         0                         0

### Get move positions history {#trading-account-rest-api-get-move-positions-history}

Only applicable to users with a trading level greater than or equal to
VIP5, and can only be called through the API Key of the master account.
Users can check their trading level through the fee details table on the
[My trading fees](https://www.okx.com/balance/fee) page.\

Retrieve move position details in the last 3 days.

#### Rate limit: 2 requests per 2 seconds {#trading-account-rest-api-get-move-positions-history-rate-limit-2-requests-per-2-seconds}

#### Rate limit rule: Master account UserID {#trading-account-rest-api-get-move-positions-history-rate-limit-rule-master-account-userid}

#### HTTP Request {#trading-account-rest-api-get-move-positions-history-http-request}

`GET /api/v5/account/move-positions-history`

> Request example

::: highlight
``` {.highlight .shell .tab-shell}
Get /api/v5/account/move-positions-history
```
:::

#### Request parameters {#trading-account-rest-api-get-move-positions-history-request-parameters}

  **Parameter**   **Type**   **Required**   **Description**
  --------------- ---------- -------------- ------------------------------------------------------------------------------------------------------------------------
  blockTdId       String     No             BlockTdId generated by the system
  clientId        String     No             Client-supplied ID. A combination of case-sensitive alphanumerics, all numbers, or all letters of up to 32 characters.
  beginTs         String     No             Filter with a begin timestamp. Unix timestamp format in milliseconds (inclusive)
  endTs           String     No             Filter with an end timestamp. Unix timestamp format in milliseconds (inclusive)
  limit           String     No             Number of results per request. The maximum and default are both `100`
  state           String     No             Positions transfer state, `filled` `pending`

> Response example

::: highlight
``` {.highlight .json .tab-json}
{
    "code": "0",
    "msg": "",
    "data": [
        {
            "clientId": "test",
            "blockTdId": "2066393411110139648",
            "state": "filled",
            "ts": "1734085725000",
            "fromAcct": "0",
            "toAcct": "test",
            "legs": [
                {
                    "from": {
                        "posId": "2065477911110792832",
                        "instId": "BTC-USD-SWAP",
                        "px": "100123.8",
                        "side": "sell",
                        "sz": "1"
                    },
                    "to": {
                        "instId": "BTC-USD-SWAP",
                        "px": "100123.8",
                        "side": "buy",
                        "sz": "1",
                        "tdMode": "cross",
                        "posSide": "net",
                        "ccy": ""
                    }
                },
                {
                    "from": {
                        "posId": "2063533111112153856",
                        "instId": "BTC-USDT-SWAP",
                        "px": "100078.7",
                        "side": "sell",
                        "sz": "1"
                    },
                    "to": {
                        "instId": "BTC-USDT-SWAP",
                        "px": "100078.7",
                        "side": "buy",
                        "sz": "1",
                        "tdMode": "cross",
                        "posSide": "net",
                        "ccy": ""
                    }
                }
            ]
        }
   ]
}
```
:::

#### Response parameters {#trading-account-rest-api-get-move-positions-history-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  clientId                String                  Client-supplied ID. A
                                                  combination of
                                                  case-sensitive
                                                  alphanumerics, all
                                                  numbers, or all letters
                                                  of up to 32 characters.

  blockTdId               String                  Block trade ID.

  state                   String                  Position transfer
                                                  state, `filled`
                                                  `pending`

  ts                      String                  Unix timestamp in
                                                  milliseconds indicating
                                                  when the transfer
                                                  request was processed

  fromAcct                String                  Source account name

  toAcct                  String                  Destination account
                                                  name

  legs                    Array                   An array of objects
                                                  containing details of
                                                  each position to be
                                                  moved

  \> from                 Object                  Object describing the
                                                  \"from\" leg

  \>\> instId             String                  Instrument ID

  \>\> posId              String                  Position ID

  \>\> px                 String                  Transfer price,
                                                  typically a 60-minute
                                                  TWAP of the mark price

  \>\> side               String                  Direction of the leg in
                                                  the source account\
                                                  `buy`\
                                                  `sell`

  \>\> sz                 String                  Number of Contracts

  \> to                   Object                  Object describing the
                                                  \"to\" leg

  \>\> instId             String                  Instrument ID

  \>\> px                 String                  Transfer price,
                                                  typically a 60-minute
                                                  TWAP of the mark price

  \>\> side               String                  Trade side from the
                                                  perspective of
                                                  destination account\
                                                  `buy`\
                                                  `sell`

  \>\> sz                 String                  Number of contracts.

  \>\> tdMode             String                  Trading mode in the
                                                  destination account\
                                                  `cross`\
                                                  `isolated`

  \>\> posSide            String                  Position side\
                                                  `net`\
                                                  `long`\
                                                  `short`

  \>\> ccy                String                  Margin currency in
                                                  destination account\
                                                  Only applicable to
                                                  cross margin positions
                                                  in `Futures mode`.
  -----------------------------------------------------------------------

### Set auto earn {#trading-account-rest-api-set-auto-earn}

Turn on/off auto earn.

#### Rate limit: 2 requests per 2 seconds {#trading-account-rest-api-set-auto-earn-rate-limit-2-requests-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-auto-earn-rate-limit-rule-user-id}

#### HTTP Request {#trading-account-rest-api-set-auto-earn-http-request}

`POST /api/v5/account/set-auto-earn`

> Request example

::: highlight
``` {.highlight .shell .tab-shell}
// turn on auto lend
{
   "earnType": "0",
   "ccy":"BTC",
   "action":"turn_on"
}
```
:::

#### Request parameters {#trading-account-rest-api-set-auto-earn-request-parameters}

  -------------------------------------------------------------------------
  **Parameter**     **Type**          **Required**      **Description**
  ----------------- ----------------- ----------------- -------------------
  earnType          String            No                Auto earn type\
                                                        `0`: auto earn
                                                        (auto lend, auto
                                                        staking)\
                                                        `1`: auto earn
                                                        (USDG earn)\
                                                        The default value
                                                        is `0`

  ccy               String            Yes               Currency

  action            String            Yes               Auto earn operation
                                                        action\
                                                        `turn_on`: turn on
                                                        auto earn\
                                                        `turn_off`: turn
                                                        off auto earn\
                                                        ~~`amend`: amend
                                                        minimum lending
                                                        APR, applicable
                                                        onlyto earnType
                                                        `0`~~ (deprecated)

  apr               String            Optional          ~~Minimum lending
                                                        APR. Users must
                                                        pass in this field
                                                        when earnType is
                                                        `0` and action is
                                                        `turn_on/amend`.\
                                                        0.01 means 1%,
                                                        available range
                                                        0.01-3.65,
                                                        increment 0.01~~
                                                        (deprecated)
  -------------------------------------------------------------------------

> Response example

::: highlight
``` {.highlight .json .tab-json}
{
   "code":"0",
   "msg":"",
   "data":[
      {
         "earnType": "0",
         "ccy":"BTC",
         "action":"turn_on",
         "apr":"0.01"
      }
   ]
}
```
:::

#### Response parameters {#trading-account-rest-api-set-auto-earn-response-parameters}

  -----------------------------------------------------------------------
  **Parameter**           **Type**                **Description**
  ----------------------- ----------------------- -----------------------
  earnType                String                  Auto earn type\
                                                  `0`: auto earn (auto
                                                  lend, auto staking)\
                                                  `1`: auto earn (USDG
                                                  earn)

  ccy                     String                  Currency

  action                  Boolean                 Auto earn operation
                                                  action\
                                                  `turn_on`\
                                                  `turn_off`\
                                                  ~~`amend`~~
                                                  (deprecated)

  apr                     String                  ~~Minimum lending APR~~
                                                  (deprecated)
  -----------------------------------------------------------------------

### Set settle currency {#trading-account-rest-api-set-settle-currency}

Only applicable to USD-margined contract.

#### Rate limit: 20 times per 2 seconds {#trading-account-rest-api-set-settle-currency-rate-limit-20-times-per-2-seconds}

#### Rate limit rule: User ID {#trading-account-rest-api-set-settle-currency-rate-limit-rule-user-id}

#### Permission: Trading {#trading-account-rest-api-set-settle-currency-permission-trading}

#### HTTP Request {#trading-account-rest-api-set-settle-currency-http-request}

`POST /api/v5/account/set-settle-currency`

> Request Example

::: highlight
``` {.highlight .shell .tab-shell}
POST /api/v5/account/set-settle-currency
body
{
    "settleCcy": "USDC"
}
```
:::

#### Request Parameters {#trading-account-rest-api-set-settle-currency-request-parameters}

  Parameter   Type      Required   Description
  ----------- --------- ---------- ---------------------------------------
  settleCcy   Integer   Yes        USD-margined contract settle currency

> Response Example

::: highlight
``` {.highlight .json .tab-json}
{
    "code":"0",
    "msg":"",
    "data" :[
          {
            "settleCcy":"USDC"
          }
    ]
}
```
:::

#### Response Parameters {#trading-account-rest-api-set-settle-currency-response-parameters}

  Parameter   Type     Description
  ----------- -------- ---------------------------------------
  settleCcy   String   USD-margined contract settle currency
