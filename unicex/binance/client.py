import json
from typing import Literal

from unicex.abstract import BaseAsyncClient, BaseSyncClient
from unicex.types import JsonLike

from .types import FuturesTimeframes, SpotTimeframes


class _BaseBinanceClient:
    """Базовый класс для клиентов Binance API."""

    _BASE_SPOT_URL: str = "https://api.binance.com"
    """Базовый URL для REST API Binance Spot."""

    _BASE_FUTURES_URL: str = "https://fapi.binance.com"
    """Базовый URL для REST API Binance Futures."""


class BinanceClient(BaseSyncClient, _BaseBinanceClient):
    """Клиент для работы с Binance API."""

    def ping(self) -> JsonLike:
        """Проверка подключения к REST API.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#test-connectivity

        Пример ответа:
        ```json
        {}
        ```
        """
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ping")

    def futures_ping(self) -> JsonLike:
        """Проверка подключения к REST API.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api#api-description

        Пример ответа:
        `json
        {}
        ```
        """
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/ping")

    def exchange_info(self) -> JsonLike:
        """Текущие правила биржевой торговли и информация о символах рынка.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints#exchange-information

        Пример ответа:
        ```json
        {
        "timezone": "UTC",
        "serverTime": 1565246363776,
        "rateLimits": [
            {
            // These are defined in the `ENUM definitions` section under `Rate Limiters (rateLimitType)`.
            // All limits are optional
            }
        ],
        "exchangeFilters": [
            // These are the defined filters in the `Filters` section.
            // All filters are optional.
        ],
        "symbols": [
            {
            "symbol": "ETHBTC",
            "status": "TRADING",
            "baseAsset": "ETH",
            "baseAssetPrecision": 8,
            "quoteAsset": "BTC",
            "quotePrecision": 8, // will be removed in future api versions (v4+)
            "quoteAssetPrecision": 8,
            "baseCommissionPrecision": 8,
            "quoteCommissionPrecision": 8,
            "orderTypes": [
                "LIMIT",
                "LIMIT_MAKER",
                "MARKET",
                "STOP_LOSS",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT",
                "TAKE_PROFIT_LIMIT"
            ],
            "icebergAllowed": true,
            "ocoAllowed": true,
            "otoAllowed": true,
            "quoteOrderQtyMarketAllowed": true,
            "allowTrailingStop": false,
            "cancelReplaceAllowed":false,
            "amendAllowed":false,
            "pegInstructionsAllowed": true,
            "isSpotTradingAllowed": true,
            "isMarginTradingAllowed": true,
            "filters": [
                // These are defined in the Filters section.
                // All filters are optional
            ],
            "permissions": [],
            "permissionSets": [
                [
                "SPOT",
                "MARGIN"
                ]
            ],
            "defaultSelfTradePreventionMode": "NONE",
            "allowedSelfTradePreventionModes": [
                "NONE"
            ]
            }
        ],
        // Optional field. Present only when SOR is available.
        // https://github.com/binance/binance-spot-api-docs/blob/master/faqs/sor_faq.md
        "sors": [
            {
            "baseAsset": "BTC",
            "symbols": [
                "BTCUSDT",
                "BTCUSDC"
            ]
            }
        ]
        }
        ```
        """
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/exchangeInfo")

    def futures_exchange_info(self) -> JsonLike:
        """Текущие правила биржевой торговли и информация о символах рынка.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#api-description

        Пример ответа:
        ```json
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
                            "asset": "BTC",
                            "marginAvailable": true, // whether the asset can be used as margin in Multi-Assets mode
                            "autoAssetExchange": "-0.10" // auto-exchange threshold in Multi-Assets margin mode
                    },
                    {
                            "asset": "USDT",
                            "marginAvailable": true,
                            "autoAssetExchange": "0"
                    },
                    {
                            "asset": "BNB",
                            "marginAvailable": false,
                            "autoAssetExchange": null
                    }
            ],
            "symbols": [
                    {
                            "symbol": "BLZUSDT",
                            "pair": "BLZUSDT",
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
                                    "limit": 10
                                    },
                                    {
                                            "filterType": "MIN_NOTIONAL",
                                            "notional": "5.0",
                                    },
                                    {
                                    "filterType": "PERCENT_PRICE",
                                    "multiplierUp": "1.1500",
                                    "multiplierDown": "0.8500",
                                    "multiplierDecimal": "4"
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
        """
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/exchangeInfo")

    def depth(self, symbol: str, limit: int | None = None) -> JsonLike:
        """Книга ордеров.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#order-book

        Пример ответа:
            ```json
            {
            "lastUpdateId": 1027024,
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
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/depth", params=params)

    def futures_depth(self, symbol: str, limit: int | None = None) -> JsonLike:
        """Книга ордеров.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book#request-parameters

        Пример ответа:
        ```json
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
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/depth", params=params)

    def trades(self, symbol: str, limit: int | None = None) -> JsonLike:
        """Последние сделки.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#recent-trades-list

        Пример ответа:
        ```json
        [
          {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "quoteQty": "48.000012",
            "time": 1499865549590,
            "isBuyerMaker": true,
            "isBestMatch": true
          }
        ]
        ```
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/trades", params=params)

    def futures_trades(self, symbol: str, limit: int | None = None) -> JsonLike:
        """Последние сделки.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Recent-Trades-List

        Пример ответа:
        ```json
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
        """
        params = self.filter_params({"symbol": symbol, "limit": limit})
        return self._make_request("GET", self._BASE_FUTURES_URL + "/fapi/v1/trades", params=params)

    def historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> JsonLike:
        """Исторические сделки.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#old-trade-lookup

        Пример ответа:
        ```json
        [
          {
            "id": 28457,
            "price": "4.00000100",
            "qty": "12.00000000",
            "quoteQty": "48.000012",
            "time": 1499865549590,
            "isBuyerMaker": true,
            "isBestMatch": true
          }
        ]
        ```
        """
        params = self.filter_params({"symbol": symbol, "limit": limit, "fromId": from_id})
        return self._make_request(
            "GET", self._BASE_SPOT_URL + "/api/v3/historicalTrades", params=params
        )

    def futures_historical_trades(
        self, symbol: str, limit: int | None = None, from_id: int | None = None
    ) -> JsonLike:
        """Исторические сделки.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Old-Trades-Lookup

        Пример ответа:
        ```json
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
        """
        params = self.filter_params({"symbol": symbol, "limit": limit, "fromId": from_id})
        return self._make_request(
            "GET", self._BASE_FUTURES_URL + "/fapi/v1/historicalTrades", params=params
        )

    def ticker_24h(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        type: Literal["FULL", "MINI"] | None = None,
    ) -> JsonLike:
        """Статистика изменения цен за 24 часа.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#24hr-ticker-price-change-statistics

        Пример ответа:
        ```json
        {
          "symbol": "BNBBTC",
          "priceChange": "-94.99999800",
          "priceChangePercent": "-95.960",
          "weightedAvgPrice": "0.29628482",
          "prevClosePrice": "0.10002000",
          "lastPrice": "4.00000200",
          "lastQty": "200.00000000",
          "bidPrice": "4.00000000",
          "bidQty": "100.00000000",
          "askPrice": "4.00000200",
          "askQty": "100.00000000",
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

        ИЛИ

        ```json
        [
          {
            "symbol": "BNBBTC",
            "priceChange": "-94.99999800",
            "priceChangePercent": "-95.960",
            "weightedAvgPrice": "0.29628482",
            "prevClosePrice": "0.10002000",
            "lastPrice": "4.00000200",
            "lastQty": "200.00000000",
            "bidPrice": "4.00000000",
            "bidQty": "100.00000000",
            "askPrice": "4.00000200",
            "askQty": "100.00000000",
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
        """
        params = self.filter_params({"symbol": symbol, "type": type})
        if symbols is not None:
            params["symbols"] = json.dumps(symbols, separators=(",", ":"))
        return self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/ticker/24hr", params=params)

    def futures_ticker_24h(self, symbol: str | None = None) -> JsonLike:
        """Статистика изменения цен за 24 часа.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/24hr-Ticker-Price-Change-Statistics

        Пример ответа:
        ```json
        {
          "symbol": "BTCUSDT",
          "priceChange": "-94.99999800",
          "priceChangePercent": "-95.960",
          "weightedAvgPrice": "0.29628482",
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

        ИЛИ

        ```json
        [
            {
                "symbol": "BTCUSDT",
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "weightedAvgPrice": "0.29628482",
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
            },
        ]
        ```
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/ticker/24hr"
        params = self.filter_params({"symbol": symbol})
        return self._make_request("GET", url, params=params)

    def ticker_price(
        self, symbol: str | None = None, symbols: list[str] | None = None
    ) -> list[dict] | dict:
        """Последняя цена тикера(ов).

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#symbol-price-ticker

        Пример ответа:
        ```json
        {
          "symbol": "LTCBTC",
          "price": "4.00000200"
        }
        ```

        OR

        ```json
        [
          {
            "symbol": "LTCBTC",
            "price": "4.00000200"
          },
          {
            "symbol": "ETHBTC",
            "price": "0.07946600"
          }
        ]
        ```
        """
        params = self.filter_params({"symbol": symbol})
        if symbols is not None:
            params["symbols"] = json.dumps(symbols, separators=(",", ":"))
        url = self._BASE_SPOT_URL + "/api/v3/ticker/price"
        return self._make_request("GET", url, params=params)

    def futures_ticker_price(self, symbol: str | None = None) -> JsonLike:
        """Последняя цена тикера(ов).

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Symbol-Price-Ticker-v2

        Пример ответа:
        ```json
        {
          "symbol": "BTCUSDT",
          "price": "6000.01",
          "time": 1589437530011   // Transaction time
        }
        ```

        OR

        ```json
        [
            {
                "symbol": "BTCUSDT",
                "price": "6000.01",
                "time": 1589437530011
            },
        ]
        ```
        """
        params = self.filter_params({"symbol": symbol})
        return self._make_request(
            "GET", self._BASE_FUTURES_URL + "/fapi/v2/ticker/price", params=params
        )

    def open_interest(self, symbol: str) -> JsonLike:
        """Открытый интерес тикера.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest

        Пример ответа:
        ```json
        {
            "openInterest": "10659.509",
            "symbol": "BTCUSDT",
            "time": 1589437530011   // Transaction time
        }
        ```
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/openInterest"
        params = {"symbol": symbol}
        return self._make_request(method="GET", url=url, params=params)

    def klines(
        self,
        symbol: str,
        interval: SpotTimeframes,
        start_time: int | None = None,
        end_time: int | None = None,
        time_zone: str | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Свечи тикера.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data

        Пример ответа:
        ```json
        [
          [
            1499040000000,      // Kline open time
            "0.01634790",       // Open price
            "0.80000000",       // High price
            "0.01575800",       // Low price
            "0.01577100",       // Close price
            "148976.11427815",  // Volume
            1499644799999,      // Kline Close time
            "2434.19055334",    // Quote asset volume
            308,                // Number of trades
            "1756.87402397",    // Taker buy base asset volume
            "28.46694368",      // Taker buy quote asset volume
            "0"                 // Unused field, ignore.
          ],
        ]
        ```
        """
        url = self._BASE_SPOT_URL + "/api/v3/klines"
        params = self.filter_params(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "timeZone": time_zone,
                "limit": limit,
            }
        )

        return self._make_request("GET", url, params=params)

    def futures_klines(
        self,
        symbol: str,
        interval: FuturesTimeframes,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int | None = None,
    ) -> list[list]:
        """Свечи тикера.

        Документация:
            https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

        Пример ответа:
        ```json
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
        """
        url = self._BASE_FUTURES_URL + "/fapi/v1/klines"
        params = self.filter_params(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": start_time,
                "endTime": end_time,
                "limit": limit,
            }
        )

        return self._make_request("GET", url, params=params)


