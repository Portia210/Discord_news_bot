#!/usr/bin/env python3
"""
News Report Generator
A class-based system for generating HTML and PDF news reports with theme support.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from utils.logger import logger
from utils.read_write import read_text_file, write_text_file, read_json_file
from yf_scraper.yf_requests import YfRequests
from yf_scraper.qoute_fields import QouteFields as qf
from config import config
import discord
from discord_utils.process_news import process_news_to_list


class PdfReportGenerator:
    """
    A class for generating news reports with theme support.
    
    Handles the complete pipeline from data processing to PDF generation
    with automatic theme detection based on time or manual override.
    """
    
    # Theme configuration
    THEMES = {
        'morning': {
            'name': 'Morning',
            'icon': '☀️',
            'time_range': (6, 18)  # 6 AM to 6 PM
        },
        'evening': {
            'name': 'Evening', 
            'icon': '🌙',
            'time_range': (18, 6)  # 6 PM to 6 AM
        }
    }
    
    def __init__(self, discord_bot: discord.Client, template_file="news_pdf/template.html"):
        """
        Initialize the PdfReportGenerator.
        
        Args:
            discord_bot (discord.Client): Discord bot instance
            template_file (str): Path to the HTML template file
        """
        self.discord_bot = discord_bot
        self.template_file = template_file
        self.yf_requests = YfRequests()
        self._validate_files()
    
    def _validate_files(self):
        """Validate that required files exist."""
        required_files = [
            self.template_file,
            "news_pdf/style/style.css",
            "news_pdf/style/morning.css", 
            "news_pdf/style/evening.css"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            raise FileNotFoundError(f"Required files not found: {', '.join(missing_files)}")


    def get_theme_info(self, report_time: str = 'auto') -> dict:
        """
        Get information about the current theme.
        
        Args:
            report_time (str): Theme preference
            
        Returns:
            dict: Theme information including name and icon
        """
        theme = self._determine_theme(report_time)
        return {
            'theme': theme,
            'name': self.THEMES[theme]['name'],
            'icon': self.THEMES[theme]['icon']
        }



    async def _load_news_data(self, hours_back: int = 24) -> list:
        """
        Load news data from Discord channel.
        
        Args:
            hours_back (int): Number of hours to look back
            
        Returns:
            list: List of news items
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
            change_amount = company.get(qf.REGULAR_MARKET_CHANGE)["fmt"]

            symbol_data = {
                # remove signs such as $ / ! ^ etc.
                "ticker": company.get("symbol", "N/A").replace(r"[^a-zA-Z0-9]", ""),
                "company": company.get(qf.SHORT_NAME, "N/A"),
                "price": company.get(qf.REGULAR_MARKET_PRICE)["fmt"],
                "changeAmount": change_amount,
                "changePercent": company.get(qf.REGULAR_MARKET_CHANGE_PERCENT)["fmt"],
                "isPositive": float(change_amount) > 0
            }
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"❌ Error processing company data: {e}")
            return None
    

    def _determine_theme(self, report_time: str = 'auto') -> str:
        """
        Determine the appropriate theme based on time or override.
        
        Args:
            report_time (str): 'morning', 'evening', or 'auto'
            
        Returns:
            str: The determined theme ('morning' or 'evening')
        """
        if report_time in ['morning', 'evening']:
            return report_time
        
        # Auto-detect based on current time
        current_hour = datetime.now(config.app_timezone).hour
        
        if 6 <= current_hour < 18:
            return 'morning'
        else:
            return 'evening'
    
    def _generate_html_report(self, template: str, news_data: list, prices_data: list, report_time: str = 'auto') -> str:
        """
        Merge news data, price symbols, and theme into the HTML template.
        
        Args:
            template (str): HTML template content
            news_data (list): List of news items
            prices_data (list): List of price symbol data
            report_time (str): Theme preference
            
        Returns:
            str: Merged HTML content or None if failed
        """
        try:
            # Convert data to JSON strings for JavaScript
            news_json = json.dumps(news_data, ensure_ascii=False, indent=2)
            price_symbols_json = json.dumps(prices_data or [], ensure_ascii=False, indent=2)
            
            # Determine theme
            theme = self._determine_theme(report_time)
            
            # Replace placeholders in template
            html_content = template.replace('{{NEWS_DATA}}', news_json)
            html_content = html_content.replace('{{PRICE_SYMBOLS}}', price_symbols_json)
            html_content = html_content.replace('{{REPORT_TIME}}', theme)
            
            logger.info(f"✅ Successfully merged {len(news_data)} news items and {len(prices_data or [])} price symbols with {theme} theme")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Error merging data: {e}")
            return None
 
    
    async def _convert_html_to_pdf(self, html_file_path: str, pdf_file_path: str) -> bool:
        """
        Convert HTML file to PDF using Playwright.
        
        Args:
            html_file_path (str): Path to the HTML file
            pdf_file_path (str): Path for the output PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Convert file path to file URL
                file_url = f"file://{os.path.abspath(html_file_path)}"
                
                # Navigate to the HTML file
                await page.goto(file_url)
                
                # Wait for content to load
                await page.wait_for_load_state('networkidle')
                
                # Generate PDF with RTL support and better page break handling
                await page.pdf(
                    path=pdf_file_path,
                    format='A4',
                    print_background=True,
                    prefer_css_page_size=True
                )
                
                await browser.close()
            
            logger.info(f"✅ Successfully converted HTML to PDF: {pdf_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error converting HTML to PDF: {e}")
            return False
    
    async def generate_pdf_report(self, output_file: str = "news_pdf/output.html", 
                                pdf_file: str = "news_pdf/output.pdf", report_time: str = 'auto', 
                                hours_back: int = 24) -> bool:
        """
        Generate a complete PDF report from news data with price symbols.
        This is the main method for generating reports.
        
        Args:
            output_file (str): Path for the output HTML file
            pdf_file (str): Path for the output PDF file
            report_time (str): Theme preference ('morning', 'evening', 'auto')
            hours_back (int): Number of hours to look back for news
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("🚀 Starting PDF report generation...")
            
            # Step 1: Load news data
            news_data = await self._load_news_data(hours_back)
            if not news_data:
                logger.warning("⚠️ No news data loaded, continuing with empty news list")
            
            # Step 2: Load market summary data
            prices_data = await self._load_market_summary()
            if not prices_data:
                logger.warning("⚠️ No market data loaded, continuing with empty price list")
            
            # Step 3: Load HTML template
            try:
                template = read_text_file(self.template_file)
                logger.info("✅ HTML template loaded successfully")
            except Exception as e:
                logger.error(f"❌ Error loading HTML template: {e}")
                return False
            
            # Step 4: Generate HTML content
            html_content = self._generate_html_report(template, news_data, prices_data, report_time)
            if not html_content:
                logger.error("❌ Failed to generate HTML content")
                return False
            
            # Step 5: Save HTML file
            try:
                write_text_file(output_file, html_content)
                logger.info(f"✅ HTML file saved: {output_file}")
            except Exception as e:
                logger.error(f"❌ Error saving HTML file: {e}")
                return False
            
            # Step 6: Convert to PDF
            pdf_success = await self._convert_html_to_pdf(output_file, pdf_file)
            if not pdf_success:
                logger.error("❌ Failed to convert HTML to PDF")
                return False
            
            logger.info(f"🎉 PDF report generated successfully: {pdf_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF report: {e}")
            return False
    
