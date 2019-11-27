import aiohttp
import asyncio
import time 

async def main():
    async with aiohttp.ClientSession() as session:
        start = time.monotonic()
        async with session.get("https://www.amazon.comx/") as resp:
            print(resp.status)
        end = time.monotonic()
        print((end - start)*1000)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
