import requests
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils.logger import logger
import os
import pandas as pd
import pytz
from config import Config
from utils.read_write import read_json_file
from utils.safe_update_dict import safe_update_dict
import json
from investing_scraper.investing_variables import InvestingVariables
from utils.read_write import write_json_file
import asyncio


class InvestingDataScraper:
    def __init__(self):
        self.headers = read_json_file(f'investing_scraper/headers.json')
        logger.debug(f"Initialized investing scraper")
    
    @staticmethod
    def get_element_attirbutes(soup_element, attributes):
        for attribute in attributes:
            if attribute == "text":
                value = soup_element.text.strip()
            else:
                value = soup_element.get(attribute)
            if value:
                return value
        return None


    async def _fetch_table(self, page_name, payload: dict ):
        """Fetch and parse the webpage asynchronously"""
        logger.debug(f"Fetching table data for {page_name}")
        request_json = read_json_file(f'investing_scraper/requests_json/{page_name}.json')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(request_json['url'], headers=self.headers, data=payload) as response:
                # logger.debug(f"Request body: {payload}")
                if response.status != 200:
                    logger.error(f"Failed to fetch page. Status code: {response.status}")
                    return None
                try:
                    json_response = await response.read()
                    table_html = json.loads(json_response).get("data", '') 
                    return table_html
                except Exception as e:
                    logger.error(f"Error parsing JSON: {str(e)}")
                    return None 


    def _process_table_data(self, page_name, table_html):
        """Process all rows in the table"""
        table_structure = read_json_file(f'investing_scraper/tables_stucture.json')[page_name]
        table_selectors = table_structure["table_selectors"]

        def proccess_tr(tr, table_selectors):
            """Extract data from a single row"""
            row_data = {}
            for item_name, selector in table_selectors.items():
                if item_name == "date":
                    continue
                try:
                    data_element = tr.select_one(selector["selector"])
                    if data_element:
                        row_data[item_name] = self.get_element_attirbutes(data_element, selector["attribute"])
                except Exception as e:
                    logger.error(f"Error processing {item_name}: {str(e)}")
            return row_data
        
        table_soup = BeautifulSoup(table_html, 'html.parser')   
        all_rows = table_soup.find_all('tr')

        events_by_date = {}
        current_events = []
        current_date = "unknown"
        
        for row in all_rows:
            date_element = row.select_one(table_selectors['date']['selector'])
            new_date = self.get_element_attirbutes(date_element, table_selectors['date']['attribute']) if date_element else None


            # add the previous events to the matching date
            if new_date:
                if current_events:
                    events_by_date[current_date] = current_events
                    current_events = []
                current_date = new_date
                
            # extract the events if if not a date tr, or if the date is inline
            if not new_date or table_structure["is_date_inline"]:
                proccessed_row = proccess_tr(row, table_selectors)
                if proccessed_row:
                    current_events.append(proccessed_row)
        
        if current_events:
            events_by_date[current_date] = current_events
        
        return events_by_date
    



    def flatten_data(self, data):
        flat_data = []
        for date, events in data.items():
            for event in events:
                event['date'] = date
                flat_data.append(event)
        return flat_data

    def _save_data(self, file_name, data):
        output_dir = os.path.join("data", "investing_scraper")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, f"{file_name}.csv"), index=False)





    
    async def run(self, page_name, payload: dict, save_data: bool = False):
        table_html = await self._fetch_table(page_name, payload)
        if not table_html:
            logger.error(f"Failed to fetch table data for {page_name}")
            return None
        events_by_dates = self._process_table_data(page_name, table_html)
        write_json_file(f"data/investing_scraper/temp.json", events_by_dates)
        if events_by_dates == {}:
            logger.error(f"No events found for {page_name}")
            return 
        
        flat_data = self.flatten_data(events_by_dates)
        if save_data:
            self._save_data(f"{page_name}_{datetime.now().strftime('%Y-%m-%d')}", flat_data)

        return flat_data
    

        
    async def get_calendar(
            self,
            calendar_name: str,
            current_tab: str=InvestingVariables.TIME_RANGES.TODAY, 
            importance: list[str]=[InvestingVariables.IMPORTANCE.LOW, InvestingVariables.IMPORTANCE.MEDIUM, InvestingVariables.IMPORTANCE.HIGH], 
            countries: list[str]=[InvestingVariables.COUNTRIES.UNITED_STATES], 
            time_zone: str=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE), 
            date_from: str = None, 
            date_to: str = None, 
            save_data: bool = False):
        
        payload = {
            "currentTab": current_tab,
            "importance[]": importance,
            "country[]": countries,
            "timeZone": time_zone,
        }
        if date_from:
            payload["dateFrom"] = date_from
        if date_to:
            payload["dateTo"] = date_to
        return await self.run(calendar_name, payload, save_data)
    

if __name__ == "__main__":
    investing_scraper = InvestingDataScraper()
    for value in InvestingVariables.IMPORTANCE:

        result = asyncio.run(investing_scraper.get_calendar(
            calendar_name= InvestingVariables.CALENDARS.HOLIDAY_CALENDAR,
            current_tab= InvestingVariables.TIME_RANGES.CUSTOM,
            importance=[value],
            date_from="2025-07-01",
            date_to="2025-08-23",
            save_data=True))
        print(f"count: {result}")