import requests
import asyncio
import concurrent.futures
from utils.logger import logger

headers = {
    'accept': '*/*',
    'accept-language': 'en,en-US;q=0.9,he;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://edition.cnn.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://edition.cnn.com/',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
}


def get_company_info(symbol):
    url = f"https://production.dataviz.cnn.io/quote/profile/{symbol}"
    logger.info(f"Getting description for {symbol} from {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()[0]
        wanted_fields = ["symbol", "description", "market_cap", "market_cap_profile", "website_url", "profit_earnings_ratio"]
        return {field: data[field] for field in wanted_fields if field in data}
    else:
        logger.error(f"Error getting description for {symbol}")
        logger.error(response.status_code)
        return {}

async def get_info_async(symbol):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, get_company_info, symbol)

async def get_companies_info(companies_symbols):
    descriptions = {}
    for i, symbol in enumerate(companies_symbols):
        # Add delay between requests (except for the first one)
        if i > 0:
            await asyncio.sleep(0.5)  # 0.5 second delay between requests
        description = await get_info_async(symbol)
        if description:
            descriptions[symbol] = description

    return descriptions


if __name__ == "__main__":
    # asyncio.run(main())
    symbol = "SPY"
    description = get_company_info(symbol)
    print(description)