"""
Discord Scheduler - APScheduler-based scheduler with Discord integration and task management
"""

import asyncio
import discord
from datetime import datetime, date, timedelta
from typing import Optional, Callable, Union, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from utils.logger import logger
from config import Config
import pytz
from .job_summary import JobSummary
from discord_utils import send_embed_message, send_mention_message
from time import time
from bot_manager import get_bot


class CoreScheduler:
    """APScheduler-based scheduler with Discord integration"""
    
    def __init__(self, alert_channel_id: int, dev_channel_id: int, timezone: str, post_event_delay: int = 7, schedule: Config.SCHEDULE = None):
        
        self.bot = get_bot()
        self.alert_channel_id = alert_channel_id
        self.dev_channel_id = dev_channel_id or Config.CHANNEL_IDS.DEV
        self.timezone = pytz.timezone(timezone)
        self.post_event_delay = post_event_delay  # Delay in seconds for post-event updates
        self.job_summary = JobSummary(timezone)
        self.schedule = schedule
        
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,  # Allow more concurrent jobs
            'misfire_grace_time': 180  # Allow jobs to run up to 180 seconds late
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        # Add job listeners for better monitoring
        self.scheduler.add_listener(self._job_listener, mask=1 | 2 | 4096)  # Only listen to specific events
        
        self.running = False
    
    def add_cron_job(self, 
                     func: Callable, 
                     cron_expression: str, 
                     job_id: str,
                     args: tuple = None,
                     kwargs: dict = None,
                     send_alert: bool = True) -> bool:
        """
        Add a cron-based job
        
        Args:
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 8 * * 1-5" for 8 AM weekdays)
            job_id: Unique job identifier
            args: Function arguments
            kwargs: Function keyword arguments
            send_alert: Whether to send Discord alert
        """
        try:
            async def wrapped_func():
                try:
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, f"✅ **{job_id}** completed successfully", Config.COLORS.GREEN, "🔧 Scheduler Alert")
                    
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"Job failed {job_id}: {e}")
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, error_msg, Config.COLORS.RED, "🔧 Scheduler Alert")
            
            self.scheduler.add_job(
                wrapped_func,
                CronTrigger.from_crontab(cron_expression, timezone=self.timezone),
                id=job_id,
                replace_existing=True
            )
            
            # Track the job for summary
            self.job_summary.add_job({
                'id': job_id,
                'type': 'cron',
                'expression': cron_expression,
                'timezone': str(self.timezone)
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add cron job {job_id}: {e}")
            return False
    
    def add_date_job(self, 
                     func: Callable, 
                     run_date: Union[datetime, date, str], 
                     job_id: str,
                     args: tuple = None,
                     kwargs: dict = None,
                     send_alert: bool = True) -> bool:
        """
        Add a one-time job for a specific date/time
        
        Args:
            func: Function to execute
            run_date: When to run the job (datetime, date, or ISO string)
            job_id: Unique job identifier
            args: Function arguments
            kwargs: Function keyword arguments
            send_alert: Whether to send Discord alert
        """
        try:
            async def wrapped_func():
                try:
                    # Remove one-time jobs from summary when they start
                    self._remove_date_job_from_summary(job_id)
                    
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, f"✅ **{job_id}** completed successfully", Config.COLORS.GREEN, "🔧 Scheduler Alert")
                    
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"One-time job failed {job_id}: {e}")
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, error_msg, Config.COLORS.RED, "🔧 Scheduler Alert")
            
            self.scheduler.add_job(
                wrapped_func,
                DateTrigger(run_date=run_date),
                id=job_id,
                replace_existing=True
            )
            
            # Track the job for summary
            self.job_summary.add_job({
                'id': job_id,
                'type': 'date',
                'run_date': str(run_date),
                'timezone': str(self.timezone)
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add one-time job {job_id}: {e}")
            return False
    
    def add_interval_job(self, 
                        func: Callable, 
                        job_id: str,
                        seconds: int = 60,
                        args: tuple = None,
                        kwargs: dict = None,
                        send_alert: bool = True) -> bool:
        """
        Add an interval-based job
        
        Args:
            func: Function to execute
            seconds: Interval in seconds
            job_id: Unique job identifier
            args: Function arguments
            kwargs: Function keyword arguments
            send_alert: Whether to send Discord alert
        """
        try:
            async def wrapped_func():
                try:
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, f"✅ **{job_id}** completed successfully", Config.COLORS.GREEN, "🔧 Scheduler Alert")
                    
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"Interval job failed {job_id}: {e}")
                    
                    if send_alert:
                        await send_embed_message(self.bot, Config.CHANNEL_IDS.DEV, error_msg, Config.COLORS.RED, "🔧 Scheduler Alert")
            
            self.scheduler.add_job(
                wrapped_func,
                IntervalTrigger(seconds=seconds),
                id=job_id,
                replace_existing=True
            )
            
            # Track the job for summary
            self.job_summary.add_job({
                'id': job_id,
                'type': 'interval',
                'seconds': seconds,
                'timezone': str(self.timezone)
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add interval job {job_id}: {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a job by ID"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"🗑️ Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to remove job {job_id}: {e}")
            return False
    
    def _remove_date_job_from_summary(self, job_id: str):
        """Remove a date job from the summary after completion"""
        try:
            self.job_summary.remove_job(job_id)
            logger.info(f"🗑️ Removed date job from summary: {job_id}")
        except Exception as e:
            logger.debug(f"Error removing date job from summary: {e}")
    
    def get_job(self, job_id: str):
        """Get job by ID"""
        return self.scheduler.get_job(job_id)
    
    def get_jobs(self):
        """Get all jobs"""
        return self.scheduler.get_jobs()
    

    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.scheduler.start()
            self.running = True
            logger.info("🚀 Discord Scheduler started")
            
            # Generate and send job summary to dev channel
            summary = self.generate_job_summary()
            logger.info(f"📋 Job Summary:\n{summary}")
            
            asyncio.create_task(send_embed_message(
                self.bot,
                Config.CHANNEL_IDS.DEV,
                summary,
                Config.COLORS.GREEN,
                "🔧 Scheduler Started"
            ))
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("🛑 Discord Scheduler stopped")
    
    def pause(self):
        """Pause the scheduler"""
        self.scheduler.pause()
        logger.info("⏸️ Discord Scheduler paused")
    
    def resume(self):
        """Resume the scheduler"""
        self.scheduler.resume()
        logger.info("▶️ Discord Scheduler resumed")
    
    def generate_job_summary(self) -> str:
        """Generate a summary of all scheduled jobs using JobSummary class"""
        return self.job_summary.generate_summary()
    
    def get_job_count(self) -> int:
        """Get number of tracked jobs"""
        return self.job_summary.get_job_count()
    
    def get_status(self) -> dict:
        """Get scheduler status"""
        jobs = self.get_jobs()
        return {
            'running': self.running,
            'job_count': len(jobs),
            'jobs': [
                {
                    'id': job.id,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                for job in jobs
            ]
        }
    
    def _job_listener(self, event):
        """Handle job events for monitoring"""
        try:
            event_code = getattr(event, 'code', None)
            
            # Only process job execution events
            if event_code == 1:  # EVENT_JOB_EXECUTED
                # Get job ID from the job object
                job_id = 'unknown'
                if hasattr(event, 'job') and event.job and hasattr(event.job, 'id'):
                    job_id = event.job.id
                
                # Only log if we have a valid job ID
                if job_id != 'unknown':
                    logger.info(f"🚀 Starting job: {job_id}")
                
            elif event_code == 2:  # EVENT_JOB_ERROR
                job_id = 'unknown'
                if hasattr(event, 'job') and event.job and hasattr(event.job, 'id'):
                    job_id = event.job.id
                exception = getattr(event, 'exception', 'unknown error')
                logger.error(f"❌ Job failed: {job_id} - {exception}")
                
            elif event_code == 4096:  # EVENT_JOB_MISSED
                job_id = 'unknown'
                if hasattr(event, 'job') and event.job and hasattr(event.job, 'id'):
                    job_id = event.job.id
                scheduled_time = getattr(event, 'scheduled_run_time', 'unknown')
                # Only log significant delays (more than 30 seconds)
                current_time = datetime.now(self.timezone)
                if hasattr(scheduled_time, 'replace'):
                    delay = (current_time - scheduled_time.replace(tzinfo=self.timezone)).total_seconds()
                    if delay > 30:
                        logger.warning(f"⚠️ Job significantly delayed: {job_id} - {delay:.1f}s late")
                
        except Exception as e:
            logger.debug(f"Error in job listener: {e}")

