from unicex.hyperliquid import Client

from os import getenv
import asyncio


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        private_key=getenv("WALLET_PRIVATE_KEY"),
    )

    from pprint import pp

    response = await client.place_order(
        asset="PURR",
        is_buy=False,
        price="0",
        size="0.0001",
        reduce_only=False,
        order_type="limit",
        # order_body={"tif": "Gtc"},
        order_body={"tif": "FrontendMarket"},
        # time_in_force="Gtc",
        # order_type={"limit": {"tif": "Gtc"}},
        # order_type={"market": {"tif": "Alo"}},
        # order_type={"trigger": {"isMarket": True, "triggerPx": "100", "tpsl": "tp"}},
        # order_type={"limit": {"tif": "FrontendMarket"}},
    )

    pp(response)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
