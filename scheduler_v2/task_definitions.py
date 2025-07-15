"""
Task Definitions V2 - Using APScheduler with cron expressions and specific dates
"""

import asyncio
from datetime import datetime, timedelta
from utils.logger import logger
from .discord_scheduler import DiscordScheduler
from .calendar_manager import CalendarManager
from .tasks.daily_tasks import (
    daily_schedule_task,
    market_open_check_task,
    daily_report_task,
    morning_greeting_task,
    evening_summary_task,
    system_health_check_task,
    news_check_task,
    schedule_future_events_task
)
from .tasks.weekly_tasks import weekly_backup_task


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
            func=lambda: daily_schedule_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="0 8 * * 1-5",  # 8:00 AM Monday-Friday
            job_id="daily_schedule"
        )
        
        # Market open check (9:30 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: market_open_check_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="30 9 * * 1-5",  # 9:30 AM Monday-Friday
            job_id="market_open_check"
        )
        
        # Daily report (2:30 PM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: daily_report_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="30 14 * * 1-5",  # 2:30 PM Monday-Friday
            job_id="daily_report"
        )
        
        # Morning greeting (7:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: morning_greeting_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="0 7 * * 1-5",  # 7:00 AM Monday-Friday
            job_id="morning_greeting"
        )
        
        # Evening summary (5:00 PM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: evening_summary_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="0 17 * * 1-5",  # 5:00 PM Monday-Friday
            job_id="evening_summary"
        )
        
        # System health check (6:00 AM weekdays)
        self.discord_scheduler.add_cron_job(
            func=lambda: system_health_check_task(self.discord_scheduler, self.calendar_manager),
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
                func=lambda: news_check_task(self.discord_scheduler, self.calendar_manager),
                cron_expression=cron_expr,
                job_id=job_id
            )
    
    def _setup_weekly_tasks(self):
        """Setup weekly recurring tasks"""
        
        # Weekly backup (Sunday 9:00 AM)
        self.discord_scheduler.add_cron_job(
            func=lambda: weekly_backup_task(self.discord_scheduler, self.calendar_manager),
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
            func=lambda: schedule_future_events_task(self.discord_scheduler, self.calendar_manager),
            cron_expression="30 7 * * 1-5",  # 7:30 AM Monday-Friday
            job_id="schedule_future_events"
        )
    

    
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