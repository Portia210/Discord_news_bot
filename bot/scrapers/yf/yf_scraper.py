from scrapers.yf.yf_headers import headers
import requests
from scrapers.yf.yf_params import QouteFields as qf, QuoteSummaryModules as qsm


class YfScraper:
    def __init__(self):
        self.url = None
        self.params = None
        self.method = None
        self.headers = headers


    def make_request(self):
        response = requests.request(self.method, self.url, headers=self.headers, params=self.params)
        response.raise_for_status()
        return response.json()
    
    def get_market_time(self):
        self.url = "https://query1.finance.yahoo.com/v6/finance/markettime"
        self.method = "GET"
        self.params = {
            "formatted": "true",
            "key": "finance",
            "lang": "en-US",
            "region": "US"
        }
        return self.make_request()

    def get_trending_us(self):
        self.url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
        self.method = "GET"
        self.params = {
            "count": "25",
            "fields": "logoUrl,longName,shortName,regularMarketChange,regularMarketChangePercent,regularMarketPrice",
            "format": "true",
            "useQuotes": "true",
            "quoteType": "ALL",
            "lang": "en-US",
            "region": "US",
            "crumb": "X7OMi/Fe4nm"
        }
        return self.make_request()
    
    def get_spark(self, symbols: list[str], interval: str = "1d", range: str = "1mo"):
        url = "https://query1.finance.yahoo.com/v7/finance/spark"
        self.url = url
        self.method = "GET"
        self.params = {
            "includePrePost": "false",
            "includeTimestamps": "false",
            "indicators": "close", 
            "interval": interval,
            "range": range,
            "symbols": ",".join(symbols),
            "lang": "en-US",
            "region": "US"
        }

        return self.make_request()

    def get_quote(self, symbols: list[str]):
        self.url = "https://query1.finance.yahoo.com/v7/finance/quote"
        self.method = "GET"

        wanted_fields = [value for value in vars(qf).values() 
                        if isinstance(value, str)]


        self.params = {
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

        return self.make_request()
    
    def get_quote_summary(self, symbol: str, modules: list[str] = None):
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
        self.url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        self.method = "GET"
        
        if modules is None:
            modules = qsm.DEFAULT_MODULES
        
        self.params = {
            "formatted": "true",
            "modules": ",".join(modules),
            "enablePrivateCompany": "true",
            "overnightPrice": "true",
            "lang": "en-US",
            "region": "US",
            "crumb": "X7OMi/Fe4nm"
        }

        return self.make_request()
    
    def get_market_summary(self):
        self.url = "https://query1.finance.yahoo.com/v6/finance/quote/marketSummary"
        self.method = "GET"

        self.params = {
            "fields": f"{qf.SHORT_NAME},{qf.REGULAR_MARKET_PRICE},{qf.REGULAR_MARKET_CHANGE},{qf.REGULAR_MARKET_CHANGE_PERCENT},{qf.PRE_MARKET_PRICE},{qf.PRE_MARKET_CHANGE},{qf.PRE_MARKET_CHANGE_PERCENT},{qf.POST_MARKET_PRICE},{qf.POST_MARKET_CHANGE},{qf.POST_MARKET_CHANGE_PERCENT}",
            "formatted": "true",
            "lang": "en-US",
            "region": "US",
            "market": "US",
            "crumb": "X7OMi/Fe4nm"
        }

        return self.make_request()


if __name__ == "__main__":
    import json
    from config import Config
    import os
    from utils import write_json_file, convert_iso_time_to_datetime
    from report_generator.news_report import NewsReport
    from utils import write_json_file
    yfr = YfScraper()

    res = yfr.get_quote_summary("IREN")
    write_json_file( "data/yf/iren.json", res)
    # print(json.dumps(res["quoteSummary"]["result"][0], indent=4))