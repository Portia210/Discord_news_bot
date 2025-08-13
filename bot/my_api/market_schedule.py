from datetime import datetime, timedelta
from utils import logger, get_time_deltas_for_date_range
from config import Config
from scrapers import InvestingScraper, InvestingParams
import asyncio
import pandas as pd
import re
import os

def get_weekday_for_date(date: str):
    "Date in format yyyy-mm-dd"
    return datetime.strptime(date, "%Y-%m-%d").weekday()


async def get_market_schedule_for_dates_range(start_date: str, end_date: str, target_tz, source_tz='America/New_York')-> pd.DataFrame:
    """returns dataframe with date and delta_hours"""
    scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY, timezone=target_tz)
    holiday_df = await scraper.get_calendar("holiday_calendar", 
                                InvestingParams.TIME_RANGES.CUSTOM, 
                                importance= InvestingParams.IMPORTANCE.APP_IMPORTANCES,
                                time_zone=InvestingParams.TIME_ZONES.ISRAEL, 
                                from_date=start_date,
                                to_date=end_date)
    if holiday_df is None:
        logger.error("No holiday data found")
        return None
    

    delta_df = get_time_deltas_for_date_range(start_date, end_date, target_tz, source_tz)
    # market open at 9:30am + delta_hours, close at 4:00pm + delta_hours (convert numbers to time)
    def apply_delta_and_convert_to_time(time_str, delta_hours):
        return (datetime.strptime(time_str, "%H:%M") + timedelta(hours=delta_hours)).strftime("%H:%M")
    
    delta_df['open_time'] = delta_df['delta_hours'].apply(lambda x: apply_delta_and_convert_to_time("09:30", x))
    delta_df['close_time'] = delta_df['delta_hours'].apply(lambda x: apply_delta_and_convert_to_time("16:00", x))

    # if date of week is 5 or 6, set open and close time to None
    delta_df['is_weekend'] = delta_df['date'].apply(lambda x: get_weekday_for_date(x) in [5, 6])
    # drop rows where is_weekend is True
    delta_df = delta_df.loc[~delta_df['is_weekend']]
    # if date in holidays_df, add "holiday" column which will be equal to holiday_df['holiday']
    for index, row in holiday_df.iterrows():
        delta_df.loc[delta_df['date'] == row['date'], 'holiday'] = row['holiday']
        if row['time'] == "all day":
            delta_df.loc[delta_df['date'] == row['date'], 'open_time'] = None
            delta_df.loc[delta_df['date'] == row['date'], 'close_time'] = None
        # check if match h:m pattern
        elif re.match(r'^\d{1,2}:\d{2}$', row['time']):
            delta_df.loc[delta_df['date'] == row['date'], 'close_time'] = row['time']
        elif row['time'] == "unknown time":
            logger.error(f"Unknown time for {row['date']}")

    output_df = delta_df[['date', 'open_time', 'close_time', 'holiday']].sort_values(by='date')
    return output_df




async def get_market_schedule_for_next_quarter(target_tz)-> pd.DataFrame:
    """returns dataframe with date and open_time, close_time, holiday"""

    output_file_path = "data/market_schedule.csv"

    today_date = datetime.now().strftime("%Y-%m-%d")
    quarter_from_now = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")

    # if df updated month forward, return the saved df
    if os.path.exists(output_file_path):
        df = pd.read_csv(output_file_path)
        month_from_now = (datetime.now() + timedelta(days=30))
        last_date = datetime.strptime(df.iloc[-1]['date'], "%Y-%m-%d")
        if month_from_now < last_date:
            logger.info(f"Market hours for next 90 days already exists")
            return df
   
    logger.info(f"Getting market hours for next 90 days")
    result = await get_market_schedule_for_dates_range(today_date, quarter_from_now, target_tz, source_tz=Config.TIMEZONES.EASTERN_US)
    result.to_csv(output_file_path, index=False)

    return result


if __name__ == "__main__":
    result = asyncio.run(get_market_schedule_for_next_quarter(Config.TIMEZONES.APP_TIMEZONE))