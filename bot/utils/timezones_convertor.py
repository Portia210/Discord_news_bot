from dateutil import parser
import pytz
from config import Config
from datetime import datetime, timedelta
import pandas as pd



def get_time_delta_for_date(date: str, target_tz: str, source_tz: str):
    # Set timezones
    tz_target = pytz.timezone(target_tz)
    tz_source = pytz.timezone(source_tz)

    date_obj = datetime.strptime(date, '%Y-%m-%d').date()

    dt_naive = datetime(date_obj.year, date_obj.month, date_obj.day, 12, 0, 0)  # Naive datetime
        
    # Calculate offset difference (Israel offset - US offset)
    target_offset = tz_target.utcoffset(dt_naive).total_seconds() / 3600
    source_offset = tz_source.utcoffset(dt_naive).total_seconds() / 3600
    delta_hours = target_offset - source_offset
    
    return {
        'date': date,
        'target_offset': target_offset,
        'source_offset': source_offset,
        'delta_hours': delta_hours
    }

def get_time_deltas_for_date_range(start_date: str, end_date: str, target_tz: str, source_tz: str):
    """returns dataframe with date and delta_hours"""
    results = []
    while start_date < end_date:
        results.append(get_time_delta_for_date(start_date, target_tz, source_tz))
        start_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    return pd.DataFrame(results, columns=['date', 'delta_hours']).sort_values(by='date')


def convert_iso_time_to_datetime(timestamp_str, timezone: str) -> datetime:
    """
    Convert any ISO timestamp to your timezone
    
    Args:
        timestamp_str: ISO timestamp (handles Z, +/-HH:MM, military letters, etc.)
        my_timezone: Your target timezone (default: Eastern Time)
    
    Returns:
        Formatted string in your timezone
    """
    # Military timezone mapping
    military_tz = {
        'A': '+01:00', 'B': '+02:00', 'C': '+03:00', 'D': '+04:00',
        'E': '+05:00', 'F': '+06:00', 'G': '+07:00', 'H': '+08:00',
        'I': '+09:00', 'K': '+10:00', 'L': '+11:00', 'M': '+12:00',
        'N': '-01:00', 'O': '-02:00', 'P': '-03:00', 'Q': '-04:00',
        'R': '-05:00', 'S': '-06:00', 'T': '-07:00', 'U': '-08:00',
        'V': '-09:00', 'W': '-10:00', 'X': '-11:00', 'Y': '-12:00',
        'Z': '+00:00'
    }
    
    timezone = pytz.timezone(timezone)
    # Handle military timezone letters
    if timestamp_str.endswith(tuple(military_tz.keys())):
        letter = timestamp_str[-1]
        offset = military_tz[letter]
        timestamp_str = timestamp_str[:-1] + offset
    
    # Parse the timestamp (handles all formats automatically)
    dt = parser.parse(timestamp_str)
    datetime_output = dt.astimezone(timezone)
    
    return datetime_output


if __name__ == "__main__":
    # Usage examples
    timestamps = [
        "2025-07-13T09:23:18Z",           # UTC with Z
        "2025-07-13T09:23:18A",           # Alpha time (UTC+1)
        "2025-07-13T09:23:18B",           # Bravo time (UTC+2)
    ]

    # Convert to Eastern Time
    for ts in timestamps:
        eastern_time = convert_iso_time_to_datetime(ts, pytz.timezone(Config.TIMEZONES.EASTERN_US))
        print(f"{ts} -> Eastern: {eastern_time}")
