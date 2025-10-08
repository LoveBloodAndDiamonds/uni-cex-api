import asyncio
from operator import call

from unicex.hyperliquid import WebsocketManager


async def callback(msg):
    try:
        print(type(msg), msg)
    except Exception as e:
        print(f"Error in callback: {e}")


async def main() -> None:
    """Main entry point for the application."""
    manager = WebsocketManager()

    c = {"callback": callback}

    user = "0x53cEF83660805dC804779565EBDe9145f1DDA8B6"

    ws = manager.notification(*c, user=user)  # type: ignore
    ws = manager.web_data2(*c, user=user)  # type: ignore
    ws = manager.candle(**c, coin="@142", interval="1m")  # type: ignore
    ws = manager.l2_book(**c, coin="BTC")  # type: ignore
    ws = manager.trades(**c, coin="BTC")
    ws = manager.order_updates(**c, user=user)
    ws = manager.user_events(**c, user=user)
    ws = manager.user_fills(**c, user=user)  # type: ignore
    ws = manager.user_fundings(**c, user=user)
    ws = manager.user_non_funding_ledger_updates(**c, user=user)
    ws = manager.active_asset_ctx(**c, coin="BTC")
    ws = manager.active_asset_data(**c, user=user, coin="BTC")
    ws = manager.user_twap_slice_fills(**c, user=user)
    ws = manager.user_twap_history(**c, user=user)
    ws = manager.bbo(**c, coin="BTC")

    await ws.start()


if __name__ == "__main__":
    asyncio.run(main())
