import asyncio
import os

from unicex.bitget.asyncio import Client
from pprint import pp


API_KEY: str = os.getenv("BITGET_API_KEY")  # type: ignore
API_SECRET: str = os.getenv("BITGET_API_SECRET")  # type: ignore
API_PASSPHRASE: str = os.getenv("BITGET_PASSPHRASE")  # type: ignore


async def main() -> None:
    """Main entry point for the application."""

    client = await Client.create(
        api_key=API_KEY, api_secret=API_SECRET, api_passphrase=API_PASSPHRASE
    )

    re = await client.get_orderbook(symbol="BGBUSDT")

    pp(re)

    return

    # POST SIGNED
    # response = await client.place_order(
    #     symbol="BGBUSDT",
    #     side="buy",
    #     order_type="limit",
    #     force="gtc",
    #     price="5.240",
    #     size="0.4",
    # )
    """
    {'code': '00000',
     'msg': 'success',
     'requestTime': 1758783385489,
     'data': {'orderId': '1355001216939143169',
              'clientOid': '99d435bb-dfa9-424d-b0d9-6796644be302'}}
    """

    response = await client.place_order(
        symbol="BGBUSDT",
        side="buy",
        order_type="market",
        size="1",
    )

    # response = await client.get_order_info(order_id="1355001216939143169")
    """
    {'code': '00000',
     'msg': 'success',
     'requestTime': 1758783440479,
     'data': [{'userId': '7042352570',
               'symbol': 'BGBUSDT',
               'orderId': '1355001216939143169',
               'clientOid': '99d435bb-dfa9-424d-b0d9-6796644be302',
               'price': '5.240',
               'size': '0.4',
               'orderType': 'limit',
               'side': 'buy',
               'status': 'live',
               'priceAvg': '0',
               'baseVolume': '0',
               'quoteVolume': '0',
               'enterPointSource': 'API',
               'feeDetail': '',
               'orderSource': 'normal',
               'tpslType': 'normal',
               'triggerPrice': None,
               'quoteCoin': 'USDT',
               'baseCoin': 'BGB',
               'cancelReason': '',
               'cTime': '1758783385500',
               'uTime': '1758783385511'}]}
    """

    response = await client.cancel_order(symbol="BGBUSDT", order_id="1355001216939143169")
    """
    {'code': '00000',
     'msg': 'success',
     'requestTime': 1758783522070,
     'data': {'orderId': '1355001216939143169',
              'clientOid': '99d435bb-dfa9-424d-b0d9-6796644be302'}}
    """

    # GET UNSIGNED (+PARAMS)
    # response = await client._make_request(
    #     method="GET", endpoint="/api/v2/spot/public/coins", params={"coin": "BGB"}
    # )

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
    # response = await client._make_request(
    #     method="GET",
    #     endpoint="/api/v2/spot/account/assets",
    #     signed=True,
    # )

    pp(response)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
