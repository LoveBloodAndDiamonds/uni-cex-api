import asyncio

from unicex import BitrueClient, BtseClient, GateioClient, KrakenClient, KucoinClient


async def main() -> None:
    """Main entry point for the application."""

    bitrue_client = await BitrueClient.create()
    btse_client = await BtseClient.create()
    gateio_client = await GateioClient.create()
    kraken_client = await KrakenClient.create()
    kucoin_client = await KucoinClient.create()

    from pprint import pp

    pp(await bitrue_client.server_time())
    pp(await btse_client.server_time())
    pp(await gateio_client.server_time())
    pp(await kraken_client.server_time())
    pp(await kucoin_client.server_time())

    await bitrue_client.close_connection()
    await btse_client.close_connection()
    await gateio_client.close_connection()
    await kraken_client.close_connection()
    await kucoin_client.close_connection()


if __name__ == "__main__":
    asyncio.run(main())
