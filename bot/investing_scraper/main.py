from investing_scraper.InvestingDataScraper import InvestingDataScraper
import json
import asyncio
import os
from investing_scraper.investing_variables import investing_variables

async def fetch_all_data(pages_names):
    investing_scraper = InvestingDataScraper()
    # Fetch all pages asynchronously
    payload_update = {
        "currentTab": investing_variables.time_ranges.this_week, 
        "timeZone": investing_variables.time_zones.israel,
        "importance[]": [investing_variables.importance.high],
        }
    fetch_tasks = [investing_scraper.run(page_name, payload_update, True) for page_name in pages_names]
    events_by_dates = await asyncio.gather(*fetch_tasks)
    
    return events_by_dates

async def holiday_calendar():
    investing_scraper = InvestingDataScraper()
    payload_update = {
        "currentTab": investing_variables.time_ranges.this_week, 
        "timeZone": investing_variables.time_zones.eastern_us,
        }
    await investing_scraper.run("holiday_calendar", payload_update, True)

async def main():
    pages_names = ["economic_calendar", "earnings_calendar", "holiday_calendar"]

    # Fetch all data asynchronously
    await fetch_all_data(pages_names)
    # await holiday_calendar()


if __name__ == "__main__":
    asyncio.run(main())