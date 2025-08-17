import aiohttp
import asyncio
from scrapers.yf.yf_headers import headers
from scrapers.yf.yf_params import QouteFields as qf, QuoteSummaryModules as qsm
from config import Config
from utils import logger, safe_get


class YfScraper:
    def __init__(self, proxy=None):
        self.headers = headers
        self.proxy = proxy or Config.PROXY.APP_PROXY

    async def make_request(self, url: str, params: dict = None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params, proxy=self.proxy) as response:
                    if not response.ok:
                        logger.error(f"Error: {response.status} {await response.text()}")
                        return None
                    else:
                        return await response.json()
        except Exception as e:
            logger.error(f"Error making request to {url}: {e}")
            return None
    
    async def get_market_time(self):
        url = "https://query1.finance.yahoo.com/v6/finance/markettime"
        params = {
            "formatted": "true",
            "key": "finance",
            "lang": "en-US",
            "region": "US"
        }
        return await self.make_request(url, params)

    async def get_trending_us(self):
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
        params = {
            "count": "25",
            "fields": "logoUrl,longName,shortName,regularMarketChange,regularMarketChangePercent,regularMarketPrice",
            "format": "true",
            "useQuotes": "true",
            "quoteType": "ALL",
            "lang": "en-US",
            "region": "US",
            "crumb": "X7OMi/Fe4nm"
        }
        return await self.make_request(url, params)
    
    async def get_spark(self, symbols: list[str], interval: str = "1d", range: str = "1mo"):
        url = "https://query1.finance.yahoo.com/v7/finance/spark"
        params = {
            "includePrePost": "false",
            "includeTimestamps": "false",
            "indicators": "close", 
            "interval": interval,
            "range": range,
            "symbols": ",".join(symbols),
            "lang": "en-US",
            "region": "US"
        }

        return await self.make_request(url, params)

    async def get_chart_data(self, symbol: str, period1: int, period2: int, interval: str = "1d", include_pre_post: bool = True, events: str = "div|split|earn"):
        """
        Get historical chart data for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'GOOGL')
            period1: Start timestamp (epoch seconds)
            period2: End timestamp (epoch seconds)
            interval: Time interval ('1d', '1wk', '1mo', etc.)
            include_pre_post: Include pre/post market data
            events: Events to include ('div|split|earn' for dividends, splits, earnings)
        """
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            "period1": str(period1),
            "period2": str(period2),
            "interval": interval,
            "includePrePost": str(include_pre_post).lower(),
            "events": events,
            "lang": "en-US",
            "region": "US",
            "source": "cosaic"
        }
        
        return await self.make_request(url, params)

    async def get_quote(self, symbols: list[str]):
        url = "https://query1.finance.yahoo.com/v7/finance/quote"

        wanted_fields = [value for value in vars(qf).values() 
                        if isinstance(value, str)]

        params = {
            "fields": ",".join(wanted_fields),
            "formatted": "true",
            "imgHeights": "50",
            "imgLabels": "logoUrl",
            "imgWidths": "50",
            "symbols": ",".join(symbols),
            "enablePrivateCompany": "true",
            "overnightPrice": "true",
            "topPickThisMonth": "true",
            "lang": "en-US",
            "region": "US",
            "crumb": "X7OMi/Fe4nm",
        }

        return await self.make_request(url, params)
    
    
    async def get_market_summary(self):
        url = "https://query1.finance.yahoo.com/v6/finance/quote/marketSummary"

        params = {
            "fields": f"{qf.SHORT_NAME},{qf.REGULAR_MARKET_PRICE},{qf.REGULAR_MARKET_CHANGE},{qf.REGULAR_MARKET_CHANGE_PERCENT},{qf.PRE_MARKET_PRICE},{qf.PRE_MARKET_CHANGE},{qf.PRE_MARKET_CHANGE_PERCENT},{qf.POST_MARKET_PRICE},{qf.POST_MARKET_CHANGE},{qf.POST_MARKET_CHANGE_PERCENT}",
            "formatted": "true",
            "lang": "en-US",
            "region": "US",
            "market": "US",
            "crumb": "X7OMi/Fe4nm"
        }

        return await self.make_request(url, params)


    async def get_quote_summary(self, symbol: str, modules: list[str] = None):
        """
        Get detailed quote summary for a specific symbol with various modules
        
        Args:
            symbol: Stock symbol (e.g., 'NVO')
            modules: List of modules to include. Default includes:
                - assetProfile: Company profile information
                - secFilings: SEC filings data
                - calendarEvents: Earnings and events calendar
                - price: Current price data
                - summaryDetail: Summary statistics
                - pageViews: Page view metrics
                - financialsTemplate: Financial data template
                - quoteUnadjustedPerformanceOverview: Performance data
        """
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        
        if modules is None:
            modules = qsm.DEFAULT_MODULES
        
        params = {
            "formatted": "true",
            "modules": ",".join(modules),
            "enablePrivateCompany": "true",
            "overnightPrice": "true",
            "lang": "en-US",
            "region": "US",
            "crumb": "X7OMi/Fe4nm"
        }

        return await self.make_request(url, params)
    
  
    
    def parse_quote_summary(self, result):
        data = {}
        data["symbol"] = safe_get(result, '["quoteSummary"]["result"][0]["price"]["symbol"]')
        data["type"] = safe_get(result, '["quoteSummary"]["result"][0]["price"]["quoteType"]')
        data["company_name"] = safe_get(result, '["quoteSummary"]["result"][0]["price"]["longName"]')
        data["website"] = safe_get(result, '["quoteSummary"]["result"][0]["assetProfile"]["website"]')
        data["ir_website"] = safe_get(result, '["quoteSummary"]["result"][0]["assetProfile"]["irWebsite"]')
        data["industry"] = safe_get(result, '["quoteSummary"]["result"][0]["assetProfile"]["industry"]')
        data["sector"] = safe_get(result, '["quoteSummary"]["result"][0]["assetProfile"]["sector"]')
        data["business_summary"] = safe_get(result, '["quoteSummary"]["result"][0]["assetProfile"]["longBusinessSummary"]')
        data["earnings_date"] = safe_get(result, '["quoteSummary"]["result"][0]["calendarEvents"]["earnings"]["earningsDate"][0]["fmt"]')
        data["is_earning_estimated"] = safe_get(result, '["quoteSummary"]["result"][0]["calendarEvents"]["earnings"]["isEarningsDateEstimate"]')
        data["last_price"] = safe_get(result, '["quoteSummary"]["result"][0]["price"]["regularMarketPrice"]["fmt"]')
        pref_overview = safe_get(result, '["quoteSummary"]["result"][0]["quoteUnadjustedPerformanceOverview"]["performanceOverview"]')
        data["pref_overview"] = {}
        for key, value in pref_overview.items():
            data["pref_overview"][key] = value.get("fmt")
        return data

if __name__ == "__main__":
    import json
    from config import Config
    import os
    import pandas as pd
    from utils import write_json_file, convert_iso_time_to_datetime, get_json_tree, safe_get, logger, write_text_file
    from report_generator.news_report import NewsReport

    yfr = YfScraper()
    res = asyncio.run(yfr.get_quote(["nvo", "spy", "qqq", "spmo", "iwm", "gld"]))
    tree = get_json_tree(res, list_limit = 2)
    write_text_file("data/yf/quote_with_specific_fields.yaml", tree)
        
    
