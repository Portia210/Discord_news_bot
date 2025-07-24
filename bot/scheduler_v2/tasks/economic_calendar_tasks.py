"""
Economic Calendar Task Functions
"""

from datetime import datetime, timedelta
from typing import Set
import pandas as pd
from utils.logger import logger
from scrapers import InvestingScraper, InvestingParams, economic_calendar_to_text
from scheduler_v2.discord_scheduler import DiscordScheduler
from config import Config
import pytz


async def get_economic_calendar_task(discord_scheduler: DiscordScheduler = None):
    """Get economic calendar and schedule alerts for unique times"""
    try:
        logger.info("📊 Fetching economic calendar...")
        
        # Use DiscordScheduler's timezone if available, otherwise fall back to config
        timezone_to_use = discord_scheduler.timezone if discord_scheduler else pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        
        # Get calendar data using InvestingDataScraper
        scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY)
        calendar_data = await scraper.get_calendar(
            calendar_name=InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
            current_tab=InvestingParams.TIME_RANGES.TODAY,
            importance=InvestingParams.IMPORTANCE.APP_IMPORTANCES,
            countries=[InvestingParams.COUNTRIES.UNITED_STATES],
            time_zone=timezone_to_use
        )
        
        # Handle None or empty DataFrame
        if calendar_data is None or calendar_data.empty:
            logger.warning("⚠️ No economic calendar data received")
            return
        
        # Send initial summary to alert channel (not dev)
        if discord_scheduler:
            await send_initial_calendar_summary_to_alert(discord_scheduler, calendar_data)
        
        # Extract unique times from DataFrame
        unique_times: Set[str] = set()
        if 'time' in calendar_data.columns:
            unique_times = set(calendar_data['time'].dropna().unique())
        
        logger.info(f"📊 Found {len(calendar_data)} events with {len(unique_times)} unique times: {sorted(unique_times)}")
        
        # Remove existing economic event jobs to avoid duplicates (but keep the daily cron job)
        if discord_scheduler:
            existing_jobs = discord_scheduler.get_jobs()
            for job in existing_jobs:
                if job.id.startswith('economic_') and not job.id == 'economic_calendar_check':
                    discord_scheduler.remove_job(job.id)
        
        # Schedule alerts for each unique time, track jobs for summary
        scheduled_jobs = []
        if discord_scheduler:
            for time_str in sorted(unique_times):
                jobs = await schedule_economic_alert_at_time(discord_scheduler, time_str, calendar_data)
                scheduled_jobs.extend(jobs)
        
        # After all jobs are scheduled, send a single job summary to dev channel
        if discord_scheduler and scheduled_jobs:
            summary = discord_scheduler.generate_job_summary()
            logger.info(f"📋 Economic Event Jobs updated: {summary}")
            await discord_scheduler.send_dev_alert(summary, 0x00ff00, "📋 Economic Event Jobs Scheduled")
        
        
    except Exception as e:
        logger.error(f"❌ Error in economic calendar task: {e}")


async def send_initial_calendar_summary_to_alert(discord_scheduler, calendar_data: pd.DataFrame):
    """Send initial calendar summary to alert channel"""
    try:
        summary_msg = economic_calendar_to_text(calendar_data)
        
        # Send to alert channel
        await discord_scheduler.send_alert(summary_msg, 0x00ff00, "Economic Events For Today")
        
        # Send role mention as separate text message
        economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
        await discord_scheduler.send_mention_text(economic_role)

        logger.info(f"📊 Sent initial calendar summary to alert channel")
    except Exception as e:
        logger.error(f"❌ Error sending initial calendar summary: {e}")


