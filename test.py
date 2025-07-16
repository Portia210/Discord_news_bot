import asyncio
import aiohttp
from config import Config
from utils.timer import measure_time
from utils.logger import logger

proxy = f"http://brd-customer-{Config.PROXY_DETAILS.CUSTOMER_ID}-zone-{Config.PROXY_DETAILS.ZONE}:{Config.PROXY_DETAILS.PASSWORD}@{Config.PROXY_DETAILS.HOST}:{Config.PROXY_DETAILS.PORT}"
url = 'https://geo.brdtest.com/mygeo.json'

@measure_time
async def fetch_data(with_proxy: bool = True):
    async with aiohttp.ClientSession() as session:
        try:
            # Use proxy only if it's enabled
            if with_proxy:
                async with session.get(url, proxy=proxy) as response:
                    text = await response.text()
                    print(text)
            else:
                # Make request without proxy
                async with session.get(url) as response:
                    text = await response.text()
                    print(text)
        except aiohttp.ClientError as e:
            print(e)

# Run the async function
if __name__ == "__main__":
    logger.info("with proxy")
    asyncio.run(fetch_data(with_proxy=True))
    logger.info("without proxy")
    asyncio.run(fetch_data(with_proxy=False))
