"""
Morning News Report Task - Generates and sends morning news reports
"""

from typing import Any
from utils.logger import logger
from news_pdf.news_report import NewsReport
from discord_utils.send_pdf import send_file
from config import Config
from discord_utils import send_alert
from scheduler_v2.global_scheduler import get_discord_scheduler


async def morning_news_report_task():
    """Generate and send morning news report"""
    try:
        discord_scheduler = get_discord_scheduler()
        if not discord_scheduler:
            logger.error("❌ No DiscordScheduler instance available")
            return
            
        logger.info("📰 Generating morning news report...")
        
        # Generate PDF report
        news_report = NewsReport(discord_scheduler.bot, timezone=discord_scheduler.timezone)
        response = await news_report.send_report_to_server(
            report_time="morning", 
            hours_back=17, 
            url=f"http://{Config.SERVER.CURRENT_SERVER_IP}:8000/api/news-report", 
            headers={"Authorization": "your-secret-token", "Content-Type": "application/json"}
        )
        
        if response:
            link_to_report = response.get("link_to_report")
            
            await send_alert(discord_scheduler.bot, f"📰 **Morning News Report**\nMorning news summary is ready!\n{link_to_report}")
            
            # Send role mention as separate text message
            news_role = Config.NOTIFICATION_ROLES.NEWS_REPORT
            await discord_scheduler.send_mention_text(news_role)
        
        logger.info("✅ Morning news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in morning news report: {e}")
        discord_scheduler = get_discord_scheduler()
        if discord_scheduler:
            await send_alert(
                discord_scheduler.bot,
                f"❌ **Morning News Report Failed**\nError: {str(e)}",
                0xff0000,
                "📰 Morning News Report"
            ) 