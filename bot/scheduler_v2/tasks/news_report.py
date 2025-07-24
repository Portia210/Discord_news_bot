"""
Daily Task Functions - News Reports
"""

import asyncio
from datetime import datetime
from utils.logger import logger
from news_pdf.news_report import NewsReport
from discord_utils.send_pdf import send_pdf
from config import Config
from scheduler_v2.discord_scheduler import DiscordScheduler
from discord_utils.role_utils import get_role_mention


async def morning_news_report_task(discord_scheduler: DiscordScheduler):
    """Morning news report task - runs at 16:00"""
    try:
        logger.info("📰 Generating morning news report...")
        
        # Generate PDF report
        news_report = NewsReport(discord_scheduler.bot, timezone=discord_scheduler.timezone)
        response = await news_report.send_report_to_server(report_time="morning", hours_back=17, url=f"http://{Config.SERVER.CURRENT_SERVER_IP}:8000/api/news-report", headers={"Authorization": "your-secret-token", "Content-Type": "application/json"})
        
        if response:
            link_to_report = response.get("link_to_report")
            
            await discord_scheduler.send_alert(f"📰 **Morning News Report**\nMorning news summary is ready!\n{link_to_report}")
            
            # Send role mention as separate text message
            news_role = Config.NOTIFICATION_ROLES.NEWS_REPORT
            await discord_scheduler.send_mention_text(news_role)
        
        logger.info("✅ Morning news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in morning news report: {e}")


async def evening_news_report_task(discord_scheduler: DiscordScheduler):
    """Evening news report task - runs at 23:00:03"""
    try:
        logger.info("📰 Generating evening news report...")
        
        # Generate PDF report
        news_report = NewsReport(discord_scheduler.bot, timezone=discord_scheduler.timezone)
        response = await news_report.send_report_to_server(report_time="evening", hours_back=7, url=f"http://{Config.SERVER.CURRENT_SERVER_IP}:{Config.SERVER.PORT}/api/news-report", headers={"Authorization": Config.SERVER.API_TOKEN, "Content-Type": "application/json"})
        
        if response:
            link_to_report = response.get("link_to_report")
            
            await discord_scheduler.send_alert(f"📰 **Evening News Report**\nEnd of day news summary is ready!\n{link_to_report}")
            
            # Send role mention as separate text message
            news_role = Config.NOTIFICATION_ROLES.NEWS_REPORT
            await discord_scheduler.send_mention_text(news_role)
        
        logger.info("✅ Evening news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in evening news report: {e}")


