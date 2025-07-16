"""
Economic Calendar Task Functions
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Set
import pandas as pd
from utils.logger import logger
from investing_scraper.InvestingDataScraper import InvestingDataScraper
from investing_scraper.investing_variables import InvestingVariables
from config import Config
import pytz


async def get_economic_calendar_task(discord_scheduler=None):
    """Get economic calendar and schedule alerts for unique times"""
    try:
        logger.info("📊 Fetching economic calendar...")
        
        # Get calendar data using InvestingDataScraper
        scraper = InvestingDataScraper()
        calendar_data = await scraper.get_calendar(
            calendar_name=InvestingVariables.CALENDARS.ECONOMIC_CALENDAR,
            current_tab=InvestingVariables.TIME_RANGES.TODAY,
            importance=[
                InvestingVariables.IMPORTANCE.HIGH,
                InvestingVariables.IMPORTANCE.MEDIUM
            ],
            countries=[InvestingVariables.COUNTRIES.UNITED_STATES],
            time_zone=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        )
        
        if not calendar_data:
            logger.warning("⚠️ No economic calendar data received")
            return
        
        today_events = calendar_data
        
        # Send initial summary to alert channel (not dev)
        if discord_scheduler:
            await send_initial_calendar_summary_to_alert(discord_scheduler, today_events)
        
        # Extract unique times
        unique_times: Set[str] = set()
        for event in today_events:
            if 'time' in event:
                unique_times.add(event['time'])
        
        logger.info(f"📊 Found {len(today_events)} events with {len(unique_times)} unique times: {sorted(unique_times)}")
        
        # Remove existing economic event jobs to avoid duplicates
        if discord_scheduler:
            existing_jobs = discord_scheduler.get_jobs()
            for job in existing_jobs:
                if job.id.startswith('economic_'):
                    discord_scheduler.remove_job(job.id)
        
        # Schedule alerts for each unique time, track jobs for summary
        scheduled_jobs = []
        if discord_scheduler:
            for time_str in sorted(unique_times):
                jobs = await schedule_economic_alert_at_time(discord_scheduler, time_str, today_events)
                scheduled_jobs.extend(jobs)
        
        # After all jobs are scheduled, send a single job summary to dev channel
        if discord_scheduler and scheduled_jobs:
            summary = discord_scheduler.generate_job_summary()
            logger.info(f"📋 Economic Event Jobs updated: {summary}")
            await discord_scheduler.send_dev_alert(summary, 0x00ff00, "📋 Economic Event Jobs Scheduled")
        
        logger.info("✅ Economic calendar processing completed")
        
    except Exception as e:
        logger.error(f"❌ Error in economic calendar task: {e}")


async def send_initial_calendar_summary_to_alert(discord_scheduler, today_events):
    """Send initial calendar summary to alert channel"""
    try:
        # Convert to DataFrame and then to CSV
        df = pd.DataFrame(today_events)
        
        # Reorder columns for better readability
        column_order = ['time', 'description', 'volatility', 'forecast', 'previous', 'actual', 'country']
        df = df.reindex(columns=[col for col in column_order if col in df.columns])
        
        # Convert to CSV string
        csv_data = df.to_csv(index=False)
        
        # Create summary message
        summary_msg = "📊 **Important economic events for today:**\n\n"
        summary_msg += f"Total events: {len(today_events)}\n"
        summary_msg += "```csv\n"
        summary_msg += csv_data
        summary_msg += "```"
        
        # Send to alert channel
        await discord_scheduler.send_alert(summary_msg, 0x00ff00, "📊 Economic Calendar Summary")
        logger.info(f"📊 Sent initial calendar summary to alert channel with {len(today_events)} events")
        
    except Exception as e:
        logger.error(f"❌ Error sending initial calendar summary: {e}")


async def schedule_economic_alert_at_time(discord_scheduler, time_str: str, today_events):
    """Schedule economic alerts for a specific time. Returns list of job dicts for summary."""
    jobs_added = []
    try:
        # Parse time and create datetime for today
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        tz = pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        today = datetime.now(tz).date()
        event_datetime = datetime.combine(today, time_obj, tzinfo=tz)
        
        # Get events for this specific time
        time_events = [event for event in today_events if event.get('time') == time_str]
        
        # Schedule 5-minute warning (only if not already scheduled)
        warning_time = event_datetime - timedelta(minutes=5)
        if warning_time > datetime.now(tz):
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
                        'timezone': str(discord_scheduler.timezone)
                    })
                else:
                    logger.de(f"📅 Warning job already exists for {time_str}")
        
        # Schedule post-event update (only if not already scheduled)
        update_time = event_datetime + timedelta(seconds=discord_scheduler.post_event_delay)
        if update_time > datetime.now(tz):
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
                        'timezone': str(discord_scheduler.timezone)
                    })
                else:
                    logger.debug(f"📅 Update job already exists for {time_str}")
        else:
            logger.debug(f"⏰ Time {time_str} has already passed, skipping alerts")
        
    except Exception as e:
        logger.error(f"❌ Error scheduling economic alerts for {time_str}: {e}")
    return jobs_added


async def economic_warning_task(time_str: str, time_events, discord_scheduler=None):
    """Send 5-minute warning for economic events"""
    try:
        logger.info(f"⚠️ Sending 5-minute warning for {time_str}")
        
        if time_events and discord_scheduler:
            # Create warning message
            event_names = [event.get('description', 'Unknown Event') for event in time_events]
            warning_msg = f"⚠️ **Events coming in 5 minutes at {time_str}:**\n"
            warning_msg += ", ".join(event_names)
            
            # Send to alert channel
            await discord_scheduler.send_alert(warning_msg, 0xffa500, "⚠️ Economic Events Warning")
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
        
        # Fetch updated calendar data
        scraper = InvestingDataScraper()
        calendar_data = await scraper.get_calendar(
            calendar_name=InvestingVariables.CALENDARS.ECONOMIC_CALENDAR,
            current_tab=InvestingVariables.TIME_RANGES.TODAY,
            importance=[
                InvestingVariables.IMPORTANCE.HIGH,
                InvestingVariables.IMPORTANCE.MEDIUM
            ],
            countries=[InvestingVariables.COUNTRIES.UNITED_STATES],
            time_zone=pytz.timezone(Config.TIMEZONES.APP_TIMEZONE)
        )
        
        if not calendar_data:
            logger.warning("⚠️ No economic calendar data for update")
            return
        
        # Get today's events
        today_key = list(calendar_data.keys())[0]
        today_events = calendar_data[today_key]
        
        # Filter events for the specific time
        time_events = [event for event in today_events if event.get('time') == time_str]
        
        if time_events and discord_scheduler:
            # Convert to DataFrame and then to CSV
            df = pd.DataFrame(time_events)
            
            # Reorder columns for better readability
            column_order = ['time', 'description', 'volatility', 'forecast', 'previous', 'actual', 'country']
            df = df.reindex(columns=[col for col in column_order if col in df.columns])
            
            # Convert to CSV string
            csv_data = df.to_csv(index=False)
            
            # Create update message
            update_msg = f"📊 **Economic Events Update for {time_str}:**\n\n"
            update_msg += f"Events: {len(time_events)}\n"
            update_msg += "```csv\n"
            update_msg += csv_data
            update_msg += "```"
            
            # Send to alert channel
            await discord_scheduler.send_alert(update_msg, 0x00ff00, "📊 Economic Events Update")
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