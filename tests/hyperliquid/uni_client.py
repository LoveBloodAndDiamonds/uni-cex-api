from unicex.enums import Timeframe
from unicex.hyperliquid import UniClient, ExchangeInfo


import asyncio


async def main() -> None:
    """Main entry point for the application."""
    await ExchangeInfo.start()
    await asyncio.sleep(3)

    print(ExchangeInfo.resolve_spot_symbol("@38"))  # @52

    # return

    client = await UniClient.create()

    from pprint import pp

    resp = await client.futures_last_price()

    raise Exception(resp)

    # resp = await client.client.spot_meta_and_asset_contexts()

    # pp(resp["UBTC"])
    # print(len(resp))

    # print(len(spot_meta_and_asset_contexts[0]["universe"]))
    # print(len(spot_meta_and_asset_contexts[0]["tokens"]))
    # print(len(spot_meta_and_asset_contexts[1]))

    # spot:
    # 221
    # 375

    # resp = await client.futures_last_price()
    # resp = await client.funding_rate()
    # resp = await client.open_interest()

    # resp = await client.tickers(resolve_symbols=True)
    # resp = await client.last_price(resolve_symbols=False)

    # resp = await client.klines(
    #     symbol="@142", interval=Timeframe.MIN_1, limit=10, resolve_symbol=True
    # )

    # resp = await client.futures_klines(symbol="BTC", interval=Timeframe.MIN_1, limit=10)

    # pp(resp)

    # last_price = await client.last_price()
    # '@142': '123456.5',

    # spot_metadata = await client.client.spot_metadata()

    # universe = spot_metadata["universe"]
    # tokens = spot_metadata["tokens"]

    # number_to_idx = {}
    # for u in universe:
    #     number_to_idx[u["name"]] = u["tokens"][0]

    # idx_to_name = {}
    # for t in tokens:
    #     idx_to_name[t["index"]] = t["name"]

    # for number in last_price:
    #     try:
    #         idx = number_to_idx[number]
    #         name = idx_to_name[idx]
    #         print(name, last_price[number])
    #     except:
    #         print("ERROR -> ", number, last_price[number])

    # tickers = await client.tickers()
    # futures_tickers = await client.futures_tickers()

    # print(tickers)
    # print(len(tickers))

    # lp = await client.last_price()
    # print(lp)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
