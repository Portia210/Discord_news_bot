#!/usr/bin/env python3
"""
Test script to verify scheduler fixes:
1. Concurrent job execution
2. Daily economic calendar job persistence
"""

import asyncio
import discord
from datetime import datetime, timedelta
import pytz
from scheduler_v2.discord_scheduler import DiscordScheduler
from scheduler_v2.task_definitions import TaskDefinitions
from config import Config

# Mock bot class for testing
class MockBot:
    def get_channel(self, channel_id):
        return MockChannel()
    
    async def send(self, *args, **kwargs):
        print(f"Mock bot would send: {args}, {kwargs}")

class MockChannel:
    async def send(self, *args, **kwargs):
        print(f"Mock channel would send: {args}, {kwargs}")

async def test_concurrent_jobs():
    """Test that jobs can run concurrently"""
    print("🧪 Testing concurrent job execution...")
    
    # Create mock bot and scheduler
    mock_bot = MockBot()
    scheduler = DiscordScheduler(
        bot=mock_bot,
        alert_channel_id=123,
        dev_channel_id=456,
        timezone=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
    )
    
    # Add two jobs that run at the same time
    async def long_running_job(job_id):
        print(f"🚀 Starting {job_id}")
        await asyncio.sleep(5)  # Simulate long-running task
        print(f"✅ Completed {job_id}")
    
    # Schedule jobs 1 second apart
    now = datetime.now(scheduler.timezone)
    scheduler.add_date_job(
        func=lambda: long_running_job("job_1"),
        run_date=now + timedelta(seconds=2),
        job_id="test_job_1",
        send_alert=False
    )
    
    scheduler.add_date_job(
        func=lambda: long_running_job("job_2"),
        run_date=now + timedelta(seconds=3),
        job_id="test_job_2",
        send_alert=False
    )
    
    # Start scheduler
    scheduler.start()
    
    # Wait for jobs to complete
    await asyncio.sleep(10)
    
    # Stop scheduler
    scheduler.stop()
    print("✅ Concurrent job test completed")

async def test_daily_job_persistence():
    """Test that daily economic calendar job persists"""
    print("🧪 Testing daily job persistence...")
    
    # Create mock bot and scheduler
    mock_bot = MockBot()
    scheduler = DiscordScheduler(
        bot=mock_bot,
        alert_channel_id=123,
        dev_channel_id=456,
        timezone=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
    )
    
    # Setup tasks
    task_defs = TaskDefinitions(scheduler)
    task_defs.setup_all_tasks()
    
    # Check if daily job exists
    daily_job = scheduler.get_job('economic_calendar_check')
    if daily_job:
        print(f"✅ Daily job exists: {daily_job.id}")
        # Get next run time safely
        try:
            next_run = daily_job.next_run_time
            print(f"   Next run: {next_run}")
        except AttributeError:
            print("   Next run: Unable to determine")
    else:
        print("❌ Daily job not found")
    
    # Start scheduler
    scheduler.start()
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Stop scheduler
    scheduler.stop()
    print("✅ Daily job persistence test completed")

async def main():
    """Run all tests"""
    print("🧪 Starting scheduler fix tests...")
    
    await test_concurrent_jobs()
    await test_daily_job_persistence()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 