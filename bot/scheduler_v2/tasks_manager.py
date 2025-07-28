"""
Task Definitions V2 - Using APScheduler with cron expressions and specific dates
"""

import asyncio
from datetime import datetime, timedelta
from utils.logger import logger
from .discord_scheduler import DiscordScheduler

from .tasks.news_report_tasks import (
    morning_news_report_task,
    evening_news_report_task
)
from .tasks.economic_calendar_tasks import get_economic_calendar_task
from .tasks.weekly_tasks import weekly_backup_task
from time import time
from config import Config

class TasksManager:
    """Task definitions using APScheduler with cron expressions"""
    
    def __init__(self, discord_scheduler: DiscordScheduler):
        self.discord_scheduler = discord_scheduler
    
    def setup_all_tasks(self):
        """Setup all scheduled tasks"""
        logger.info("📅 Setting up all scheduled tasks...")
        
        
        self._setup_startup_tasks()
        
        # Daily gatekeeper task
        self._setup_daily_tasks()
        
        # Weekly tasks
        self._setup_weekly_tasks()
        
        # Custom tasks
        self._setup_custom_tasks()
        
       
        
        logger.info("✅ All tasks setup completed")

    def _setup_startup_tasks(self):
        """Setup startup tasks"""
        # Conditional startup task - only run if after 8:00 AM
        current_time = datetime.now(self.discord_scheduler.timezone)
        current_hour = current_time.hour
        
        if current_hour >= 8:
        # if False:
            logger.info("🌅 After 8:00 AM - Running economic calendar startup task")
            self.discord_scheduler.add_date_job(
                func=lambda: get_economic_calendar_task(self.discord_scheduler),
                run_date=current_time + timedelta(seconds=5),
                job_id="economic_calendar_startup"
            )
            # logger.info("🌅 news report startup task")
            # self.discord_scheduler.add_date_job(
            #     func=lambda: morning_news_report_task(self.discord_scheduler),
            #     run_date=current_time + timedelta(seconds=5),
            #     job_id="morning_news_report_startup"
            # )
        else:
            logger.info("🌙 Before 8:00 AM - Skipping startup task, waiting for daily cron job")
    


    def _setup_daily_tasks(self):
        """Setup daily gatekeeper task"""
        
        # Daily gatekeeper task - runs first thing in the morning
        self.discord_scheduler.add_cron_job(
            func=lambda: self.daily_gatekeeper(),
            cron_expression="30 7 * * *",  # 7:30 AM daily
            job_id="daily_gatekeeper"
        )

    def daily_gatekeeper(self):
        """Main gatekeeper that checks conditions and sets up today's tasks"""
        logger.info("🚪 Daily gatekeeper starting...")
        
        # Check if today is a holiday
        if self.is_holiday_today():
            logger.info("🏖️ Holiday detected - setting up holiday tasks")
            self.setup_holiday_tasks()
            return
        
        # Get market times for today
        market_open, market_close = self.get_market_times_today()
        
        logger.info(f"📈 Market times for today: Open {market_open.strftime('%H:%M')}, Close {market_close.strftime('%H:%M')}")
        
        # Set up regular tasks with market times
        self.setup_regular_tasks(market_open, market_close)

    def setup_holiday_tasks(self):
        """Setup tasks for holiday days (currently empty)"""
        logger.info("🏖️ Setting up holiday tasks (no tasks scheduled)")
        # Keep empty for now - no tasks on holidays
        pass

    def setup_regular_tasks(self, market_open: datetime, market_close: datetime):
        """Setup regular daily tasks with market times"""
        logger.info(f"📅 Setting up regular tasks for today")
        
        # Calculate task times based on market times
        morning_news_time = market_open - timedelta(minutes=30)  # 30 minutes before market open
        evening_news_time = market_close + timedelta(minutes=1)  # 1 minute after market close
        
        logger.info(f"   - Morning news report: {morning_news_time.strftime('%H:%M')}")
        logger.info(f"   - Evening news report: {evening_news_time.strftime('%H:%M')}")
        
        # Morning news report
        self.discord_scheduler.add_date_job(
            func=lambda: morning_news_report_task(self.discord_scheduler),
            run_date=morning_news_time,
            job_id="morning_news_report_today"
        )
        
        # Evening news report
        self.discord_scheduler.add_date_job(
            func=lambda: evening_news_report_task(self.discord_scheduler),
            run_date=evening_news_time,
            job_id="evening_news_report_today"
        )
        
        # Economic calendar check (8:00 AM weekdays)
        if datetime.now(self.discord_scheduler.timezone).weekday() < 5:  # Monday-Friday
            economic_time = datetime.now(self.discord_scheduler.timezone).replace(
                hour=8, minute=0, second=0, microsecond=0
            )
            self.discord_scheduler.add_date_job(
                func=lambda: get_economic_calendar_task(self.discord_scheduler),
                run_date=economic_time,
                job_id="economic_calendar_today"
            )
            logger.info(f"   - Economic calendar: {economic_time.strftime('%H:%M')}")

    def get_market_times_today(self):
        """Get today's market opening and closing times"""
        current_time = datetime.now(self.discord_scheduler.timezone)
        
        # Check if it's DST
        is_dst = current_time.dst() != timedelta(0)
        
        if is_dst:
            # Summer time - market opens at 15:00, closes at 22:00
            market_open = current_time.replace(hour=15, minute=0, second=0, microsecond=0)
            market_close = current_time.replace(hour=22, minute=0, second=0, microsecond=0)
        else:
            # Winter time - market opens at 16:00, closes at 23:00
            market_open = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
            market_close = current_time.replace(hour=23, minute=0, second=0, microsecond=0)
        
        return market_open, market_close

    def is_holiday_today(self):
        """Check if today is a holiday"""
        # Your holiday checking logic here
        # Return True if holiday, False otherwise
        return False  # Placeholder - implement your holiday logic here
    
    def _setup_weekly_tasks(self):
        """Setup weekly recurring tasks"""
        
        # Weekly backup (Sunday 9:00 AM)
        # self.discord_scheduler.add_cron_job(
        #     func=lambda: weekly_backup_task(self.discord_scheduler),
        #     cron_expression="0 9 * * 0",  # 9:00 AM Sunday
        #     job_id="weekly_backup"
        # )
        pass

    def _setup_custom_tasks(self):
        """Setup custom tasks with specific dates"""
        
        # Example: Schedule a task for a specific date
        # You can add specific date tasks here
        pass
    

    

    