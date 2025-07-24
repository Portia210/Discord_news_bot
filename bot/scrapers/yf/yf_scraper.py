from scrapers.yf.yf_headers import headers
import requests
from scrapers.yf.yf_params import QouteFields as qf


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
    from news_pdf.news_report import NewsReport
    yfr = YfScraper()

    # res = yfr.get_market_summary()
    # print(json.dumps(res["marketSummaryResponse"]["result"][0], indent=4))
    # res = yfr.get_market_time()
    # print(json.dumps(res, indent=4))
    # time = res["finance"]["marketTimes"][0]["marketTime"][0]["time"]
    # indexes_futures = ["ES=F", "NQ=F", "RTY=F", "^VIX"]
    # indexes = ["^GSPC", "^IXIC", "^DJI", "^RUT"]
    # commodities = ["GC=F", "SI-F", "CL=F", "CG=F"] 
    # crypto = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD"]
    only_nasdaq = ["^IXIC"]
    res = yfr.get_quote(symbols=only_nasdaq)
    news_report = NewsReport(discord_bot=None, timezone=None)
    symbols_data = []
    symbols = res["quoteResponse"]["result"]
    # for symbol in symbols:
    #     try:
    #         data_processed = news_report._process_company_data(symbol)
    #         if data_processed is not None:
    #             symbols_data.append(data_processed)
    #     except Exception as e:
    #         print(f"Error processing symbol {symbol.keys()}")

    print(symbols)
    