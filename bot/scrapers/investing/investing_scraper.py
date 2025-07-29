import requests
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import pandas as pd
import pytz
import re
from config import Config
from utils import read_json_file, write_json_file, get_time_delta_for_date, logger
import json
from .investing_params import InvestingParams
import asyncio

class InvestingScraper:
    def __init__(self, proxy=None, timezone=None):
        self.headers = read_json_file(f'scrapers/investing/investing_headers.json')
        self.proxy = proxy
        self.timezone = timezone
        logger.debug(f"Initialized investing scraper" + (" with proxy" if self.proxy else "") + (f" with timezone {self.timezone}" if self.timezone else ""))
    
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
        # logger.debug(f"Fetching table data for {page_name}")
        request_json = read_json_file(f'scrapers/investing/requests_json/{page_name}.json')
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
        table_structure = read_json_file(f'scrapers/investing/tables_stucture.json')[page_name]
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
    
    def _adjust_date_format(self, date: str):
        if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date):
            return datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
        return date
    
    def _process_holidays_data(self, holiday_data:pd.DataFrame):
        holiday_data['time'] = None
        
        for idx, event in holiday_data.iterrows():
            try:
                # Use self.timezone if available, otherwise fall back to config
                target_timezone = self.timezone if self.timezone else Config.TIMEZONES.APP_TIMEZONE
                
                hours_offset = get_time_delta_for_date(event["date"], target_timezone, Config.TIMEZONES.EASTERN_US)["delta_hours"]
                
                if "שעת סגירה מוקדמת" in event["holiday"]:
                    time_match = re.search(r'(\d{1,2}:\d{2})', event["holiday"])
                    if time_match:
                        time_str = time_match.group(1)
                        adjusted_time = datetime.strptime(time_str, "%H:%M") + timedelta(hours=hours_offset)
                        holiday_data.loc[idx, 'time'] = adjusted_time.strftime("%H:%M")
                    else:
                        holiday_data.loc[idx, 'time'] = "unknown time"
                else:
                    holiday_data.loc[idx, 'time'] = "all day"
            except Exception as e:
                logger.error(f"Error processing holiday data for {event.get('date', 'unknown date')}: {str(e)}")
                holiday_data.loc[idx, 'time'] = "unknown time"
        
        return holiday_data



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
            return pd.DataFrame()
        events_by_dates = self._process_table_data(page_name, table_html)
        try:
            # os.makedirs("data/investing_scraper", exist_ok=True)
            # write_json_file(f"data/investing_scraper/temp.json", events_by_dates)
            if events_by_dates == {}:
                logger.error(f"No events found for {page_name}")
                return pd.DataFrame()
            
            flat_data = self.flatten_data(events_by_dates)
            df = pd.DataFrame(flat_data)
            # adjust date format to yyyy-mm-dd
            df['date'] = df['date'].apply(self._adjust_date_format)

            if page_name == "holiday_calendar":
                df = self._process_holidays_data(df)
                pass
            if save_data:
                now_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f") # with microseconds
                self._save_data(f"{page_name}_{now_timestamp}", df)

            return df
        except Exception as e:
            logger.error(f"Error running {page_name}: {str(e)}")
            return pd.DataFrame()

        
    async def get_calendar(
            self,
            calendar_name: str,
            current_tab: str=InvestingParams.TIME_RANGES.TODAY, 
            importance: list[str]=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH], 
            countries: list[str]=[InvestingParams.COUNTRIES.UNITED_STATES], 
            time_zone: str=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE), 
            from_date: str = None, 
            to_date: str = None, 
            save_data: bool = False):
        
        payload = {
            "currentTab": current_tab,
            "importance[]": importance,
            "country[]": countries,
            "timeZone": time_zone,
        }
        if from_date:
            payload["dateFrom"] = from_date
        if to_date:
            payload["dateTo"] = to_date
        return await self.run(calendar_name, payload, save_data)
    



if __name__ == "__main__":
    import re
    # Test with different timezones
    scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY, timezone=Config.TIMEZONES.APP_TIMEZONE)
    if not os.path.exists("data/investing_scraper"):
        os.makedirs("data/investing_scraper")
    
    async def get_todays_data(scraper):
        return await scraper.get_calendar(
            calendar_name= InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
            current_tab= InvestingParams.TIME_RANGES.CUSTOM,
            importance=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH],
            date_from="2025-07-02",
            date_to="2025-07-04",
            save_data=False)


    async def get_holidays_data(scraper):
        return await scraper.get_calendar(
            calendar_name= InvestingParams.CALENDARS.HOLIDAY_CALENDAR,
            current_tab= InvestingParams.TIME_RANGES.CUSTOM,
            importance=[InvestingParams.IMPORTANCE.LOW, InvestingParams.IMPORTANCE.MEDIUM, InvestingParams.IMPORTANCE.HIGH],
            date_from="2025-01-01",
            date_to="2025-12-31",
            save_data=True)







    
    holidays_data = asyncio.run(get_holidays_data(scraper))







    def check_vacation_today(today_data:pd.DataFrame):
        today_data['vacation'] = None
        vacation_events = today_data[today_data["volatility"] == "חופשה"]
        
        for idx, event in vacation_events.iterrows():
            if event["time"] == "כל היום":
                today_data.loc[idx, 'vacation'] = "all day"
            else:
                time_match = re.search(r'(\d{1,2}:\d{2})', event["description"])
                today_data.loc[idx, 'vacation'] = time_match.group(1) if time_match else "unknown time"
        
        return today_data

    
    # logger.info(f"Today data: {today_data.columns}")
    # for index, event in today_data.iterrows():
    #     if event["previous"] is None and event["actual"] is not None:
    #         logger.info(f"Event name: {event['description'][::-1]}, Event forecast: {event['forecast']}, actual: {event['actual']}")



