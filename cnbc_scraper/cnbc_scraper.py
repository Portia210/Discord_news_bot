import json
import re
from bs4 import BeautifulSoup
from utils.logger import logger
import requests
from yf_scraper.headers import headers
from utils.read_write import write_json_file
import pytz
from utils.timezones_convertor import convert_to_my_timezone
from config import Config
import os
import asyncio
import aiohttp

def extract_s_data_dict_from_html(html_content: str) -> dict:
    """
    Extract the window.__s_data dictionary from HTML content.
    
    Args:
        html_content (str): HTML content as string
        
    Returns:
        dict: The parsed dictionary from window.__s_data, or empty dict if not found
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find script tag containing window.__s_data
        script_pattern = re.compile(r'window\.__s_data\s*=\s*({.*?});', re.DOTALL)
        
        # Search in all script tags
        for script in soup.find_all('script'):
            if script.string:
                match = script_pattern.search(script.string)
                if match:
                    json_str = match.group(1)
                    # Parse the JSON string
                    data_dict = json.loads(json_str)
                    logger.info(f"✅ Successfully extracted window.__s_data dictionary")
                    return data_dict
        
        logger.warning("⚠️ window.__s_data not found in HTML")
        return {}
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parsing JSON from window.__s_data: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ Error extracting window.__s_data: {e}")
        return {}

def get_all_modules(json_data: dict) -> list:
    layout_items = json_data["page"]["page"]["layout"]

    all_modules = []
    for layout_item in layout_items:
        columns = layout_item["columns"]
        for column in columns:
            all_modules.extend(column["modules"])
            # modules_names = set([module["name"] for module in column["modules"]])
            # logger.debug(f"✅ {modules_names}")
    return all_modules

def get_clean_assets(all_modules: list, wanted_modules: list, optional_fields: list = []) -> dict:
    clean_assets = {}
    for module in all_modules:
        # if True:
        if module["name"] in wanted_modules:
            clean_assets[module["name"]] = {}
            data = module["data"]["assets"]
            for i, asset in enumerate(data):
                try:
                    if "title" not in asset:
                        continue
                    id = asset["id"]
                    title = asset["title"]
                    url = asset["url"]
                    clean_asset = {
                        "title": title,
                        "url": url,
                    }
                    for field in optional_fields:
                        if field in asset:
                            if field == "datePublished":
                                formatted_date = convert_to_my_timezone(asset["datePublished"], pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')
                                clean_asset[field] = formatted_date
                            else:
                                clean_asset[field] = asset[field]

                    clean_assets[module["name"]][id] = clean_asset
                except Exception as e:
                    logger.warning(f"⚠️ {e} not found in {asset}")
    return clean_assets

async def get_cnbc_world_assets(region: str = "us", proxy: str = None) -> dict[str, dict]:
    full_url = f"https://www.cnbc.com/world/?region={region}"
    async with aiohttp.ClientSession() as session:
        async with session.get(full_url, headers=headers, proxy=proxy) as response:
            html_content = await response.text()
    json_data = extract_s_data_dict_from_html(html_content)
    write_json_file("cnbc_world_s_data.json", json_data)
    all_modules = get_all_modules(json_data)
    wanted_modules = ["latestNews", "riverPlus", "featuredNewsHero"]
    clean_assets = get_clean_assets(all_modules, wanted_modules, ["datePublished", "description"])
    return clean_assets

# Example usage
async def main():

    output_dir = "data/cnbc"
    os.makedirs(output_dir, exist_ok=True)
    clean_assets = await get_cnbc_world_assets(proxy=Config.PROXY_DETAILS.APP_PROXY, region="world")
    for module_name, assets in clean_assets.items():
        write_json_file(f"{output_dir}/{module_name}.json", assets)


if __name__ == "__main__":
    asyncio.run(main())
