"""
Economic Warning Task - Sends 5-minute warnings for economic events
"""

import pandas as pd
from utils.logger import logger
from scrapers import InvestingScraper, InvestingParams
from config import Config
from discord_utils import send_embed_message, send_mention_message
from bot_manager import get_bot
from scheduler_v2.scheduler_manager import get_scheduler


async def economic_warning_task(time_str: str, time_events: pd.DataFrame):
    """Send 5-minute warning for economic events"""
    try:
        bot = get_bot()
        if not bot:
            logger.error("❌ No Discord bot instance available")
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
        await send_embed_message(bot, Config.CHANNEL_IDS.ECONOMIC_CALENDAR, warning_msg, Config.COLORS.ORANGE, "⚠️ Economic Events Warning")
        
        # Send role mention as separate text message
        economic_role = Config.NOTIFICATION_ROLES.ECONOMIC_CALENDAR
        discord_scheduler = get_scheduler()
        if discord_scheduler:
            await discord_scheduler.send_mention_text(economic_role)
        
        logger.info(f"⚠️ 5-minute warning sent for {len(time_events)} events at {time_str}")
        
    except Exception as e:
        logger.error(f"❌ Error in economic warning task for {time_str}: {e}")
        bot = get_bot()
        if bot:
            await send_embed_message(
                bot,
                Config.CHANNEL_IDS.ECONOMIC_CALENDAR,
                f"❌ **Economic Warning Failed**\nTime: {time_str}\nError: {str(e)}",
                Config.COLORS.RED,
                "⚠️ Economic Events Warning"
            ) 