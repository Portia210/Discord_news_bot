from datetime import datetime
import re
from utils.logger import logger

def parse_hebrew_date(hebrew_date_str):
    """Convert Hebrew date string to datetime object"""
    
    # Hebrew month mapping
    hebrew_months = {
        'ינואר': 1, 'פברואר': 2, 'מרץ': 3, 'אפריל': 4,
        'מאי': 5, 'יוני': 6, 'יולי': 7, 'אוגוסט': 8,
        'ספטמבר': 9, 'אוקטובר': 10, 'נובמבר': 11, 'דצמבר': 12
    }
    
    # Hebrew day mapping
    hebrew_days = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת"]
    
    try:
        # Extract components using regex
        # יום שלישי, 15 ביולי, 2025
        pattern = r'יום (\w+), (\d+) ב(\w+), (\d{4})'
        match = re.match(pattern, hebrew_date_str)
        
        if match:
            day_name, month_day, month_name, year = match.groups()
            
            if day_name not in hebrew_days:
                logger.warning(f"Unknown Hebrew day: {day_name}")
            
            # Convert Hebrew month name to number
            month = hebrew_months.get(month_name)
            if not month:
                raise ValueError(f"Unknown Hebrew month: {month_name}")
            
            # Create datetime object
            dt = datetime(int(year), month, int(month_day))
            

            return dt
        else:
            raise ValueError("Date format not recognized")
            
    except Exception as e:
        logger.error(f"Error parsing Hebrew date: {e}")
        return None

if __name__ == "__main__":  
# Test it
    hebrew_date = "יום שלישי, 15 ביולי, 2025"
    dt = parse_hebrew_date(hebrew_date)
    print(dt)  # 2025-07-15 00:00:00
    print(dt.strftime("%Y-%m-%d"))  # 2025-07-15