"""
Economic Calendar Task - Main economic calendar functionality
"""

from datetime import datetime, timedelta
from typing import Set
import pandas as pd
import asyncio
from utils.logger import logger
from scrapers import InvestingScraper, InvestingParams, economic_calendar_to_text
from config import Config
from .economic_warning_task import economic_warning_task
from .economic_update_task import economic_update_task
from discord_utils import send_alert
from scheduler_v2.global_scheduler import get_discord_scheduler


async def schedule_economic_calendar_task():
    """Execute the economic calendar task"""
    try:
        discord_scheduler = get_discord_scheduler()
        if not discord_scheduler:
            logger.error("❌ No DiscordScheduler instance available")
            return
        

            
        logger.info("📊 Fetching economic calendar...")
        
        # Get calendar data using InvestingDataScraper
        scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY)
        calendar_data = await scraper.get_calendar(
            calendar_name=InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
            current_tab=InvestingParams.TIME_RANGES.TODAY,
            importance=InvestingParams.IMPORTANCE.APP_IMPORTANCES,
            countries=[InvestingParams.COUNTRIES.UNITED_STATES],
            time_zone=InvestingParams.TIME_ZONES.ISRAEL
        )
        
        # Handle None or empty DataFrame
        if calendar_data.empty:
            logger.warning("⚠️ No economic calendar data received")
            return
        
        # Send initial summary to alert channel
        await _send_initial_summary(calendar_data, discord_scheduler)
        
        # Extract unique times from DataFrame
        unique_times: Set[str] = set()
        if 'time' in calendar_data.columns:
            unique_times = set(calendar_data['time'].dropna().unique())
        
        logger.debug(f"📊 Found {len(calendar_data)} events at {len(unique_times)} times")
        
        # Remove existing economic event jobs to avoid duplicates
        _remove_existing_economic_jobs(discord_scheduler)
        
        # Schedule alerts for each unique time
        await _schedule_economic_alerts(unique_times, calendar_data, discord_scheduler)

    except Exception as e:
        logger.error(f"❌ Error in economic calendar task: {e}")


async def _send_initial_summary(calendar_data: pd.DataFrame, discord_scheduler):
    """Send initial calendar summary to alert channel"""
    try:
        summary_msg = economic_calendar_to_text(calendar_data)
        
        # Send to alert channel using send_message
        await send_alert(discord_scheduler.bot, summary_msg, 0x00ff00, "Economic Events For Today")
        
        # Send role mention as separate text message
        economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
        await discord_scheduler.send_mention_text(economic_role)

        logger.debug(f"📊 Sent initial calendar summary")
    except Exception as e:
        logger.error(f"❌ Error sending initial calendar summary: {e}")


def _remove_existing_economic_jobs(discord_scheduler):
    """Remove existing economic event jobs to avoid duplicates"""
    if discord_scheduler:
        existing_jobs = discord_scheduler.get_jobs()
        for job in existing_jobs:
            if job.id.startswith('economic_') and not job.id == 'economic_calendar_check':
                discord_scheduler.remove_job(job.id)


async def _schedule_economic_alerts(unique_times: Set[str], calendar_data: pd.DataFrame, discord_scheduler):
    """Schedule economic alerts for each unique time"""
    scheduled_jobs = []
    if discord_scheduler:
        for time_str in sorted(unique_times):
            jobs = await _schedule_alert_at_time(time_str, calendar_data, discord_scheduler)
            scheduled_jobs.extend(jobs)
    return scheduled_jobs


async def _schedule_alert_at_time(time_str: str, calendar_data: pd.DataFrame, discord_scheduler):
    """Schedule economic alerts for a specific time"""
    jobs_added = []
    try:
        # Parse time and create datetime for today using scheduler timezone
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        today = datetime.now(discord_scheduler.timezone).date()
        
        # Create timezone-aware datetime using the scheduler's timezone
        event_datetime = discord_scheduler.timezone.localize(datetime.combine(today, time_obj))
        current_time = datetime.now(discord_scheduler.timezone)
        
        # Get events for this specific time from DataFrame
        time_events = calendar_data[calendar_data['time'] == time_str]
        
        if not time_events.empty:
            # Schedule warning task (5 minutes before)
            warning_time = event_datetime - timedelta(minutes=5)
            
            # Only schedule warning if it's in the future
            if warning_time > current_time:
                discord_scheduler.add_date_job(
                    func=economic_warning_task,
                    run_date=warning_time,
                    job_id=f"economic_warning_{time_str.replace(':', '_')}",
                    args=(time_str, time_events)
                )
                jobs_added.append({
                    'id': f"economic_warning_{time_str.replace(':', '_')}",
                    'time': warning_time.strftime('%H:%M'),
                    'type': 'warning'
                })
            
            # Schedule update task (after event) - only if event hasn't passed
            update_time = event_datetime + timedelta(seconds=discord_scheduler.post_event_delay)
            if update_time > current_time:
                discord_scheduler.add_date_job(
                    func=economic_update_task,
                    run_date=update_time,
                    job_id=f"economic_update_{time_str.replace(':', '_')}",
                    args=(time_str,)
                )
                jobs_added.append({
                    'id': f"economic_update_{time_str.replace(':', '_')}",
                    'time': update_time.strftime('%H:%M'),
                    'type': 'update'
                })

    except Exception as e:
        logger.error(f"❌ Error scheduling economic alert for {time_str}: {e}")
    
    return jobs_added

