"""
Discord Scheduler - APScheduler-based scheduler with Discord integration
"""

import asyncio
import discord
from datetime import datetime, date
from typing import Optional, Callable, Union, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from utils.logger import logger
from config import config
import pytz
from .job_summary import JobSummary

class DiscordScheduler:
    """APScheduler-based scheduler with Discord integration"""
    
    def __init__(self, bot: discord.Client, alert_channel_id: int, dev_channel_id: int = None, timezone: pytz.timezone = config.app_timezone):
        self.bot = bot
        self.alert_channel_id = alert_channel_id
        self.dev_channel_id = dev_channel_id or config.channel_ids.dev_alerts
        self.timezone = timezone
        self.job_summary = JobSummary(timezone)
        
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        self.running = False
    
    async def send_alert(self, message: str, color: int = 0x00ff00, title: str = "📅 Scheduler Alert"):
        """Send alert to the main alert channel (for actual data/messages)"""
        try:
            channel = self.bot.get_channel(self.alert_channel_id)
            if channel:
                embed = discord.Embed(
                    title=title,
                    description=message,
                    color=color,
                    timestamp=datetime.now(self.timezone)
                )
                await channel.send(embed=embed)
            else:
                logger.error(f"Alert channel {self.alert_channel_id} not found")
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    async def send_dev_alert(self, message: str, color: int = 0x00ff00, title: str = "🔧 Dev Alert"):
        """Send alert to the dev channel (for scheduler status, errors, etc.)"""
        try:
            channel = self.bot.get_channel(self.dev_channel_id)
            if channel:
                embed = discord.Embed(
                    title=title,
                    description=message,
                    color=color,
                    timestamp=datetime.now(self.timezone)
                )
                await channel.send(embed=embed)
            else:
                logger.error(f"Dev channel {self.dev_channel_id} not found")
        except Exception as e:
            logger.error(f"Error sending dev alert: {e}")
    
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
                    logger.info(f"🚀 Executing job: {job_id}")
                    
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await self.send_dev_alert(f"✅ **{job_id}** completed successfully", 0x00ff00)
                    
                    logger.info(f"✅ Job completed: {job_id}")
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"Job failed {job_id}: {e}")
                    
                    if send_alert:
                        await self.send_dev_alert(error_msg, 0xff0000)
            
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
                    logger.info(f"🚀 Executing one-time job: {job_id}")
                    
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await self.send_dev_alert(f"✅ **{job_id}** completed successfully", 0x00ff00)
                    
                    logger.info(f"✅ One-time job completed: {job_id}")
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"One-time job failed {job_id}: {e}")
                    
                    if send_alert:
                        await self.send_dev_alert(error_msg, 0xff0000)
            
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
                    logger.info(f"🚀 Executing interval job: {job_id}")
                    
                    if args and kwargs:
                        result = await func(*args, **kwargs)
                    elif args:
                        result = await func(*args)
                    elif kwargs:
                        result = await func(**kwargs)
                    else:
                        result = await func()
                    
                    if send_alert:
                        await self.send_dev_alert(f"✅ **{job_id}** completed successfully", 0x00ff00)
                    
                    logger.info(f"✅ Interval job completed: {job_id}")
                    return result
                    
                except Exception as e:
                    error_msg = f"❌ **{job_id}** failed: {str(e)}"
                    logger.error(f"Interval job failed {job_id}: {e}")
                    
                    if send_alert:
                        await self.send_dev_alert(error_msg, 0xff0000)
            
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
            
            asyncio.create_task(self.send_dev_alert(
                summary,
                0x00ff00,
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