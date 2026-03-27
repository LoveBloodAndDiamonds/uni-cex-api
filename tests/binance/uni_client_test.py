import asyncio

from unicex import OrderSide, OrderType, MarginType  # type: ignore
from unicex.binance import UniClient
from unicex import IUniClient

from loguru import logger  # type: ignore

import os

logger.remove()


async def main() -> None:
    """Main entry point for the application."""
    c = await UniClient.create(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
    )

    # async with c:
    tickers = await c.tickers()
    print(len(tickers))

    # fi = await c.funding_interval()
    # print(fi)

    # for t in tickers:
    #     await c.futures_set_leverage(t, leverage=5)
    #     await c.futures_set_margin_type(t, MarginType.ISOLATED)
    #     print(t)

    # async with c:
    # while True:
    #     import time

    #     time.sleep(1)
    #     # r = await c.futures_order_create(
    #     #     symbol="TRXUSDT",
    #     #     side=OrderSide.BUY,
    #     #     type=OrderType.MARKET,
    #     #     quantity="100",
    #     #     reduce_only=True,
    #     # )
    #     r = await c.client.futures_position_info("BARDUSDT", version="3")
    #     from pprint import pp

    #     pp(r)


if __name__ == "__main__":
    asyncio.run(main())


"""
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60460000',
  'unRealizedProfit': '-0.01200000',
  'liquidationPrice': '0.49434959',
  'isolatedMargin': '2.40274800',
  'notional': '12.09200000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.41474800',
  'initialMargin': '2.41840000',
  'maintMargin': '0.24184000',
  'positionInitialMargin': '2.41840000',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910474707}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60530000',
  'unRealizedProfit': '0.00200000',
  'liquidationPrice': '0.49434959',
  'isolatedMargin': '2.41674800',
  'notional': '12.10600000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.41474800',
  'initialMargin': '2.42120000',
  'maintMargin': '0.24212000',
  'positionInitialMargin': '2.42120000',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910474707}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60484088',
  'unRealizedProfit': '-0.00718240',
  'liquidationPrice': '0.49434959',
  'isolatedMargin': '2.40756560',
  'notional': '12.09681760',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.41474800',
  'initialMargin': '2.41936352',
  'maintMargin': '0.24193635',
  'positionInitialMargin': '2.41936352',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910474707}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60490000',
  'unRealizedProfit': '-0.00600000',
  'liquidationPrice': '0.49434959',
  'isolatedMargin': '2.40874800',
  'notional': '12.09800000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.41474800',
  'initialMargin': '2.41960001',
  'maintMargin': '0.24196000',
  'positionInitialMargin': '2.41960001',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910474707}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60470000',
  'unRealizedProfit': '-0.01000000',
  'liquidationPrice': '0.49398487',
  'isolatedMargin': '2.41189652',
  'notional': '12.09400000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.42189652',
  'initialMargin': '2.41880000',
  'maintMargin': '0.24188000',
  'positionInitialMargin': '2.41880000',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910800256}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60480000',
  'unRealizedProfit': '-0.00800000',
  'liquidationPrice': '0.49398487',
  'isolatedMargin': '2.41389652',
  'notional': '12.09600000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.42189652',
  'initialMargin': '2.41920000',
  'maintMargin': '0.24192000',
  'positionInitialMargin': '2.41920000',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910800256}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60500000',
  'unRealizedProfit': '-0.00400000',
  'liquidationPrice': '0.49398487',
  'isolatedMargin': '2.41789652',
  'notional': '12.10000000',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.42189652',
  'initialMargin': '2.42000000',
  'maintMargin': '0.24200000',
  'positionInitialMargin': '2.42000000',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910800256}]
[{'symbol': 'BARDUSDT',
  'positionSide': 'BOTH',
  'positionAmt': '20',
  'entryPrice': '0.6052',
  'breakEvenPrice': '0.6055026',
  'markPrice': '0.60524007',
  'unRealizedProfit': '0.00080140',
  'liquidationPrice': '0.49398487',
  'isolatedMargin': '2.42269792',
  'notional': '12.10480140',
  'marginAsset': 'USDT',
  'isolatedWallet': '2.42189652',
  'initialMargin': '2.42096028',
  'maintMargin': '0.24209602',
  'positionInitialMargin': '2.42096028',
  'openOrderInitialMargin': '0',
  'adl': 3,
  'bidNotional': '0',
  'askNotional': '0',
  'updateTime': 1773910800256}]


"""
