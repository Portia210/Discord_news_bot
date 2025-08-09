"""
News Report Task - Generates and sends news reports (morning/evening)
"""

from typing import Any
from utils.logger import logger
from news_pdf.news_report import NewsReport
from discord_utils.send_file import send_file
from config import Config
from discord_utils import send_embed_message, send_mention_message
from bot_manager import get_bot


async def news_report_task(report_time, hours_back):
    """Generate and send news report (morning or evening)"""
    try:
        bot = get_bot()
        if not bot:
            logger.error("❌ No Discord bot instance available")
            return
            
        logger.info("📰 Generating news report...")
        
        news_report = NewsReport(bot, Config.TIMEZONES.APP_TIMEZONE)
        await news_report.generate_full_json_report(report_time, hours_back)
        await news_report.send_report_to_discord(Config.CHANNEL_IDS.MARKET_NEWS, Config.NOTIFICATION_ROLES.NEWS_REPORT)

        
        logger.info("✅ news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in news report: {e}")
        bot = get_bot()
        if bot:
            await send_embed_message(
                bot,
                Config.CHANNEL_IDS.MARKET_NEWS,
                f"❌ **News Report Failed**\nError: {str(e)}",
                Config.COLORS.RED,
                "📰 News Report"
            ) 