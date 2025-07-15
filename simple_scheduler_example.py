#!/usr/bin/env python3
"""
Simple APScheduler & DiscordScheduler Example
A beginner-friendly guide to understand scheduling concepts
"""

import asyncio
import discord
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from config import config
from scheduler_v2 import DiscordScheduler

# ============================================================================
# STEP 1: Basic APScheduler Example (No Discord)
# ============================================================================

async def basic_apscheduler_example():
    """Basic APScheduler without Discord integration"""
    print("🔍 Basic APScheduler Example")
    print("=" * 50)
    
    # Create a simple scheduler
    scheduler = AsyncIOScheduler(timezone=config.app_timezone)
    
    # Task 1: Simple function that prints current time
    async def print_time():
        now = datetime.now(config.app_timezone)
        print(f"🕐 Current time: {now.strftime('%H:%M:%S')}")
    
    # Task 2: Function that counts executions
    counter = 0
    async def count_executions():
        nonlocal counter
        counter += 1
        print(f"🔢 Execution #{counter}")
    
    # Task 3: Function that shows a message
    async def show_message():
        print("💬 Hello from scheduled task!")
    
    # Add different types of jobs
    print("📅 Adding jobs...")
    
    # Job 1: Run every 10 seconds (interval)
    scheduler.add_job(
        print_time,
        IntervalTrigger(seconds=10),
        id="print_time",
        replace_existing=True
    )
    print("✅ Added: Print time every 10 seconds")
    
    # Job 2: Run every 30 seconds (interval)
    scheduler.add_job(
        count_executions,
        IntervalTrigger(seconds=30),
        id="count_executions",
        replace_existing=True
    )
    print("✅ Added: Count executions every 30 seconds")
    
    # Job 3: Run in 1 minute (one-time)
    future_time = datetime.now(config.app_timezone) + timedelta(minutes=1)
    scheduler.add_job(
        show_message,
        DateTrigger(run_date=future_time),
        id="show_message",
        replace_existing=True
    )
    print(f"✅ Added: Show message at {future_time.strftime('%H:%M:%S')}")
    
    # Start the scheduler
    print("\n🚀 Starting scheduler...")
    scheduler.start()
    
    # Let it run for 2 minutes
    print("⏰ Running for 2 minutes...")
    await asyncio.sleep(120)
    
    # Stop the scheduler
    scheduler.shutdown()
    print("🛑 Scheduler stopped")
    print()

# ============================================================================
# STEP 2: Cron Jobs Example
# ============================================================================

async def cron_jobs_example():
    """Example of cron-based scheduling"""
    print("🔍 Cron Jobs Example")
    print("=" * 50)
    
    scheduler = AsyncIOScheduler(timezone=config.app_timezone)
    
    # Task: Print current time and day
    async def print_time_and_day():
        now = datetime.now(config.app_timezone)
        day_name = now.strftime('%A')
        print(f"📅 {day_name} at {now.strftime('%H:%M:%S')}")
    
    # Add cron jobs with different patterns
    print("📅 Adding cron jobs...")
    
    # Job 1: Every minute (for demonstration)
    scheduler.add_job(
        print_time_and_day,
        CronTrigger.from_crontab("* * * * *", timezone=config.app_timezone),
        id="every_minute",
        replace_existing=True
    )
    print("✅ Added: Every minute")
    
    # Job 2: Every 2 minutes
    scheduler.add_job(
        lambda: print("🔄 Every 2 minutes task"),
        CronTrigger.from_crontab("*/2 * * * *", timezone=config.app_timezone),
        id="every_2_minutes",
        replace_existing=True
    )
    print("✅ Added: Every 2 minutes")
    
    # Job 3: At specific times (if current minute is 0, 15, 30, or 45)
    current_minute = datetime.now(config.app_timezone).minute
    if current_minute in [0, 15, 30, 45]:
        scheduler.add_job(
            lambda: print("🎯 Quarter-hour task"),
            CronTrigger.from_crontab("0,15,30,45 * * * *", timezone=config.app_timezone),
            id="quarter_hour",
            replace_existing=True
        )
        print("✅ Added: Every quarter hour")
    
    # Start and run for 3 minutes
    print("\n🚀 Starting cron scheduler...")
    scheduler.start()
    await asyncio.sleep(180)
    scheduler.shutdown()
    print("🛑 Cron scheduler stopped")
    print()

# ============================================================================
# STEP 3: DiscordScheduler Example (Mock Discord)
# ============================================================================

class MockDiscordBot:
    """Mock Discord bot for testing"""
    def get_channel(self, channel_id):
        class MockChannel:
            def __init__(self, channel_id):
                self.id = channel_id
                self.name = "test_channel"
            
            async def send(self, embed):
                print(f"📨 [Discord] {embed.title}: {embed.description}")
        
        return MockChannel(channel_id)

