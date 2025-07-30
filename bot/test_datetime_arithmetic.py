#!/usr/bin/env python3

from datetime import datetime, timedelta, time
import pytz

def test_datetime_arithmetic():
    """Test the datetime arithmetic conversion from time objects"""
    
    # Set up timezone (similar to the scheduler)
    timezone = pytz.timezone('Asia/Jerusalem')
    
    # Test time objects (similar to what we get from market schedule)
    market_open = time(9, 30)  # 9:30 AM
    market_close = time(16, 0)  # 4:00 PM
    
    print(f"Original time objects:")
    print(f"  Market open: {market_open} (type: {type(market_open)})")
    print(f"  Market close: {market_close} (type: {type(market_close)})")
    print()
    
    # Convert to datetime objects (same logic as in scheduler)
    today = datetime.now(timezone).date()
    market_open_dt = datetime.combine(today, market_open)
    market_close_dt = datetime.combine(today, market_close)
    
    print(f"Converted to datetime objects:")
    print(f"  Market open datetime: {market_open_dt} (type: {type(market_open_dt)})")
    print(f"  Market close datetime: {market_close_dt} (type: {type(market_close_dt)})")
    print()
    
    # Test arithmetic operations
    morning_news_time = market_open_dt - timedelta(minutes=30)  # 30 minutes before market open
    evening_news_time = market_close_dt + timedelta(minutes=1)  # 1 minute after market close
    
    print(f"Arithmetic operations:")
    print(f"  Morning news time: {morning_news_time} (30 min before open)")
    print(f"  Evening news time: {evening_news_time} (1 min after close)")
    print()
    
    # Test edge cases
    print(f"Edge case - early morning market:")
    early_market_open = time(6, 0)  # 6:00 AM
    early_market_dt = datetime.combine(today, early_market_open)
    early_morning_news = early_market_dt - timedelta(minutes=30)
    print(f"  Market open: {early_market_open}")
    print(f"  Morning news: {early_morning_news}")
    print()
    
    print(f"Edge case - late market close:")
    late_market_close = time(23, 30)  # 11:30 PM
    late_market_dt = datetime.combine(today, late_market_close)
    late_evening_news = late_market_dt + timedelta(minutes=1)
    print(f"  Market close: {late_market_close}")
    print(f"  Evening news: {late_evening_news}")
    print()
    
    # Test with None values (holiday case)
    print(f"Testing with None values (holiday case):")
    try:
        none_market_open = None
        if none_market_open is not None:
            none_market_dt = datetime.combine(today, none_market_open)
            print(f"  This should not execute")
        else:
            print(f"  Market open is None - holiday detected correctly")
    except Exception as e:
        print(f"  Error with None: {e}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_datetime_arithmetic() 