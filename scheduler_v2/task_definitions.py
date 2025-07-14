"""
Task Definitions V2 - Using APScheduler with cron expressions and specific dates
"""

import asyncio
from datetime import datetime, timedelta
from utils.logger import logger
from .discord_scheduler import DiscordScheduler
from .calendar_manager import CalendarManager


class TaskDefinitions:
    """Task definitions using APScheduler with cron expressions"""
    
    def __init__(self, discord_scheduler: DiscordScheduler, calendar_manager: CalendarManager):
        self.discord_scheduler = discord_scheduler
        self.calendar_manager = calendar_manager
    
    def setup_all_tasks(self):
        """Setup all scheduled tasks"""
        logger.info("📅 Setting up all scheduled tasks...")
        
        # Daily tasks (weekdays)
        self._setup_daily_tasks()
        
        # Weekly tasks
        self._setup_weekly_tasks()
        
        # Custom tasks
        self._setup_custom_tasks()
        
        # Future events scheduling
        self._setup_future_events()
        
        logger.info("✅ All tasks setup completed")
    
    def _setup_daily_tasks(self):
        """Setup daily recurring tasks"""
        
        # Daily schedule task (8:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.daily_schedule_task,
            cron_expression="0 8 * * 1-5",  # 8:00 AM Monday-Friday
            job_id="daily_schedule"
        )
        
        # Market open check (9:30 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.market_open_check_task,
            cron_expression="30 9 * * 1-5",  # 9:30 AM Monday-Friday
            job_id="market_open_check"
        )
        
        # Daily report (2:30 PM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.daily_report_task,
            cron_expression="30 14 * * 1-5",  # 2:30 PM Monday-Friday
            job_id="daily_report"
        )
        
        # Morning greeting (7:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.morning_greeting_task,
            cron_expression="0 7 * * 1-5",  # 7:00 AM Monday-Friday
            job_id="morning_greeting"
        )
        
        # Evening summary (5:00 PM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.evening_summary_task,
            cron_expression="0 17 * * 1-5",  # 5:00 PM Monday-Friday
            job_id="evening_summary"
        )
        
        # System health check (6:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=self.system_health_check_task,
            cron_expression="0 6 * * 1-5",  # 6:00 AM Monday-Friday
            job_id="system_health_check"
        )
        
        # News checks (multiple times during market hours)
        news_times = [
            ("0 10 * * 1-5", "news_check_10"),  # 10:00 AM
            ("0 12 * * 1-5", "news_check_12"),  # 12:00 PM
            ("0 14 * * 1-5", "news_check_14"),  # 2:00 PM
            ("0 16 * * 1-5", "news_check_16"),  # 4:00 PM
        ]
        
        for cron_expr, job_id in news_times:
            self.discord_scheduler.add_cron_job(
                func=self.news_check_task,
                cron_expression=cron_expr,
                job_id=job_id
            )
    
    def _setup_weekly_tasks(self):
        """Setup weekly recurring tasks"""
        
        # Weekly backup (Sunday 9:00 AM)
        self.discord_scheduler.add_cron_job(
            func=self.weekly_backup_task,
            cron_expression="0 9 * * 0",  # 9:00 AM Sunday
            job_id="weekly_backup"
        )
    
    def _setup_custom_tasks(self):
        """Setup custom tasks with specific dates"""
        
        # Example: Schedule a task for a specific date
        # You can add specific date tasks here
        pass
    
    def _setup_future_events(self):
        """Setup future events scheduling"""
        
        # Schedule future events check (daily at 7:30 AM)
        self.discord_scheduler.add_cron_job(
            func=self.schedule_future_events_task,
            cron_expression="30 7 * * 1-5",  # 7:30 AM Monday-Friday
            job_id="schedule_future_events"
        )
    
    # Task implementations
    async def daily_schedule_task(self):
        """Main daily schedule task - runs at 8:00 AM weekdays"""
        try:
            logger.info("🚀 Starting daily schedule...")
            
            # Step 1: Check for holidays
            is_holiday = await self.calendar_manager.check_holiday_calendar()
            if is_holiday:
                logger.info("🛑 Holiday detected - cancelling daily tasks")
                await self.discord_scheduler.send_alert(
                    "🛑 **Daily tasks cancelled due to holiday**", 
                    0xff0000,
                    "📅 Daily Schedule"
                )
                return
            
            # Step 2: Get economic events for today
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
            
            # Add your backup logic here
            await asyncio.sleep(10)  # Simulate backup process
            
            logger.info("✅ Weekly backup completed")
            
        except Exception as e:
            logger.error(f"❌ Error in weekly backup: {e}")
    
    async def market_open_check_task(self):
        """Market open check task - runs at 9:30 AM weekdays"""
        try:
            logger.info("🔍 Checking market open status...")
            
            # Add your market open check logic here
            # For example, check if market is open and send alert
            
            logger.info("✅ Market open check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in market open check: {e}")
    
    async def daily_report_task(self):
        """Daily report task - runs at 2:30 PM weekdays"""
        try:
            logger.info("📊 Generating daily report...")
            
            # Add your daily report logic here
            # For example, generate PDF report
            
            logger.info("✅ Daily report completed")
            
        except Exception as e:
            logger.error(f"❌ Error in daily report: {e}")
    
    async def morning_greeting_task(self):
        """Morning greeting task - runs at 7:00 AM weekdays"""
        try:
            logger.info("🌅 Sending morning greeting...")
            
            greeting = "🌅 **Good morning!** The trading day is about to begin."
            await self.discord_scheduler.send_alert(greeting, 0x00ff00, "🌅 Morning Greeting")
            
            logger.info("✅ Morning greeting sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending morning greeting: {e}")
    
    async def evening_summary_task(self):
        """Evening summary task - runs at 5:00 PM weekdays"""
        try:
            logger.info("🌆 Sending evening summary...")
            
            summary = "🌆 **Trading day summary** - Check your positions and prepare for tomorrow."
            await self.discord_scheduler.send_alert(summary, 0xffa500, "🌆 Evening Summary")
            
            logger.info("✅ Evening summary sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending evening summary: {e}")
    
    async def news_check_task(self):
        """News check task - runs multiple times during market hours"""
        try:
            logger.info("📰 Checking news updates...")
            
            # Add your news checking logic here
            # For example, check RSS feeds, API endpoints, etc.
            
            logger.info("✅ News check completed")
            
        except Exception as e:
            logger.error(f"❌ Error checking news: {e}")
    
    async def system_health_check_task(self):
        """System health check task - runs at 6:00 AM weekdays"""
        try:
            logger.info("🏥 Performing system health check...")
            
            # Add your health check logic here
            # For example, check database connections, API endpoints, etc.
            
            logger.info("✅ System health check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in system health check: {e}")
    
    async def schedule_future_events_task(self):
        """Schedule future events task - runs at 7:30 AM weekdays"""
        try:
            logger.info("📅 Scheduling future events...")
            
            # Schedule events for the next 7 days
            await self.calendar_manager.schedule_future_events(days_ahead=7)
            
            logger.info("✅ Future events scheduling completed")
            
        except Exception as e:
            logger.error(f"❌ Error scheduling future events: {e}")
    
    # Helper methods for adding specific date tasks
    def add_specific_date_task(self, func, run_date: datetime, job_id: str, **kwargs):
        """Add a task for a specific date"""
        return self.discord_scheduler.add_date_job(
            func=func,
            run_date=run_date,
            job_id=job_id,
            **kwargs
        )
    
    def add_cron_task(self, func, cron_expression: str, job_id: str, **kwargs):
        """Add a cron-based task"""
        return self.discord_scheduler.add_cron_job(
            func=func,
            cron_expression=cron_expression,
            job_id=job_id,
            **kwargs
        )
    
    def add_interval_task(self, func, seconds: int, job_id: str, **kwargs):
        """Add an interval-based task"""
        return self.discord_scheduler.add_interval_job(
            func=func,
            job_id=job_id,
            seconds=seconds,
            **kwargs
        ) 