class AsyncBinanceClient(BaseAsyncClient, _BaseBinanceClient):
    """Асинхронный клиент для работы с Binance API."""

    async def exchange_info(self) -> JsonLike:
        """Текущие правила биржевой торговли и информация о символах.

        Документация:
            https://developers.binance.com/docs/binance-spot-api-docs/rest-api/general-endpoints

        Пример ответа:
        ```json
            {
            "timezone": "UTC",
            "serverTime": 1565246363776,
            "rateLimits": [
                {
                // These are defined in the `ENUM definitions` section under `Rate Limiters (rateLimitType)`.
                // All limits are optional
                }
            ],
            "exchangeFilters": [
                // These are the defined filters in the `Filters` section.
                // All filters are optional.
            ],
            "symbols": [
                {
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "baseAssetPrecision": 8,
                "quoteAsset": "BTC",
                "quotePrecision": 8, // will be removed in future api versions (v4+)
                "quoteAssetPrecision": 8,
                "baseCommissionPrecision": 8,
                "quoteCommissionPrecision": 8,
                "orderTypes": [
                    "LIMIT",
                    "LIMIT_MAKER",
                    "MARKET",
                    "STOP_LOSS",
                    "STOP_LOSS_LIMIT",
                    "TAKE_PROFIT",
                    "TAKE_PROFIT_LIMIT"
                ],
                "icebergAllowed": true,
                "ocoAllowed": true,
                "otoAllowed": true,
                "quoteOrderQtyMarketAllowed": true,
                "allowTrailingStop": false,
                "cancelReplaceAllowed":false,
                "amendAllowed":false,
                "pegInstructionsAllowed": true,
                "isSpotTradingAllowed": true,
                "isMarginTradingAllowed": true,
                "filters": [
                    // These are defined in the Filters section.
                    // All filters are optional
                ],
                "permissions": [],
                "permissionSets": [
                    [
                    "SPOT",
                    "MARGIN"
                    ]
                ],
                "defaultSelfTradePreventionMode": "NONE",
                "allowedSelfTradePreventionModes": [
                    "NONE"
                ]
                }
            ],
            // Optional field. Present only when SOR is available.
            // https://github.com/binance/binance-spot-api-docs/blob/master/faqs/sor_faq.md
            "sors": [
                {
                "baseAsset": "BTC",
                "symbols": [
                    "BTCUSDT",
                    "BTCUSDC"
                ]
                }
            ]
            }
        ```
        """
        return await self._make_request("GET", self._BASE_SPOT_URL + "/api/v3/exchangeInfo")