async def schedule_economic_alert_at_time(discord_scheduler: DiscordScheduler, time_str: str, calendar_data: pd.DataFrame):
    """Schedule economic alerts for a specific time. Returns list of job dicts for summary."""
    jobs_added = []
    try:
        # Use DiscordScheduler's timezone consistently
        scheduler_tz = discord_scheduler.timezone
        
        # Parse time and create datetime for today using scheduler timezone
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        today = datetime.now(scheduler_tz).date()
        
        # Create timezone-aware datetime using the scheduler's timezone
        event_datetime = scheduler_tz.localize(datetime.combine(today, time_obj))
        
        # Get events for this specific time from DataFrame
        time_events = calendar_data[calendar_data['time'] == time_str]
        
        # Schedule 5-minute warning (only if not already scheduled)
        warning_time = event_datetime - timedelta(minutes=5)
        current_time = datetime.now(scheduler_tz)
        
        # Debug logging to verify timezone fix
        # logger.info(f"🔍 DEBUG - Scheduling for {time_str}:")
        # logger.info(f"   Scheduler timezone: {scheduler_tz}")
        # logger.info(f"   Event datetime: {event_datetime}")
        # logger.info(f"   Current time: {current_time}")
        # logger.info(f"   Warning time: {warning_time}")
        # logger.info(f"   Update time: {event_datetime + timedelta(seconds=discord_scheduler.post_event_delay)}")
        
        if warning_time > current_time:
            warning_job_id = f"economic_warning_{time_str.replace(':', '_')}"
            
            # Check if job already exists
            existing_job = discord_scheduler.get_job(warning_job_id)
            if not existing_job:
                success = discord_scheduler.add_date_job(
                    func=economic_warning_task,
                    run_date=warning_time,
                    job_id=warning_job_id,
                    args=(time_str, time_events, discord_scheduler),
                    send_alert=False
                )
                if success:
                    jobs_added.append({
                        'id': warning_job_id,
                        'type': 'date',
                        'run_date': str(warning_time),
                        'timezone': str(scheduler_tz)
                    })
                else:
                    logger.debug(f"📅 Warning job already exists for {time_str}")
        
        # Schedule post-event update (only if not already scheduled)
        update_time = event_datetime + timedelta(seconds=discord_scheduler.post_event_delay)
        
        if update_time > current_time:
            update_job_id = f"economic_update_{time_str.replace(':', '_')}"
            
            # Check if job already exists
            existing_job = discord_scheduler.get_job(update_job_id)
            if not existing_job:
                success = discord_scheduler.add_date_job(
                    func=economic_update_task,
                    run_date=update_time,
                    job_id=update_job_id,
                    args=(time_str, discord_scheduler),
                    send_alert=False
                )
                if success:
                    jobs_added.append({
                        'id': update_job_id,
                        'type': 'date',
                        'run_date': str(update_time),
                        'timezone': str(scheduler_tz)
                    })
                else:
                    logger.debug(f"📅 Update job already exists for {time_str}")
        else:
            logger.debug(f"⏰ Time {time_str} has already passed, skipping alerts")
        
    except Exception as e:
        logger.error(f"❌ Error scheduling economic alerts for {time_str}: {e}")
    return jobs_added


async def economic_warning_task(time_str: str, time_events: pd.DataFrame, discord_scheduler=None):
    """Send 5-minute warning for economic events"""
    try:
        logger.info(f"⚠️ Sending 5-minute warning for {time_str}")
        
        if not time_events.empty and discord_scheduler:
            # Create warning message from DataFrame
            event_names = time_events['description'].fillna('Unknown Event').tolist()
            
            warning_msg = f"⚠️ **Events coming in 5 minutes at {time_str}:**\n"
            warning_msg += ", ".join(event_names)
            
            # Send to alert channel
            await discord_scheduler.send_alert(warning_msg, 0xffa500, "⚠️ Economic Events Warning")
            
            # Send role mention as separate text message
            economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
            await discord_scheduler.send_mention_text(economic_role)
            logger.info(f"⚠️ 5-minute warning sent for {len(time_events)} events at {time_str}")
        else:
            logger.info(f"⚠️ No events found for time {time_str}")
            
    except Exception as e:
        logger.error(f"❌ Error in economic warning task for {time_str}: {e}")
        if discord_scheduler:
            await discord_scheduler.send_alert(
                f"❌ **Economic Warning Failed**\nTime: {time_str}\nError: {str(e)}",
                0xff0000,
                "⚠️ Economic Events Warning"
            )


async def economic_update_task(time_str: str, discord_scheduler=None):
    """Send post-event update for economic events"""
    try:
        logger.info(f"📊 Sending post-event update for {time_str}")
        
        # Use DiscordScheduler's timezone if available, otherwise fall back to config
        timezone_to_use = discord_scheduler.timezone if discord_scheduler else pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        
        # Fetch updated calendar data
        scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY)
        calendar_data = await scraper.get_calendar(
            calendar_name=InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
            current_tab=InvestingParams.TIME_RANGES.TODAY,
            importance=InvestingParams.IMPORTANCE.APP_IMPORTANCES,
            countries=[InvestingParams.COUNTRIES.UNITED_STATES],
            time_zone=timezone_to_use
        )
        
        if calendar_data is None or calendar_data.empty:
            logger.warning("⚠️ No economic calendar data for update")
            return
        
        # Filter events for the specific time from DataFrame
        time_events = calendar_data[calendar_data['time'] == time_str]
        
        if not time_events.empty and discord_scheduler:
            summary_msg = economic_calendar_to_text(time_events)
            
            # Create update message
            update_msg = f"📊 **Economic Events Update for {time_str}:**\n"
            update_msg += summary_msg
            
            # Send to alert channel
            await discord_scheduler.send_alert(update_msg, 0x00ff00, "Economic Events Update")
            
            # Send role mention as separate text message
            economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
            await discord_scheduler.send_mention_text(economic_role)
            logger.info(f"📊 Post-event update sent for {len(time_events)} events at {time_str}")
        else:
            logger.info(f"📊 No events found for time {time_str}")
            
    except Exception as e:
        logger.error(f"❌ Error in economic update task for {time_str}: {e}")
        if discord_scheduler:
            await discord_scheduler.send_alert(
                f"❌ **Economic Update Failed**\nTime: {time_str}\nError: {str(e)}",
                0xff0000,
                "📊 Economic Events Update"
            ) 