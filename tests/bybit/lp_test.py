import asyncio

from unicex import BybitClient
from os import getenv


async def main() -> None:
    client = await BybitClient.create(
        api_key=getenv("BYBIT_API_KEY"), api_secret=getenv("BYBIT_API_SECRET")
    )

    # orders = await client._make_request(
    #     "POST",
    #     "/v5/p2p/item/online",
    #     params={
    #         "tokenId": "USDT",
    #         "currencyId": "USD",
    #         "side": "1",  # 0 - buy, 1 - sell,
    #         # "page": "1",
    #         # "size": "10",
    #     },
    #     signed=True,
    # )

    # orders = await client.position_info(category="option", settle_coin="USDT")

    # resp = await client.account_info()

    # resp = await client.set_leverage(
    #     category="linear", symbol="BTCUSDT", buy_leverage="11", sell_leverage="11"
    # )

    # resp = await client.create_order(
    #     category="linear",
    #     qty="300",
    #     price="0.29445",
    #     order_type="Limit",
    #     symbol="TRXUSDT",
    #     side="Buy",
    # )
    #
    positions_raw = await client.position_info(category="linear", symbol="BTCUSDT")

    from pprint import pp

    pp(positions_raw)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
