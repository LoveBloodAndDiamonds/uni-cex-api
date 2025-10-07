# # topic: Order Book Trading
# # sub-topic: Market Data

# async def tickers(
#     self,
#     inst_type: Literal["SPOT", "SWAP", "FUTURES", "OPTION"],
#     inst_family: Literal["FUTURES", "SWAP", "OPTION"] | None = None,
# ) -> dict:
#     """Получение информации о тикерах.

#     https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-tickers

#     """
#     params = {
#         "instType": inst_type,
#         "instFamily": inst_family,
#     }
#     return await self._make_request("GET", endpoint="/api/v5/market/tickers", params=params)

# async def candles(
#     self,
#     inst_id: str,
#     bar: str | None = None,
#     after: int | None = None,
#     before: int | None = None,
#     limit: int | None = None,
# ) -> dict:
#     """Получение свечей.

#     https://www.okx.com/docs-v5/en/#order-book-trading-market-data-get-candlesticks
#     """
#     params = {
#         "instId": inst_id,
#         "bar": bar,
#         "after": after,
#         "before": before,
#         "limit": limit,
#     }
#     return await self._make_request("GET", endpoint="/api/v5/market/candles", params=params)

# # topic: Public Data
# # sub-topic: REST API

# async def get_funding_rate(self, inst_id: str) -> dict:
#     """Получение информации о ставке финансирования.

#     https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate
#     """
#     params = {
#         "instId": inst_id,
#     }
#     return await self._make_request(
#         "GET", endpoint="/api/v5/public/funding-rate", params=params
#     )

# async def get_open_interest(
#     self,
#     inst_type: Literal["SWAP", "FUTURES", "OPTION"],
#     inst_family: str | None = None,
#     inst_id: str | None = None,
# ) -> dict:
#     """Получение информации по открытому интересу.

#     https://www.okx.com/docs-v5/en/#public-data-rest-api-get-open-interest
#     """
#     params = {
#         "instType": inst_type,
#         "instFamily": inst_family,
#         "instId": inst_id,
#     }
#     return await self._make_request(
#         "GET", endpoint="/api/v5/public/open-interest", params=params
#     )
