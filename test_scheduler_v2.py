#!/usr/bin/env python3
"""
Test script for Scheduler V2 - APScheduler-based scheduler
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all scheduler V2 imports"""
    try:
        print("🔍 Testing Scheduler V2 imports...")
        
        # Test core imports
        from scheduler_v2 import DiscordScheduler, CalendarManager, TaskDefinitions
        print("✅ Core scheduler V2 imports successful")
        
        # Test APScheduler imports
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.date import DateTrigger
        print("✅ APScheduler imports successful")
        
        print("\n🎉 All imports successful! Scheduler V2 is ready to use.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_scheduler_functionality():
    """Test basic scheduler functionality"""
    try:
        print("\n🔍 Testing scheduler functionality...")
        
        from scheduler_v2 import DiscordScheduler
        
        # Create a mock bot and scheduler
        class MockBot:
            def get_channel(self, channel_id):
                return None  # Mock channel
        
        mock_bot = MockBot()
        scheduler = DiscordScheduler(mock_bot, 123456789)
        
        # Test cron job addition
        async def test_task():
            print("✅ Test task executed!")
        
        success = scheduler.add_cron_job(
            func=test_task,
            cron_expression="0 8 * * 1-5",
            job_id="test_cron_job"
        )
        
        if success:
            print("✅ Cron job addition successful")
        else:
            print("❌ Cron job addition failed")
            return False
        
        # Test date job addition
        future_date = datetime.now() + timedelta(minutes=1)
        success = scheduler.add_date_job(
            func=test_task,
            run_date=future_date,
            job_id="test_date_job"
        )
        
        if success:
            print("✅ Date job addition successful")
        else:
            print("❌ Date job addition failed")
            return False
        
        # Test job count
        job_count = scheduler.get_job_count()
        print(f"✅ Job count: {job_count}")
        
        # Test job removal
        success = scheduler.remove_job("test_cron_job")
        if success:
            print("✅ Job removal successful")
        else:
            print("❌ Job removal failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler functionality test failed: {e}")
        return False

def test_cron_expressions():
    """Test cron expression parsing"""
    try:
        print("\n🔍 Testing cron expressions...")
        
        from apscheduler.triggers.cron import CronTrigger
        
        # Test various cron expressions
        test_expressions = [
            "0 8 * * 1-5",      # 8:00 AM weekdays
            "30 9 * * 1-5",     # 9:30 AM weekdays
            "0 9 * * 0",        # 9:00 AM Sunday
            "0 6 * * *",        # 6:00 AM daily
            "0 10,12,14,16 * * 1-5",  # Multiple times
        ]
        
        for expr in test_expressions:
            try:
                trigger = CronTrigger.from_crontab(expr)
                print(f"✅ Cron expression valid: {expr}")
            except Exception as e:
                print(f"❌ Cron expression invalid: {expr} - {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Cron expression test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Scheduler V2 Test Suite")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    if imports_ok:
        # Test cron expressions
        cron_ok = test_cron_expressions()
        
        if cron_ok:
            # Test scheduler functionality
            scheduler_ok = await test_scheduler_functionality()
            
            if scheduler_ok:
                print("\n🎉 All tests passed! Scheduler V2 is working correctly.")
                print("\nNext steps:")
                print("1. Run the new bot: python bot_v2.py")
                print("2. Check the logs for scheduler initialization")
                print("3. Monitor your Discord channel for alerts")
                print("4. Try adding specific date tasks")
            else:
                print("\n❌ Scheduler functionality test failed")
                sys.exit(1)
        else:
            print("\n❌ Cron expression test failed")
            sys.exit(1)
    else:
        print("\n❌ Import test failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 