"""
Task Definitions V2 - Using APScheduler with cron expressions and specific dates
"""

import asyncio
from datetime import datetime, timedelta
from utils.logger import logger
from .discord_scheduler import DiscordScheduler

from .tasks.news_report import (
    morning_news_report_task,
    evening_news_report_task
)
from .tasks.economic_calendar_tasks import get_economic_calendar_task
from .tasks.weekly_tasks import weekly_backup_task
from time import time
from config import config

class TaskDefinitions:
    """Task definitions using APScheduler with cron expressions"""
    
    def __init__(self, discord_scheduler: DiscordScheduler):
        self.discord_scheduler = discord_scheduler
    
    def setup_all_tasks(self):
        """Setup all scheduled tasks"""
        logger.info("📅 Setting up all scheduled tasks...")
        
        # Daily tasks (weekdays)
        self._setup_daily_tasks()
        
        # Weekly tasks
        self._setup_weekly_tasks()
        
        # Custom tasks
        self._setup_custom_tasks()
        
        self.discord_scheduler.add_date_job(
            func=lambda: get_economic_calendar_task(self.discord_scheduler),
            run_date=datetime.now(self.discord_scheduler.timezone) + timedelta(seconds=5),
            job_id="economic_calendar_startup"
        )
        
        logger.info("✅ All tasks setup completed")
    
    def _setup_daily_tasks(self):
        """Setup daily recurring tasks"""
        
        # Morning news report (16:00 daily)
        self.discord_scheduler.add_cron_job(
            func=lambda: morning_news_report_task(self.discord_scheduler),
            cron_expression="0 16 * * *",  # 4:00 PM daily
            job_id="morning_news_report"
        )
        
        # Evening news report (23:00 daily)
        self.discord_scheduler.add_cron_job(
            func=lambda: evening_news_report_task(self.discord_scheduler),
            cron_expression="0 23 * * *",  # 11:00 PM daily
            job_id="evening_news_report"
        )
        
        # Economic calendar check (8:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: get_economic_calendar_task(self.discord_scheduler),
            cron_expression="0 8 * * 1-5",  # 8:00 AM Monday-Friday
            job_id="economic_calendar_check"
        )
    
    def _setup_weekly_tasks(self):
        """Setup weekly recurring tasks"""
        
        # Weekly backup (Sunday 9:00 AM)
        self.discord_scheduler.add_cron_job(
            func=lambda: weekly_backup_task(self.discord_scheduler),
            cron_expression="0 9 * * 0",  # 9:00 AM Sunday
            job_id="weekly_backup"
        )
    
    def _setup_custom_tasks(self):
        """Setup custom tasks with specific dates"""
        
        # Example: Schedule a task for a specific date
        # You can add specific date tasks here
        pass
    

    

    