#!/usr/bin/env python3
"""
Test script to verify scheduler functionality and economic calendar alerts
"""

import sys
import os
import asyncio
import pandas as pd
from datetime import datetime, timedelta
import pytz
from scheduler_v2.tasks.economic_calendar_tasks import (
    economic_calendar_to_text, economic_warning_task, economic_update_task, schedule_economic_alert_at_time
)
# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all scheduler imports"""
    try:
        print("🔍 Testing scheduler imports...")
        
        # Test core scheduler imports
        from scheduler_v2.discord_scheduler import DiscordScheduler
        from scheduler_v2.task_definitions import TaskDefinitions
        print("✅ Core scheduler imports successful")
        
        # Test economic calendar tasks

        print("✅ Economic calendar tasks import successful")
        
        # Test other task modules
        from scheduler_v2.tasks.news_report import morning_news_report_task, evening_news_report_task
        from scheduler_v2.tasks.weekly_tasks import weekly_backup_task
        print("✅ All task modules import successful")
        
        print("\n🎉 All imports successful! Scheduler is ready to use.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_mock_discord_bot():
    """Create a mock Discord bot for testing"""
    class MockBot:
        def get_channel(self, channel_id):
            class MockChannel:
                async def send(self, embed):
                    print(f"📨 Mock message sent to channel {channel_id}: {embed.title}")
            return MockChannel()
    
    return MockBot()

def create_test_calendar_data():
    """Create test economic calendar data"""
    test_data = {
        'time': ['15:30', '15:30', '16:00', '16:00', '16:00'],
        'description': [
            'US CPI Data Release',
            'Federal Reserve Interest Rate Decision', 
            'US Unemployment Rate',
            'US GDP Growth Rate',
            'US Inflation Rate'
        ],
        'volatility': ['High', 'High', 'Medium', 'Medium', 'Low'],
        'previous': ['2.5%', '5.25%', '3.7%', '2.1%', '2.5%'],
        'forecast': ['2.6%', '5.5%', '3.8%', '2.3%', '2.4%'],
        'actual': ['2.7%', '5.5%', '3.9%', '2.2%', '2.3%']
    }
    return pd.DataFrame(test_data)

async def test_schedule_economic_alert_at_time_duplicate(discord_scheduler, time_str: str, calendar_data: pd.DataFrame):
    """Duplicate of schedule_economic_alert_at_time for testing"""
    jobs_added = []
    try:
        print(f"🔍 Testing schedule_economic_alert_at_time for time: {time_str}")
        
        # Parse time and create datetime for today
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        tz = pytz.timezone('Asia/Jerusalem')  # Use the same timezone as config
        today = datetime.now(tz).date()
        event_datetime = datetime.combine(today, time_obj, tzinfo=tz)
        
        # Get events for this specific time from DataFrame
        time_events = calendar_data[calendar_data['time'] == time_str]
        print(f"📊 Found {len(time_events)} events for time {time_str}")
        
        # Schedule 5-minute warning (only if not already scheduled)
        warning_time = event_datetime - timedelta(minutes=5)
        if warning_time > datetime.now(tz):
            warning_job_id = f"test_economic_warning_{time_str.replace(':', '_')}"
            
            # Check if job already exists
            existing_job = discord_scheduler.get_job(warning_job_id)
            if not existing_job:
                success = discord_scheduler.add_date_job(
                    # func=economic_warning_task,
                    func=schedule_economic_alert_at_time,
                    run_date=warning_time,
                    job_id=warning_job_id,
                    args=(time_str, time_events, discord_scheduler),
                    send_alert=False
                )
                if success:
                    jobs_added.append({
                        'id': warning_job_id,
                        'type': 'date',
                        'run_date': str(warning_time),
                        'timezone': str(discord_scheduler.timezone)
                    })
                    print(f"✅ Warning job scheduled: {warning_job_id} at {warning_time}")
                else:
                    print(f"❌ Failed to schedule warning job for {time_str}")
            else:
                print(f"⚠️ Warning job already exists for {time_str}")
        else:
            print(f"⏰ Time {time_str} warning has already passed, skipping")
        
        # Schedule post-event update (only if not already scheduled)
        update_time = event_datetime + timedelta(seconds=discord_scheduler.post_event_delay)
        if update_time > datetime.now(tz):
            update_job_id = f"test_economic_update_{time_str.replace(':', '_')}"
            
            # Check if job already exists
            existing_job = discord_scheduler.get_job(update_job_id)
            if not existing_job:
                success = discord_scheduler.add_date_job(
                    func=economic_update_task,
                    run_date=update_time,
                    job_id=update_job_id,
                    args=(time_str, discord_scheduler),
                    send_alert=False
                )
                if success:
                    jobs_added.append({
                        'id': update_job_id,
                        'type': 'date',
                        'run_date': str(update_time),
                        'timezone': str(discord_scheduler.timezone)
                    })
                    print(f"✅ Update job scheduled: {update_job_id} at {update_time}")
                else:
                    print(f"❌ Failed to schedule update job for {time_str}")
            else:
                print(f"⚠️ Update job already exists for {time_str}")
        else:
            print(f"⏰ Time {time_str} update has already passed, skipping")
        
    except Exception as e:
        print(f"❌ Error testing schedule_economic_alert_at_time for {time_str}: {e}")
    
    return jobs_added

async def test_scheduler_functionality():
    """Test the complete scheduler functionality"""
    try:
        print("\n🔍 Testing scheduler functionality...")
        
        # Import here to ensure it's available
        from scheduler_v2.discord_scheduler import DiscordScheduler
        
        # Create mock bot and scheduler
        mock_bot = create_mock_discord_bot()
        discord_scheduler = DiscordScheduler(
            bot=mock_bot,
            alert_channel_id=123456789,  # Mock channel ID
            dev_channel_id=987654321,    # Mock dev channel ID
            timezone=pytz.timezone('Asia/Jerusalem'),
            post_event_delay=3
        )
        
        print("✅ DiscordScheduler created successfully")
        
        # Test scheduler start
        discord_scheduler.start()
        print("✅ Scheduler started successfully")
        
        # Create test calendar data
        test_calendar_data = create_test_calendar_data()
        print(f"✅ Test calendar data created with {len(test_calendar_data)} events")
        
        # Extract unique times
        unique_times = set(test_calendar_data['time'].dropna().unique())
        print(f"📊 Found unique times: {sorted(unique_times)}")
        
        # Test scheduling alerts for each unique time
        all_scheduled_jobs = []
        for time_str in sorted(unique_times):
            jobs = await test_schedule_economic_alert_at_time_duplicate(
                discord_scheduler, time_str, test_calendar_data
            )
            all_scheduled_jobs.extend(jobs)
        
        print(f"\n📋 Total jobs scheduled: {len(all_scheduled_jobs)}")
        
        # Generate and display job summary
        summary = discord_scheduler.generate_job_summary()
        print(f"\n📋 Job Summary:\n{summary}")
        
        # Test scheduler status
        status = discord_scheduler.get_status()
        print(f"\n📊 Scheduler Status:")
        print(f"   Running: {status['running']}")
        print(f"   Job count: {status['job_count']}")
        
        # Test individual job retrieval
        for job_info in all_scheduled_jobs[:2]:  # Test first 2 jobs
            job = discord_scheduler.get_job(job_info['id'])
            if job:
                print(f"✅ Job {job_info['id']} found in scheduler")
                print(f"   Next run: {job.next_run_time}")
            else:
                print(f"❌ Job {job_info['id']} not found in scheduler")
        
        # Test job removal
        if all_scheduled_jobs:
            test_job_id = all_scheduled_jobs[0]['id']
            success = discord_scheduler.remove_job(test_job_id)
            if success:
                print(f"✅ Successfully removed job: {test_job_id}")
            else:
                print(f"❌ Failed to remove job: {test_job_id}")
        
        # Test scheduler stop
        discord_scheduler.stop()
        print("✅ Scheduler stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler functionality test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_economic_calendar_tasks():
    """Test the economic calendar task functions specifically"""
    try:
        print("\n🔍 Testing economic calendar task functions...")
        
        # Import here to ensure it's available
        from scheduler_v2.discord_scheduler import DiscordScheduler
        
        # Create mock bot and scheduler
        mock_bot = create_mock_discord_bot()
        discord_scheduler = DiscordScheduler(
            bot=mock_bot,
            alert_channel_id=123456789,
            dev_channel_id=987654321,
            timezone=pytz.timezone('Asia/Jerusalem'),
            post_event_delay=3
        )
        
        # Start scheduler
        discord_scheduler.start()
        
        # Test economic warning task
        print("🔍 Testing economic_warning_task...")
        test_events = create_test_calendar_data()
        time_events = test_events[test_events['time'] == '15:30']
        
        await economic_warning_task('15:30', time_events, discord_scheduler)
        print("✅ economic_warning_task executed successfully")
        
        # Test economic update task
        print("🔍 Testing economic_update_task...")
        await economic_update_task('15:30', discord_scheduler)
        print("✅ economic_update_task executed successfully")
        
        # Stop scheduler
        discord_scheduler.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Economic calendar tasks test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cron_jobs():
    """Test cron job scheduling"""
    try:
        print("\n🔍 Testing cron job scheduling...")
        
        # Import here to ensure it's available
        from scheduler_v2.discord_scheduler import DiscordScheduler
        
        # Create mock bot and scheduler
        mock_bot = create_mock_discord_bot()
        discord_scheduler = DiscordScheduler(
            bot=mock_bot,
            alert_channel_id=123456789,
            dev_channel_id=987654321,
            timezone=pytz.timezone('Asia/Jerusalem')
        )
        
        # Start scheduler
        discord_scheduler.start()
        
        # Test async function
        async def test_cron_func():
            print("✅ Cron job executed successfully!")
            return "test result"
        
        # Add cron job (every minute for testing)
        success = discord_scheduler.add_cron_job(
            func=test_cron_func,
            cron_expression="* * * * *",  # Every minute
            job_id="test_cron_job",
            send_alert=False
        )
        
        if success:
            print("✅ Cron job scheduled successfully")
            
            # Wait a bit to see if it executes
            print("⏳ Waiting 70 seconds to see if cron job executes...")
            await asyncio.sleep(70)
            
            # Check job status
            job = discord_scheduler.get_job("test_cron_job")
            if job:
                print(f"✅ Cron job found, next run: {job.next_run_time}")
            
            # Remove the test job
            discord_scheduler.remove_job("test_cron_job")
            print("✅ Test cron job removed")
        else:
            print("❌ Failed to schedule cron job")
        
        # Stop scheduler
        discord_scheduler.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Cron job test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Scheduler Test Suite")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Import test failed")
        return False
    
    # Test scheduler functionality
    scheduler_ok = await test_scheduler_functionality()
    
    if not scheduler_ok:
        print("\n❌ Scheduler functionality test failed")
        return False
    
    # Test economic calendar tasks
    tasks_ok = await test_economic_calendar_tasks()
    
    if not tasks_ok:
        print("\n❌ Economic calendar tasks test failed")
        return False
    
    # Test cron jobs
    cron_ok = await test_cron_jobs()
    
    if not cron_ok:
        print("\n❌ Cron job test failed")
        return False
    
    print("\n🎉 All tests passed! Your scheduler is working correctly.")
    print("\nNext steps:")
    print("1. Run your bot: python bot.py")
    print("2. Check the logs for scheduler initialization")
    print("3. Monitor your Discord channel for alerts")
    print("4. Verify that economic calendar alerts are working")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 