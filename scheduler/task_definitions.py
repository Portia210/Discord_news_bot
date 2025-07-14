"""
Task Definitions - Define all your scheduled tasks here
"""

import asyncio
from datetime import datetime
from utils.logger import logger
from scheduler.tasks import Task, create_condition, parse_days
from scheduler.calendar_manager import CalendarManager


class TaskDefinitions:
    """Container for all task definitions"""
    
    def __init__(self, calendar_manager: CalendarManager):
        self.calendar_manager = calendar_manager
    
    async def daily_schedule_task(self):
        """Main daily schedule task - runs at 8:00 AM weekdays"""
        try:
            logger.info("🚀 Starting daily schedule...")
            
            # Step 1: Check for holidays
            is_holiday = await self.calendar_manager.check_holiday_calendar()
            if is_holiday:
                logger.info("🛑 Holiday detected - cancelling daily tasks")
                await self.calendar_manager.send_alert("🛑 **Daily tasks cancelled due to holiday**", 0xff0000)
                return
            
            # Step 2: Get economic events
            economic_events = await self.calendar_manager.get_economic_events()
            
            # Step 3: Schedule dynamic tasks for economic events
            await self.calendar_manager.schedule_economic_events(economic_events)
            
            logger.info(f"✅ Daily schedule completed - {len(economic_events)} events scheduled")
            
        except Exception as e:
            logger.error(f"❌ Error in daily schedule task: {e}")
    
    async def weekly_backup_task(self):
        """Weekly backup task - runs on Sunday at 9:00 AM"""
        try:
            logger.info("💾 Starting weekly backup...")
            await self.calendar_manager.send_alert("💾 **Weekly backup started**", 0x0000ff)
            
            # Add your backup logic here
            await asyncio.sleep(10)  # Simulate backup process
            
            await self.calendar_manager.send_alert("✅ **Weekly backup completed**", 0x00ff00)
            logger.info("✅ Weekly backup completed")
            
        except Exception as e:
            logger.error(f"❌ Error in weekly backup: {e}")
            await self.calendar_manager.send_alert(f"❌ **Weekly backup failed**: {e}", 0xff0000)
    
    async def market_open_check_task(self):
        """Market open check task - runs at 9:30 AM weekdays"""
        try:
            logger.info("🔍 Checking market open status...")
            
            # Add your market open check logic here
            # For example, check if market is open and send alert
            
            await self.calendar_manager.send_alert("📈 **Market open check completed**", 0x00ff00)
            logger.info("✅ Market open check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in market open check: {e}")
    
    async def daily_report_task(self):
        """Daily report task - runs at 2:30 PM weekdays"""
        try:
            logger.info("📊 Generating daily report...")
            
            # Add your daily report logic here
            # For example, generate PDF report
            
            await self.calendar_manager.send_alert("📊 **Daily report completed**", 0x00ff00)
            logger.info("✅ Daily report completed")
            
        except Exception as e:
            logger.error(f"❌ Error in daily report: {e}")
    
    def get_all_tasks(self) -> list[Task]:
        """Get all defined tasks"""
        return [
            # Daily schedule task (8:00 AM weekdays)
            Task(
                name="daily_schedule",
                func=self.daily_schedule_task,
                time_str="08:00",
                days=parse_days("mon-fri")
            ),
            
            # Weekly backup task (Sunday 9:00 AM)
            Task(
                name="weekly_backup",
                func=self.weekly_backup_task,
                time_str="09:00",
                days=["sun"]
            ),
            
            # Market open check (9:30 AM weekdays)
            Task(
                name="market_open_check",
                func=self.market_open_check_task,
                time_str="09:30",
                days=parse_days("mon-fri")
            ),
            
            # Daily report (2:30 PM weekdays)
            Task(
                name="daily_report",
                func=self.daily_report_task,
                time_str="14:30",
                days=parse_days("mon-fri")
            )
        ]


# Example of how to add new tasks:
"""
# To add a new task, simply add it to the get_all_tasks() method:

async def new_task(self):
    # Your task logic here
    pass

def get_all_tasks(self) -> list[Task]:
    return [
        # ... existing tasks ...
        
        # New task
        Task(
            name="new_task",
            func=self.new_task,
            time_str="15:00",
            days=parse_days("mon-fri")
        )
    ]
""" 