#!/usr/bin/env python3
"""
News Report Generator
A class-based system for generating HTML and PDF news reports with theme support.
"""

import json
from datetime import datetime
from utils.logger import logger
from scrapers import YfScraper, QouteFields as qf
import pytz
import discord
from ai_tools.process_discord_news import process_news_to_list
import requests
import asyncio
from discord_utils import send_embed_message, send_mention_message
from config import Config

class NewsReport:
    
    def __init__(self, discord_bot: discord.Client, timezone: str):
        """
        Initialize the PdfReportGenerator.
        
        Args:
            discord_bot (discord.Client): Discord bot instance
            template_file (str): Path to the HTML template file
        """
        self.discord_bot = discord_bot
        self.timezone = pytz.timezone(timezone)
        self.yf_requests = YfScraper()
        self.symbols_config = self._load_symbols_config()
        self.full_report = None
    
    def _load_symbols_config(self) -> dict:
        """Load symbols configuration from JSON file"""
        try:
            with open("news_pdf/symbols_config.json", "r") as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"❌ Error loading symbols config: {e}")
            return {}
    
   

    def _get_report_time(self, report_time: str = 'auto') -> dict:
        try:
            if report_time in ["morning", "evening"]:
                return report_time
            elif report_time == "auto":
                # Auto-detect based on current time
                current_hour = datetime.now(self.timezone).hour
                if 6 <= current_hour < 18:
                    return 'morning'
                else:
                    return 'evening'
            else:
                logger.error(f"❌ Invalid report time: {report_time}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting theme: {e}")
            return None



    async def _read_and_process_discord_news(self, hours_back: int = 24) -> list:
        """
        Load news data from Discord channel.
        """
        try:
            news_list = await process_news_to_list(
                discord_bot=self.discord_bot, 
                hours_back=hours_back
            )
            
            # Sort news by date (oldest first)
            if news_list:
                news_list.sort(key=lambda x: x.get('date', ''), reverse=False)
                logger.info(f"✅ Loaded and sorted {len(news_list)} news items by date")
            else:
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
            yfr = YfScraper()
            # Group symbols by type

            all_symbols = [symbol for symbol, data in self.symbols_config.items() if data["type"] in ["index", "commodity", "crypto"]]
            res = yfr.get_quote(symbols= all_symbols)
            if res is None:
                logger.error(f"❌ Error loading market summary: {res}")
                return []
            return self._process_market_summary(res)
            
        except Exception as e:
            logger.error(f"❌ Error loading market summary: {e}")
            return []
            
    def _process_market_summary(self, res: dict) -> dict:
        # Group symbols by type
        categorized_data = {}
        
        for symbol_result in res["quoteResponse"]["result"]:
            try:
                data_processed = self._process_symbol_data(symbol_result)
                if data_processed is not None:
                    symbol = data_processed["ticker"]
                    if symbol not in self.symbols_config:
                        logger.error(f"❌ Symbol {symbol} not found in symbols config")
                        continue
                    
                    data_processed["name"] = self.symbols_config[symbol]["name"]
                    symbol_type = self.symbols_config[symbol]["type"]
                    data_processed["type"] = symbol_type
                    
                    # Add to appropriate category
                    if symbol_type not in categorized_data:
                        categorized_data[symbol_type] = []
                    categorized_data[symbol_type].append(data_processed)
                    
            except Exception as e:
                print(f"Error processing symbol {symbol_result}: {e}")
        
        return categorized_data

    def _process_symbol_data(self, company: dict) -> dict:
        """
        Process individual symbol data from market summary.
        
        Args:
            company (dict): Company data from market summary
            
        Returns:
            dict: Processed symbol data or None if invalid
        """
        try:
            symbol_data = {
                "ticker": company.get("symbol", "N/A"),
                "name": "N/A",
                "type": "N/A",
                "price": company.get(qf.REGULAR_MARKET_PRICE)["fmt"],
                "abs_change": company.get(qf.REGULAR_MARKET_CHANGE)["fmt"],
                "percent_change": company.get(qf.REGULAR_MARKET_CHANGE_PERCENT)["fmt"],
                "is_positive": float(company.get(qf.REGULAR_MARKET_CHANGE)["raw"]) > 0
            }
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"❌ Error processing market summary: {json.dumps(company, indent=4)}")
            logger.error(f"❌ Error processing market summary: {e}")
            return None
    

    async def generate_full_json_report(self, report_time: str = 'auto', hours_back: int = 24) -> dict:
        """
        Generate a full JSON report with news and prices data.
        """
        try:
            categorized_prices = await self._load_market_summary()
            news_data = await self._read_and_process_discord_news(hours_back)
            report_time = self._get_report_time(report_time)
            
            hebrew_report_time = "בוקר" if report_time == "morning" else "ערב"
            self.full_report =  {
                "date": datetime.now(self.timezone).strftime("%Y-%m-%d"),
                "title": f"דוח חדשות פיננסיות - {hebrew_report_time}",
                "report_title": f"דוח חדשות {hebrew_report_time}",
                "report_subtitle": "עדכוני שוק ופיננסים אחרונים",
                "generation_time": datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S"),
                "report_time": report_time,
                "news_data": news_data,
                "categorized_prices": categorized_prices,
            }
            return self.full_report
        except Exception as e:
            logger.error(f"❌ Error generating full JSON report: {e}")
            return None
        
    async def send_report_to_server(self) -> str:
        """
        Send the report to the server.
        """
        if not self.full_report:
            logger.error(f"❌ use first generate_full_json_report before sending to server")
            return None
        
        url = f"http://{Config.SERVER.CURRENT_SERVER_IP}:{Config.SERVER.PORT}/api/news-report"
        headers = {"Authorization": Config.SERVER.API_TOKEN, "Content-Type": "application/json"}
        logger.debug(f"🔍 Sending report to server: {url}")
        try:
            response = requests.post(url, headers=headers, json=self.full_report)
            if response.status_code != 201:
                logger.error(f"❌ Error sending report to server: {response.status_code}")
                logger.error(f"❌ Response text: {response.text}")
                return None
            
            # Parse the JSON response
            response_data = response.json()
            link_to_report = response_data.get("link_to_report", "")
            return link_to_report
        except Exception as e:
            logger.error(f"❌ Error sending report to server: {e}")
            return None
        
    async def send_report_to_discord(self, channel_id: int, notification_role: str):
        """
        Create and send embeds with the report data to Discord
        """
        try:
            if not self.full_report:
                logger.error(f"❌ use first generate_full_json_report before sending to discord")
                return None
        
            
            # Create market data summary embed with inline fields
            categorized_prices = self.full_report.get("categorized_prices", {})
            if categorized_prices:
                # Create embed
                market_embed = discord.Embed(
                    title="📊 תנועות שוק נכון לעכשיו",
                    color=Config.COLORS.GREEN
                )
                
                # Category headers mapping
                category_headers = {
                    "index": "📈 **מדדים**",
                    "index_futures": "📈 **חוזים עתידיים מדדים**",
                    "commodity": "💎 **סחורות**", 
                    "crypto": "🚀 **קריפטו**"
                }
                
                # Process each category
                for category_type, symbols in categorized_prices.items():
                    if symbols:  # Only process if category has symbols
                        # Add category header
                        header = category_headers.get(category_type, f"**{category_type.title()}**")
                        market_embed.add_field(name=header, value="", inline=False)
                        
                        for symbol in symbols[:6]:  # Limit to 6 per category
                            change_emoji = "🟢" if symbol.get("is_positive", False) else "🔴"
                            field_name = f"{change_emoji} {symbol.get('name', 'N/A')}"
                            field_value = f"{symbol.get('price', 'N/A')}\n{symbol.get('percent_change', 'N/A')}"
                            market_embed.add_field(name=field_name, value=field_value, inline=True)
                
                # Send market embed
                channel = self.discord_bot.get_channel(channel_id)
                if channel:
                    await channel.send(embed=market_embed)
            
            link_to_report = await self.send_report_to_server()
            # Create news summary embed
            news_data = self.full_report.get("news_data", [])
            if news_data:
                news_summary = "📰 **חדשות אחרונות:**\n\n"
                news_summary += f"[קישור לקריאה נוחה של החדשות באתר האינטרנט]({link_to_report})\n\n"

                for i, news in enumerate(news_data, 1):  
                    message = news.get('message', 'N/A')
                    time = news.get('time', 'N/A')
                    links = news.get('links', [])
                    
                    news_summary += f"{i}. {message}"
                    if time != 'N/A':
                        news_summary += f" **({time})**"
                    
                    # Handle multiple links
                    if links:
                        # New format with multiple links
                        link_texts = []
                        for j, link_url in enumerate(links, 1):
                            if link_url:
                                link_texts.append(f"[קישור {j}]({link_url})")
                        if link_texts:
                            news_summary += f"\n{' | '.join(link_texts)}"  # New line with pipe separator between links
                    
                    news_summary += "\n\n"
                
                
                await send_embed_message(
                    bot=self.discord_bot,
                    channel_id=channel_id,
                    message=news_summary,
                    color=Config.COLORS.ORANGE,
                    title="📰 חדשות פיננסיות",
                    error_context="send_report_to_discord"
                )
            
            # Send role mention last
            await send_mention_message(self.discord_bot, channel_id, notification_role)
            
            logger.info(f"✅ Successfully sent report to Discord")
            return True

        except Exception as e:
            logger.error(f"❌ Error sending report to discord: {e}")
            return None
    
    
if __name__ == "__main__":
    news_report = NewsReport(discord_bot=None, timezone=pytz.timezone("Asia/Jerusalem"))
    res = asyncio.run(news_report.generate_full_json_report())
    print(json.dumps(res, indent=4))