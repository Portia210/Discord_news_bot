"""
Daily Task Functions - News Reports
"""

import asyncio
from datetime import datetime
from utils.logger import logger
from news_pdf.pdf_report_generator import PdfReportGenerator
from discord_utils.send_pdf import send_pdf


async def morning_news_report_task(discord_scheduler=None):
    """Morning news report task - runs at 16:00"""
    try:
        logger.info("📰 Generating morning news report...")
        
        # Generate PDF report
        pdf_generator = PdfReportGenerator(discord_scheduler.bot if discord_scheduler else None)
        success = await pdf_generator.generate_pdf_report(output_pdf="news_pdf/morning_report.pdf", report_time="morning", hours_back=17)
        
        if success and discord_scheduler:
            await send_pdf(discord_scheduler.bot, discord_scheduler.alert_channel_id, "news_pdf/morning_report.pdf", "📰 **Morning News Report**\nMorning news summary is ready!", "morning_report.pdf")
        
        logger.info("✅ Morning news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in morning news report: {e}")



async def evening_news_report_task(discord_scheduler=None):
    """Evening news report task - runs at 23:00:03"""
    try:
        logger.info("📰 Generating evening news report...")
        
        # Generate PDF report
        pdf_generator = PdfReportGenerator(discord_scheduler.bot if discord_scheduler else None)
        success = await pdf_generator.generate_pdf_report(output_pdf="news_pdf/evening_report.pdf", report_time="evening", hours_back=7)
        
        if success and discord_scheduler:
            await send_pdf(discord_scheduler.bot, discord_scheduler.alert_channel_id, "news_pdf/evening_report.pdf", "📰 **Evening News Report**\nEnd of day news summary is ready!", "evening_report.pdf")
        
        logger.info("✅ Evening news report completed")
        
    except Exception as e:
        logger.error(f"❌ Error in evening news report: {e}")


