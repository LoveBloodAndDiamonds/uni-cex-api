import asyncio

import aiohttp
import time


async def main() -> None:
    """Main entry point for the application."""
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.asterdex.com/bapi/future/v1/public/future/aster/ticker/pair"
            ) as response:
                data = await response.json()

                code = response.status

                response.raise_for_status()

                from pprint import pp

                try:
                    for item in data["data"]:
                        if item["symbol"] == "BTCUSDT":
                            print(time.ctime(), item)
                except Exception as e:
                    print(time.ctime(), code, str(data)[:200])

                # for item in data["data"]:
                # print(item["symbol"], int(item["openInterest"]))


if __name__ == "__main__":
    asyncio.run(main())
