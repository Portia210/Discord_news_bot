"""
Economic Update Task - Sends post-event updates for economic events
"""

import pandas as pd
import asyncio
from datetime import datetime
from utils.logger import logger
from scrapers import InvestingScraper, InvestingParams, economic_calendar_to_text
from config import Config
from discord_utils import send_embed_message, send_mention_message
from bot_manager import get_bot
from scheduler_v2.scheduler_manager import get_scheduler


async def economic_update_task(time_str: str):
    """Send post-event update for economic events"""
    try:
        bot = get_bot()
        if not bot:
            logger.error("❌ No Discord bot instance available")
            return
            
        logger.info(f"📊 Sending post-event update for {time_str}")
        
        # Get scheduler first
        discord_scheduler = get_scheduler()
        
        # Initialize scraper
        scraper = InvestingScraper(proxy=Config.PROXY.APP_PROXY, timezone=discord_scheduler.timezone)
        
        # Wait for event data to be published (max 60 seconds)
        max_wait_time = 30
        wait_time = discord_scheduler.post_event_delay if discord_scheduler else 7
        poll_interval = 1
        
        while wait_time < max_wait_time:
            calendar_data = await scraper.get_calendar(
                calendar_name=InvestingParams.CALENDARS.ECONOMIC_CALENDAR,
                current_tab=InvestingParams.TIME_RANGES.TODAY,
                importance=InvestingParams.IMPORTANCE.APP_IMPORTANCES,
                countries=[InvestingParams.COUNTRIES.UNITED_STATES],
                time_zone=InvestingParams.TIME_ZONES.ISRAEL
            )
            
            if calendar_data.empty:
                logger.warning("⚠️ No economic calendar data for update")
                return
            
            # Get events for this time and check if any still need data
            current_events = calendar_data[calendar_data['time'] == time_str]
            unupdated_events = current_events[
                (current_events['previous'].notna()) & 
                (current_events['actual'].isna())
            ]
            
            if unupdated_events.empty:
                logger.info(f"✅ Data updated after {wait_time} seconds")
                break
                
            # Log waiting status and continue polling
            # logger.debug(f"⏳ There are {len(unupdated_events)} events that need to update...")
            wait_time += poll_interval
            await asyncio.sleep(poll_interval)
        else:
            logger.warning(f"⏰ Timeout reached ({max_wait_time}s) waiting for event data update")
        
        if not current_events.empty:
            summary_msg = economic_calendar_to_text(current_events)
            
            # Create update message
            update_msg = f"📊 **Economic Events Update for {time_str}:**\n"
            update_msg += summary_msg
            
            # Send to alert channel
            await send_embed_message(bot, Config.CHANNEL_IDS.ECONOMIC_CALENDAR, update_msg, Config.COLORS.GREEN, "Economic Events Update")
            
            # Send role mention as separate text message
            economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
            await send_mention_message(bot, Config.CHANNEL_IDS.ECONOMIC_CALENDAR, economic_role)
            
            logger.info(f"📊 Post-event update sent for {len(current_events)} events at {time_str}")
        else:
            logger.info(f"📊 No events found for time {time_str}")
            
    except Exception as e:
        logger.error(f"❌ Error in economic update task for {time_str}: {e}")
        bot = get_bot()
        if bot:
            await send_embed_message(
                bot,
                Config.CHANNEL_IDS.ECONOMIC_CALENDAR,
                f"❌ **Economic Update Failed**\nTime: {time_str}\nError: {str(e)}",
                Config.COLORS.RED,
                "📊 Economic Events Update"
            ) 