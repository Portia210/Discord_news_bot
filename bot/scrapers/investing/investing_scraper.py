import requests
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import pandas as pd
import pytz
from config import Config
from utils import read_json_file, write_json_file, logger
import json
from .investing_params import InvestingParams
import asyncio

class InvestingScraper:
    def __init__(self, proxy=None):
        self.headers = read_json_file(f'scrapers/investing/investing_headers.json')
        self.proxy = proxy
        logger.debug(f"Initialized investing scraper" + (" with proxy" if self.proxy else ""))
    
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

    async def _fetch_table(self, page_name, payload: dict):
        """Fetch and parse the webpage asynchronously"""
        logger.debug(f"Fetching table data for {page_name}")
        request_json = read_json_file(f'investing_scraper/requests_json/{page_name}.json')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(request_json['url'], headers=self.headers, data=payload, proxy=self.proxy) as response:
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
        except Exception as e:
            logger.error(f"Error fetching table: {str(e)}")
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

    def _save_data(self, file_name, data: pd.DataFrame):
        output_dir = os.path.join("data", "investing_scraper")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        data.to_csv(os.path.join(output_dir, f"{file_name}.csv"), index=False)





    
    async def run(self, page_name, payload: dict, save_data: bool = False):
        table_html = await self._fetch_table(page_name, payload)
        if not table_html:
            logger.error(f"Failed to fetch table data for {page_name}")
            return None
        events_by_dates = self._process_table_data(page_name, table_html)
        try:
            write_json_file(f"data/investing_scraper/temp.json", events_by_dates)
            if events_by_dates == {}:
                logger.error(f"No events found for {page_name}")
                return 
            
            flat_data = self.flatten_data(events_by_dates)
            df = pd.DataFrame(flat_data)
            if save_data:
                now_timestamp = datetime.now().timestamp()
                self._save_data(f"{page_name}_{now_timestamp}", df)

            return df
        except Exception as e:
            logger.error(f"Error running {page_name}: {str(e)}")
            return None

        
    async def get_calendar(
            self,
            calendar_name: str,
            current_tab: str=InvestingParams.TIME_RANGES.TODAY, 
            importance: list[str]=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH], 
            countries: list[str]=[InvestingParams.COUNTRIES.UNITED_STATES], 
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
    
    # this is test function to test the scheduler
    # async def get_calendar(
    #         self,
    #         calendar_name: str,
    #         current_tab: str=InvestingVariables.TIME_RANGES.TODAY, 
    #         importance: list[str]=[InvestingVariables.IMPORTANCE.LOW, InvestingVariables.IMPORTANCE.MEDIUM, InvestingVariables.IMPORTANCE.HIGH], 
    #         countries: list[str]=[InvestingVariables.COUNTRIES.UNITED_STATES], 
    #         time_zone: str=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE), 
    #         date_from: str = None, 
    #         date_to: str = None, 
    #         save_data: bool = False):
        
    #     df = pd.read_csv(f"data/investing_scraper/economic_test.csv")
    #     # change value of df time[1] to next minutes 
    #     next_minutes = (datetime.now(pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)) + timedelta(minutes=1)).strftime("%H:%M")
    #     df.loc[0, "time"] = next_minutes
    #     return df
    



if __name__ == "__main__":
    import time
    proxy_scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY)
    no_proxy_scraper = InvestingScraper(proxy=None)

    async def get_todays_data(scraper):
        return await scraper.get_calendar(
            calendar_name= InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
            current_tab= InvestingParams.TIME_RANGES.TODAY,
            importance=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH],
            save_data=True)

    async def check_investing_latency():
        # print now hour and minute and second 
        print(datetime.now().hour, datetime.now().minute, datetime.now().second)
        # check if now time is 16:45
        if not os.path.exists("data/investing_scraper"):
            os.makedirs("data/investing_scraper")
        while True:
            if datetime.now().hour == 17 and datetime.now().minute == 0:
                now_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                print("now time is 17:00")
                df = await get_todays_data(no_proxy_scraper)
                df.to_csv(f"data/investing_scraper/{now_time}.csv", index=False)
                
            else:
                print("now time is not 17:00")
                time.sleep(1)
    asyncio.run(check_investing_latency())
    # async def get_all_year_data(scraper):
    async def get_all_year_data(scraper):
        all_months = [f"0{i}" if i < 10 else f"{i}" for i in range(1, 13)]
        days_ranges = ["01", "10", "20"]
        for month_index, month in enumerate(all_months):
            for day_index, day in enumerate(days_ranges):
                # Calculate the next date in a cleaner way
                if day_index < len(days_ranges) - 1:
                    # Next day in same month
                    date_to = f"2025-{month}-{days_ranges[day_index+1]}"
                elif month_index < len(all_months) - 1:
                    # First day of next month
                    date_to = f"2025-{all_months[month_index+1]}-{days_ranges[0]}"
                else:
                    # First day of next year
                    date_to = "2026-01-01"

                await scraper.get_calendar(
                    calendar_name= InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
                    current_tab= InvestingParams.TIME_RANGES.CUSTOM,
                    importance=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH],
                    date_from=f"2025-{month}-{day}",
                    date_to=date_to,
                    save_data=True)

