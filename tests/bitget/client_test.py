import asyncio
import os

from unicex.bitget.asyncio import Client


API_KEY: str = os.getenv("BITGET_API_KEY")  # type: ignore
API_SECRET: str = os.getenv("BITGET_API_SECRET")  # type: ignore
API_PASSPHRASE: str = os.getenv("BITGET_PASSPHRASE")  # type: ignore


async def main() -> None:
    """Main entry point for the application."""

    client = await Client.create(
        api_key=API_KEY, api_secret=API_SECRET, api_passphrase=API_PASSPHRASE
    )

    # POST SIGNED
    # response = await client._make_request(
    #     method="POST",
    #     endpoint="/api/v2/spot/trade/place-order",
    #     signed=True,
    #     data={
    #         "symbol": "BGBUSDT",
    #         "side": "buy",
    #         "orderType": "limit",
    #         "force": "gtc",
    #         "price": "5.240",
    #         "size": "0.4",
    #     },
    # )

    # GET UNSIGNED (+PARAMS)
    response = await client._make_request(
        method="GET", endpoint="/api/v2/spot/public/coins", params={"coin": "BGB"}
    )

    # GET UNSIGNED (-PARAMS)
    # response = await client._make_request(
    #     method="GET",
    #     endpoint="/api/v2/spot/public/coins",
    # )

    # GET SIGNED (+PARAMS)
    # response = await client._make_request(
    #     method="GET",
    #     endpoint="/api/v2/spot/trade/unfilled-orders",
    #     signed=True,
    #     params={"symbol": "BGBUSDT", "limit": "100"},
    # )

    # GET SIGNED (-PARAMS)
    response = await client._make_request(
        method="GET",
        endpoint="/api/v2/spot/account/assets",
        signed=True,
    )

    from pprint import pp

    pp(response)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
