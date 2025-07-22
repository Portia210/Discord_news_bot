import requests
from bs4 import BeautifulSoup
import asyncio
import concurrent.futures
import os
from utils.logger import logger
from utils.read_write import read_json_file, write_json_file

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


# Create a session for consistent requests
session = requests.Session()
session.headers.update(headers)

def extract_text_from_soup(soup: BeautifulSoup, selector):
    element = soup.select_one(selector)
    if element:
        return element.get_text()
    else:
        return None

def get_description(symbol):
    url = f"https://production.dataviz.cnn.io/quote/profile/{symbol}"
    logger.info(f"Getting description for {symbol} from {url}")
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()[0]
        wanted_fields = ["symbol", "description", "market_cap", "market_cap_profile", "website_url", "profit_earnings_ratio"]
        return {field: data[field] for field in wanted_fields if field in data}
    else:
        logger.error(f"Error getting description for {symbol}")
        logger.error(response.status_code)
        return {}

async def get_description_async(symbol):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, get_description, symbol)

async def get_companies_description(companies_symbols):
    descriptions = {}
    for i, symbol in enumerate(companies_symbols):
        # Add delay between requests (except for the first one)
        if i > 0:
            await asyncio.sleep(0.5)  # 0.5 second delay between requests
        description = await get_description_async(symbol)
        if description:
            descriptions[symbol] = description

    return descriptions

async def main():
    companies_symbols2 = ["AAPL", "MSFT", "GOOGL", "PLTR", "IREN", "TSLA", "NVDA", "META", "AMZN", "GOOG", "NFLX", "TSM", "BABA", "WMT", "JPM", "V", "JNJ", "PG", "MA", "UNH", "XOM", "JPM", "A", "BAC", "CSCO", "DAL", "DIS", "GE", "GS", "HD", "IBM", "INTC", "JNJ", "JPM", "KO", "MCD", "MMM", "MRK", "MS", "NFLX", "NKE", "ORCL", "PEP", "PG", "T", "TSM", "UNH", "V", "VZ", "WMT", "XOM"]
    companies_symbols = ["IREN", "CORZ", "CRWV"]
    descriptions_path = "companies_descriptions.json"
    if not os.path.exists(descriptions_path):
        write_json_file(descriptions_path, {})
    descriptions = read_json_file(descriptions_path)
    not_processed_symbols = [symbol for symbol in companies_symbols if symbol not in descriptions]

    logger.info(f"Not processed symbols: {not_processed_symbols}")
    input("Press Enter to continue...")
    for i in range(0, len(not_processed_symbols), 5):
        chunk = not_processed_symbols[i:i+5]
        descriptions_async = await get_companies_description(chunk)
        # update descriptions
        descriptions.update(descriptions_async)
        # write to json file
        write_json_file(descriptions_path, descriptions)

if __name__ == "__main__":
    asyncio.run(main())