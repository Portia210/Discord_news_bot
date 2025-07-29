"""
Economic Warning Task - Sends 5-minute warnings for economic events
"""

import pandas as pd
from utils.logger import logger
from scrapers import InvestingScraper, InvestingParams
from config import Config
from discord_utils import send_alert
from scheduler_v2.global_scheduler import get_discord_scheduler


async def economic_warning_task(time_str: str, time_events: pd.DataFrame):
    """Send 5-minute warning for economic events"""
    try:
        discord_scheduler = get_discord_scheduler()
        if not discord_scheduler:
            logger.error("❌ No DiscordScheduler instance available")
            return
            
        logger.info(f"⚠️ Sending 5-minute warning for {time_str}")
        
        if time_events.empty:
            logger.info(f"⚠️ No events found for time {time_str}")
            return
        
        # Create warning message from DataFrame
        event_names = time_events['description'].fillna('Unknown Event').tolist()
        
        warning_msg = f"⚠️ **Events coming in 5 minutes at {time_str}:**\n"
        warning_msg += ", ".join(event_names)
        
        # Send to alert channel
        await send_alert(discord_scheduler.bot, warning_msg, 0xffa500, "⚠️ Economic Events Warning")
        
        # Send role mention as separate text message
        economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
        await discord_scheduler.send_mention_text(economic_role)
        
        logger.info(f"⚠️ 5-minute warning sent for {len(time_events)} events at {time_str}")
        
    except Exception as e:
        logger.error(f"❌ Error in economic warning task for {time_str}: {e}")
        discord_scheduler = get_discord_scheduler()
        if discord_scheduler:
            await send_alert(
                discord_scheduler.bot,
                f"❌ **Economic Warning Failed**\nTime: {time_str}\nError: {str(e)}",
                0xff0000,
                "⚠️ Economic Events Warning"
            ) 