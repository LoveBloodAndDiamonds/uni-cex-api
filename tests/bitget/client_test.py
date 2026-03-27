import asyncio
from datetime import datetime

from unicex.bitget import Client


async def main() -> None:
    """Main entry point for the application."""
    client = await Client.create()
    async with client:
        r = await client.futures_get_contracts("USDT-FUTURES")

        for item in r["data"]:
            symbol = item["symbol"]
            off_time = item["offTime"]

            # offTime == "-1" означает бессрочный контракт
            if off_time != "-1" and off_time != "":
                dt = datetime.fromtimestamp(int(off_time) / 1000)
                print(symbol, dt)


if __name__ == "__main__":
    asyncio.run(main())


"""
{'symbol': 'BTCUSDT',
 'lastPr': '66383',
 'askPr': '66384.5',
 'bidPr': '66384.4',
 'bidSz': '0.0152',
 'askSz': '17.0401',
 'high24h': '69850.6',
 'low24h': '66098.9',
 'ts': '1774619401596',
 'change24h': '-0.04662',
 'baseVolume': '61948.5546',
 'quoteVolume': '4217809623.2421',
 'usdtVolume': '4217809623.2421',
 'openUtc': '68791.9',
 'changeUtc24h': '-0.03515',
 'indexPrice': '66417.3150048314485464',
 'fundingRate': '0.000005',
 'holdingAmount': '29418.8402',
 'deliveryStartTime': None,
 'deliveryTime': None,
 'deliveryStatus': '',
 'open24h': '69629.3',
 'markPrice': '66384.4'}
{'symbol': 'PYRUSDT',
 'lastPr': '0.2704',
 'askPr': '0.2704',
 'bidPr': '0.2697',
 'bidSz': '209',
 'askSz': '123',
 'high24h': '0.2777',
 'low24h': '0.2666',
 'ts': '1774619401598',
 'change24h': '-0.02242',
 'baseVolume': '181315',
 'quoteVolume': '49446.0545',
 'usdtVolume': '49446.0545',
 'openUtc': '0.2757',
 'changeUtc24h': '-0.01922',
 'indexPrice': '0.2742436298954524',
 'fundingRate': '-0.001063',
 'holdingAmount': '255651',
 'deliveryStartTime': None,
 'deliveryTime': None,
 'deliveryStatus': '',
 'open24h': '0.2766',
 'markPrice': '0.2704'}
{'symbol': 'CTCUSDT',
 'lastPr': '0.146',
 'askPr': '0.147',
 'bidPr': '0.1468',
 'bidSz': '785',
 'askSz': '402',
 'high24h': '0.152',
 'low24h': '0.146',
 'ts': '1774619401599',
 'change24h': '-0.02472',
 'baseVolume': '159883',
 'quoteVolume': '23897.6545',
 'usdtVolume': '23897.6545',
 'openUtc': '0.1493',
 'changeUtc24h': '-0.0221',
 'indexPrice': '0.1470550824090751',
 'fundingRate': '0.00005',
 'holdingAmount': '1610073',
 'deliveryStartTime': None,
 'deliveryTime': None,
 'deliveryStatus': '',
 'open24h': '0.1497',
 'markPrice': '0.147'}

"""
