from unicex.hyperliquid import Client

from os import getenv
import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        private_key=getenv("WALLET_PRIVATE_KEY"),
    )

    from pprint import pp

    # response = await client.place_order(
    #     asset=0,
    #     is_buy=True,
    #     price="120000",
    #     size="0.0001",
    #     reduce_only=False,
    #     order_type="limit",
    #     order_body={"tif": "Gtc"},
    #     client_order_id="0x1234567890abcdef1234567890abcdef",
    #     # order_body={"tif": "FrontendMarket"},
    #     # time_in_force="Gtc",
    #     # order_type={"limit": {"tif": "Gtc"}},
    #     # order_type={"market": {"tif": "Alo"}},
    #     # order_type={"trigger": {"isMarket": True, "triggerPx": "100", "tpsl": "tp"}},
    #     # order_type={"limit": {"tif": "FrontendMarket"}},
    # )

    # 0x1234567890abcdef1234567890abcdef

    # response = await client.cancel_order(asset=0, order_id=187095629111)

    # response = await client.cancel_order_by_cloid(
    #     asset=0, client_order_id="0x1234567890abcdef1234567890abcdef"
    # )

    # response = await client.usd_class_transfer(
    #     hyperliquid_chain="Mainnet", signature_chain_id="0xa4b1", amount="1", to_perp=True
    # )

    response = await client.all_mids()

    pp(response)

    response = await client.spot_metadata()

    # pp(response)

    tokens = response[0]["tokens"]
    universe = response[0]["universe"]

    # for t in tokens:
    #     print(t)
    #     if t["name"] in ["BTC/USDC"]:
    #         print(t)

    for t in universe:
        print(t)

    # pp(response)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
