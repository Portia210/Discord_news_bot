"""
Custom Tasks - Add your bot-specific tasks here
"""

import asyncio
from datetime import datetime
from utils.logger import logger
from scheduler.tasks import Task, create_condition, parse_days
from scheduler.calendar_manager import CalendarManager


class CustomTasks:
    """Custom tasks specific to your Discord bot"""
    
    def __init__(self, calendar_manager: CalendarManager):
        self.calendar_manager = calendar_manager
    
    async def send_morning_greeting(self):
        """Send morning greeting to the channel"""
        try:
            logger.info("🌅 Sending morning greeting...")
            
            greeting = "🌅 **Good morning!** The trading day is about to begin."
            await self.calendar_manager.send_alert(greeting, 0x00ff00)
            
            logger.info("✅ Morning greeting sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending morning greeting: {e}")
    
    async def send_evening_summary(self):
        """Send evening summary to the channel"""
        try:
            logger.info("🌆 Sending evening summary...")
            
            summary = "🌆 **Trading day summary** - Check your positions and prepare for tomorrow."
            await self.calendar_manager.send_alert(summary, 0xffa500)
            
            logger.info("✅ Evening summary sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending evening summary: {e}")
    
    async def check_news_updates(self):
        """Check for news updates"""
        try:
            logger.info("📰 Checking news updates...")
            
            # Add your news checking logic here
            # For example, check RSS feeds, API endpoints, etc.
            
            await self.calendar_manager.send_alert("📰 **News check completed**", 0x00ff00)
            logger.info("✅ News check completed")
            
        except Exception as e:
            logger.error(f"❌ Error checking news: {e}")
    
    async def system_health_check(self):
        """Perform system health check"""
        try:
            logger.info("🏥 Performing system health check...")
            
            # Add your health check logic here
            # For example, check database connections, API endpoints, etc.
            
            await self.calendar_manager.send_alert("🏥 **System health check completed**", 0x00ff00)
            logger.info("✅ System health check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in system health check: {e}")
    
    def get_custom_tasks(self) -> list[Task]:
        """Get all custom tasks"""
        return [
            # Morning greeting (7:00 AM weekdays)
            Task(
                name="morning_greeting",
                func=self.send_morning_greeting,
                time_str="07:00",
                days=parse_days("mon-fri")
            ),
            
            # Evening summary (5:00 PM weekdays)
            Task(
                name="evening_summary",
                func=self.send_evening_summary,
                time_str="17:00",
                days=parse_days("mon-fri")
            ),
            
            # News check (10:00 AM weekdays)
            Task(
                name="news_check_10",
                func=self.check_news_updates,
                time_str="10:00",
                days=parse_days("mon-fri")
            ),
            
            # News check (12:00 PM weekdays)
            Task(
                name="news_check_12",
                func=self.check_news_updates,
                time_str="12:00",
                days=parse_days("mon-fri")
            ),
            
            # News check (2:00 PM weekdays)
            Task(
                name="news_check_14",
                func=self.check_news_updates,
                time_str="14:00",
                days=parse_days("mon-fri")
            ),
            
            # News check (4:00 PM weekdays)
            Task(
                name="news_check_16",
                func=self.check_news_updates,
                time_str="16:00",
                days=parse_days("mon-fri")
            ),
            
            # System health check (daily at 6:00 AM)
            Task(
                name="system_health",
                func=self.system_health_check,
                time_str="06:00",
                days=parse_days("mon-fri")
            )
        ]


# Example of how to integrate custom tasks with the main scheduler:
"""
# In your bot.py or wherever you initialize the scheduler:

# After initializing calendar_manager:
custom_tasks = CustomTasks(calendar_manager)

# Add custom tasks to the scheduler:
for task in custom_tasks.get_custom_tasks():
    scheduler.add_task(task)

# Or add them individually:
scheduler.add_task(custom_tasks.get_custom_tasks()[0])  # Add morning greeting
""" 