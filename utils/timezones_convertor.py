from dateutil import parser
import pytz
from config import config
from datetime import datetime

def convert_to_my_timezone(timestamp_str, my_timezone=config.eastern_timezone):
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
    
    # Handle military timezone letters
    if timestamp_str.endswith(tuple(military_tz.keys())):
        letter = timestamp_str[-1]
        offset = military_tz[letter]
        timestamp_str = timestamp_str[:-1] + offset
    
    # Parse the timestamp (handles all formats automatically)
    dt = parser.parse(timestamp_str)
    converted_time = dt.astimezone(my_timezone)
    
    return converted_time


if __name__ == "__main__":
    # Usage examples
    timestamps = [
        "2025-07-13T09:23:18Z",           # UTC with Z
        "2025-07-13T09:23:18A",           # Alpha time (UTC+1)
        "2025-07-13T09:23:18B",           # Bravo time (UTC+2)
    ]

    # Convert to Eastern Time
    for ts in timestamps:
        eastern_time = convert_to_my_timezone(ts, config.eastern_timezone)
        print(f"{ts} -> Eastern: {eastern_time}")