async def discord_scheduler_example():
    """Example using DiscordScheduler with mock Discord"""
    print("🔍 DiscordScheduler Example")
    print("=" * 50)
    
    # Create mock bot and scheduler
    mock_bot = MockDiscordBot()
    scheduler = DiscordScheduler(
        bot=mock_bot,
        dev_channel_id=123456789,
        timezone=config.app_timezone
    )
    
    # Task 1: Simple greeting
    async def morning_greeting():
        await scheduler.send_alert(
            "🌅 Good morning! Have a great day!",
            0x00ff00,
            "🌅 Morning Greeting"
        )
    
    # Task 2: Weather check (simulated)
    async def weather_check():
        weather = "☀️ Sunny and 25°C"
        await scheduler.send_alert(
            f"🌤️ Weather Update: {weather}",
            0x00ff00,
            "🌤️ Weather"
        )
    
    # Task 3: Reminder task
    async def reminder_task():
        await scheduler.send_alert(
            "⏰ Don't forget to take a break!",
            0xffa500,
            "⏰ Reminder"
        )
    
    # Add jobs
    print("📅 Adding DiscordScheduler jobs...")
    
    # Job 1: Greeting every 2 minutes
    scheduler.add_cron_job(
        morning_greeting,
        cron_expression="*/2 * * * *",
        job_id="morning_greeting",
        send_alert=False  # Don't send scheduler status
    )
    print("✅ Added: Morning greeting every 2 minutes")
    
    # Job 2: Weather check every 3 minutes
    scheduler.add_cron_job(
        weather_check,
        cron_expression="*/3 * * * *",
        job_id="weather_check",
        send_alert=False
    )
    print("✅ Added: Weather check every 3 minutes")
    
    # Job 3: Reminder in 1 minute
    future_time = datetime.now(config.app_timezone) + timedelta(minutes=1)
    scheduler.add_date_job(
        reminder_task,
        run_date=future_time,
        job_id="reminder_task",
        send_alert=False
    )
    print(f"✅ Added: Reminder at {future_time.strftime('%H:%M:%S')}")
    
    # Start scheduler
    print("\n🚀 Starting DiscordScheduler...")
    scheduler.start()
    
    # Run for 2 minutes
    print("⏰ Running for 2 minutes...")
    await asyncio.sleep(120)
    
    # Stop scheduler
    scheduler.stop()
    print("🛑 DiscordScheduler stopped")
    print()

# ============================================================================
# STEP 4: Interactive Example
# ============================================================================

async def interactive_example():
    """Interactive example where you can see jobs being added"""
    print("🔍 Interactive Example")
    print("=" * 50)
    
    scheduler = AsyncIOScheduler(timezone=config.app_timezone)
    
    # Task that shows job information
    async def show_job_info(job_name):
        now = datetime.now(config.app_timezone)
        print(f"🎯 {job_name} executed at {now.strftime('%H:%M:%S')}")
    
    # Add jobs with different timing
    print("📅 Adding interactive jobs...")
    
    # Immediate job (runs in 5 seconds)
    scheduler.add_job(
        lambda: show_job_info("Immediate"),
        DateTrigger(run_date=datetime.now(config.app_timezone) + timedelta(seconds=5)),
        id="immediate_job"
    )
    print("✅ Added: Immediate job (5 seconds)")
    
    # Short interval job
    scheduler.add_job(
        lambda: show_job_info("Short Interval"),
        IntervalTrigger(seconds=15),
        id="short_interval"
    )
    print("✅ Added: Short interval (15 seconds)")
    
    # Long interval job
    scheduler.add_job(
        lambda: show_job_info("Long Interval"),
        IntervalTrigger(seconds=45),
        id="long_interval"
    )
    print("✅ Added: Long interval (45 seconds)")
    
    # Start and show job count
    scheduler.start()
    print(f"📊 Total jobs: {len(scheduler.get_jobs())}")
    
    # Run for 1 minute
    print("⏰ Running for 1 minute...")
    await asyncio.sleep(60)
    
    scheduler.shutdown()
    print("🛑 Interactive example stopped")
    print()

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Run all examples"""
    print("🚀 Simple APScheduler & DiscordScheduler Examples")
    print("=" * 60)
    print("This will demonstrate basic scheduling concepts step by step.")
    print("Each example runs for a few minutes to show the behavior.")
    print()
    
    try:
        # Run examples one by one
        await basic_apscheduler_example()
        await cron_jobs_example()
        await discord_scheduler_example()
        await interactive_example()
        
        print("🎉 All examples completed!")
        print("\n📚 What you learned:")
        print("• Basic APScheduler setup and usage")
        print("• Different trigger types (Interval, Date, Cron)")
        print("• Cron expression patterns")
        print("• DiscordScheduler integration")
        print("• Job management and monitoring")
        
    except KeyboardInterrupt:
        print("\n⏹️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 