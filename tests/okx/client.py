from webbrowser import get
from unicex.okx import Client


import asyncio

from os import getenv


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create(
        api_key=getenv("OKX_API_KEY"),
        api_secret=getenv("OKX_API_SECRET"),
        api_passphrase=getenv("OKX_API_PASSPHRASE"),
    )
    r = await client.create_order(
        inst_id="XRP-USDT", side="buy", ord_type="market", px="2.9", sz="10"
    )
    #
    # r = await client.get_positions(inst_id="BTC-USDT")

    # r = await client.create_listen_key()

    from pprint import pp

    pp(r)

    await client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
