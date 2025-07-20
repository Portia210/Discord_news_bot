#!/usr/bin/env python3
"""
News Report Generator
A class-based system for generating HTML and PDF news reports with theme support.
"""

import json
from datetime import datetime
from utils.logger import logger
from yf_scraper.yf_requests import YfRequests
from yf_scraper.qoute_fields import QouteFields as qf
import pytz
from config import Config
import discord
from discord_utils.process_news import process_news_to_list
import requests
import asyncio

class NewsReport:
    THEMES = ["morning", "evening"]
    
    def __init__(self, discord_bot: discord.Client, timezone: pytz.timezone):
        """
        Initialize the PdfReportGenerator.
        
        Args:
            discord_bot (discord.Client): Discord bot instance
            template_file (str): Path to the HTML template file
        """
        self.discord_bot = discord_bot
        self.timezone = timezone
        self.yf_requests = YfRequests()
    
   

    def _get_theme(self, report_time: str = 'auto') -> dict:
        if report_time in self.THEMES:
            return report_time
        
        # Auto-detect based on current time
        current_hour = datetime.now(self.timezone).hour
        
        if 6 <= current_hour < 18:
            return 'morning'
        else:
            return 'evening'



    async def _read_discord_news(self, hours_back: int = 24) -> list:
        """
        Load news data from Discord channel.
        """
        try:
            news_list = await process_news_to_list(
                discord_bot=self.discord_bot, 
                hours_back=hours_back
            )
            logger.info(f"✅ Loaded {len(news_list)} news items")
            return news_list
        except Exception as e:
            logger.error(f"❌ Error loading news data: {e}")
            return []


    async def _load_market_summary(self) -> list:
        """
        Load and transform price data from market summary.
        
        Returns:
            list: List of price symbol data for the template
        """
        try:
            response = self.yf_requests.get_market_summary()
            price_symbols = []
            
            for company in response["marketSummaryResponse"]["result"]:
                try:
                    symbol_data = self._process_company_data(company)
                    if symbol_data:
                        price_symbols.append(symbol_data)
                        
                except Exception as e:
                    logger.error(f"❌ Error processing company data: {e}")
                    continue
            
            logger.info(f"✅ Loaded {len(price_symbols)} price symbols from market summary")
            return price_symbols
            
        except Exception as e:
            logger.error(f"❌ Error loading market summary: {e}")
            return []
    

    def _process_company_data(self, company: dict) -> dict:
        """
        Process individual company data from market summary.
        
        Args:
            company (dict): Company data from market summary
            
        Returns:
            dict: Processed symbol data or None if invalid
        """
        try:
            symbol_data = {
                # remove signs such as $ / ! ^ etc.
                "ticker": company.get("symbol", "N/A").replace(r"[^a-zA-Z0-9]", ""),
                "company": company.get(qf.SHORT_NAME, "N/A"),
                "price": company.get(qf.REGULAR_MARKET_PRICE)["fmt"],
                "change_amount": company.get(qf.REGULAR_MARKET_CHANGE)["fmt"],
                "change_percent": company.get(qf.REGULAR_MARKET_CHANGE_PERCENT)["fmt"],
                "is_positive": float(company.get(qf.REGULAR_MARKET_CHANGE)["fmt"]) > 0
            }
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"❌ Error processing company data: {e}")
            return None
    

    async def _generate_full_json_report(self, report_time: str = 'auto', hours_back: int = 24) -> dict:
        """
        Generate a full JSON report with news and prices data.
        """
        prices_data = await self._load_market_summary()
        news_data = await self._read_discord_news(hours_back)
        report_time = self._get_theme(report_time)
        hebrew_report_time = "בוקר" if report_time == "morning" else "ערב"
        return {
            "date": datetime.now(self.timezone).strftime("%Y-%m-%d"),
            "title": f"דוח חדשות פיננסיות - {hebrew_report_time}",
            "report_title": f"דוח חדשות {hebrew_report_time}",
            "report_subtitle": "עדכוני שוק ופיננסים אחרונים",
            "generation_time": datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S"),
            "report_time": report_time,
            "news_data": news_data,
            "price_symbols": prices_data,
        }
    
    async def send_report_to_server(self, report_time: str, hours_back: int, url: str, headers: dict = None):
        """
        Send the report to the server.
        """
        report = await self._generate_full_json_report(report_time, hours_back)
        logger.info(f"🔍 Sending report to server: {url}")
        logger.info(f"🔍 Report time: {report_time}")
        logger.info(f"🔍 Hours back: {hours_back}")
        logger.info(f"🔍 Headers: {headers}")
        logger.info(f"🔍 Report: {len(report)}")
        try:
            response = requests.post(url, headers=headers, json=report)
            if response.status_code != 201:
                logger.error(f"❌ Error sending report to server: {response.status_code}")
                logger.error(f"❌ Response text: {response.text}")
                return None
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error sending report to server: {e}")
            return None
    
    
if __name__ == "__main__":
    news_report = NewsReport(discord_bot=None, timezone=pytz.timezone("Asia/Jerusalem"))
    res = asyncio.run(news_report._generate_full_json_report())
    print(json.dumps(res, indent=4))