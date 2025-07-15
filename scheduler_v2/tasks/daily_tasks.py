"""
Daily Task Functions - Can be tested independently
"""

import asyncio
from datetime import datetime
from utils.logger import logger


async def daily_schedule_task(discord_scheduler=None, calendar_manager=None):
    """Main daily schedule task - runs at 8:00 AM weekdays"""
    try:
        logger.info("🚀 Starting daily schedule...")
        
        if calendar_manager:
            # Step 1: Check for holidays
            is_holiday = await calendar_manager.check_holiday_calendar()
            if is_holiday:
                logger.info("🛑 Holiday detected - cancelling daily tasks")
                if discord_scheduler:
                    await discord_scheduler.send_alert(
                        "🛑 **Daily tasks cancelled due to holiday**", 
                        0xff0000,
                        "📅 Daily Schedule"
                    )
                return
            
            # Step 2: Get economic events for today
            economic_events = await calendar_manager.get_economic_events()
            
            # Step 3: Schedule dynamic tasks for economic events
            await calendar_manager.schedule_economic_events(economic_events)
            
            logger.info(f"✅ Daily schedule completed - {len(economic_events)} events scheduled")
        else:
            logger.info("✅ Daily schedule task executed (no calendar manager)")
            
    except Exception as e:
        logger.error(f"❌ Error in daily schedule task: {e}")


async def market_open_check_task(discord_scheduler=None, calendar_manager=None):
    """Market open check task - runs at 9:30 AM weekdays"""
    try:
        logger.info("🔍 Checking market open status...")
        
        # Add your market open check logic here
        # For example, check if market is open and send alert
        
        if discord_scheduler:
            await discord_scheduler.send_alert("📈 **Market open check completed**", 0x00ff00)
        
        logger.info("✅ Market open check completed")
        
    except Exception as e:
        logger.error(f"❌ Error in market open check: {e}")


async def daily_report_task(discord_scheduler=None, calendar_manager=None):
    """Daily report task - runs at 2:30 PM weekdays"""
    try:
        logger.info("📊 Generating daily report...")
        
        # Add your daily report logic here
        # For example, generate PDF report
        
        if discord_scheduler:
            await discord_scheduler.send_alert("📊 **Daily report completed**", 0x00ff00)
        
        logger.info("✅ Daily report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in daily report: {e}")


async def morning_greeting_task(discord_scheduler=None, calendar_manager=None):
    """Morning greeting task - runs at 7:00 AM weekdays"""
    try:
        logger.info("🌅 Sending morning greeting...")
        
        greeting = "🌅 **Good morning!** The trading day is about to begin."
        
        if discord_scheduler:
            await discord_scheduler.send_alert(greeting, 0x00ff00, "🌅 Morning Greeting")
        else:
            print(f"🌅 {greeting}")
        
        logger.info("✅ Morning greeting sent")
        
    except Exception as e:
        logger.error(f"❌ Error sending morning greeting: {e}")


async def evening_summary_task(discord_scheduler=None, calendar_manager=None):
    """Evening summary task - runs at 5:00 PM weekdays"""
    try:
        logger.info("🌆 Sending evening summary...")
        
        summary = "🌆 **Trading day summary** - Check your positions and prepare for tomorrow."
        
        if discord_scheduler:
            await discord_scheduler.send_alert(summary, 0xffa500, "🌆 Evening Summary")
        else:
            print(f"🌆 {summary}")
        
        logger.info("✅ Evening summary sent")
        
    except Exception as e:
        logger.error(f"❌ Error sending evening summary: {e}")


async def news_check_task(discord_scheduler=None, calendar_manager=None):
    """News check task - runs multiple times during market hours"""
    try:
        logger.info("📰 Checking news updates...")
        
        # Add your news checking logic here
        # For example, check RSS feeds, API endpoints, etc.
        
        if discord_scheduler:
            await discord_scheduler.send_alert("📰 **News check completed**", 0x00ff00)
        
        logger.info("✅ News check completed")
        
    except Exception as e:
        logger.error(f"❌ Error checking news: {e}")


async def system_health_check_task(discord_scheduler=None, calendar_manager=None):
    """System health check task - runs at 6:00 AM weekdays"""
    try:
        logger.info("🏥 Performing system health check...")
        
        # Add your health check logic here
        # For example, check database connections, API endpoints, etc.
        
        if discord_scheduler:
            await discord_scheduler.send_alert("🏥 **System health check completed**", 0x00ff00)
        
        logger.info("✅ System health check completed")
        
    except Exception as e:
        logger.error(f"❌ Error in system health check: {e}")


async def schedule_future_events_task(discord_scheduler=None, calendar_manager=None):
    """Schedule future events task - runs at 7:30 AM weekdays"""
    try:
        logger.info("📅 Scheduling future events...")
        
        if calendar_manager:
            # Schedule events for the next 7 days
            await calendar_manager.schedule_future_events(days_ahead=7)
            logger.info("✅ Future events scheduling completed")
        else:
            logger.info("✅ Future events task executed (no calendar manager)")
            
    except Exception as e:
        logger.error(f"❌ Error scheduling future events: {e}") 