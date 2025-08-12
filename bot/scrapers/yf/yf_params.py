class QouteFields:
    FIFTY_TWO_WEEK_HIGH = "fiftyTwoWeekHigh"
    FIFTY_TWO_WEEK_LOW = "fiftyTwoWeekLow"
    FROM_CURRENCY = "fromCurrency"
    FROM_EXCHANGE = "fromExchange"
    HEAD_SYMBOL_AS_STRING = "headSymbolAsString"
    LOGO_URL = "logoUrl"
    LONG_NAME = "longName"
    MARKET_CAP = "marketCap"
    MESSAGE_BOARD_ID = "messageBoardId"
    OPTIONS_TYPE = "optionsType"
    OVERNIGHT_MARKET_TIME = "overnightMarketTime"
    OVERNIGHT_MARKET_PRICE = "overnightMarketPrice"
    OVERNIGHT_MARKET_CHANGE = "overnightMarketChange"
    OVERNIGHT_MARKET_CHANGE_PERCENT = "overnightMarketChangePercent"
    REGULAR_MARKET_TIME = "regularMarketTime"
    REGULAR_MARKET_CHANGE = "regularMarketChange"
    REGULAR_MARKET_CHANGE_PERCENT = "regularMarketChangePercent"
    REGULAR_MARKET_OPEN = "regularMarketOpen"
    REGULAR_MARKET_PRICE = "regularMarketPrice"
    REGULAR_MARKET_SOURCE = "regularMarketSource"
    REGULAR_MARKET_VOLUME = "regularMarketVolume"
    POST_MARKET_TIME = "postMarketTime"
    POST_MARKET_PRICE = "postMarketPrice"
    POST_MARKET_CHANGE = "postMarketChange"
    POST_MARKET_CHANGE_PERCENT = "postMarketChangePercent"
    PRE_MARKET_TIME = "preMarketTime"
    PRE_MARKET_PRICE = "preMarketPrice"
    PRE_MARKET_CHANGE = "preMarketChange"
    PRE_MARKET_CHANGE_PERCENT = "preMarketChangePercent"
    SHORT_NAME = "shortName"
    TO_CURRENCY = "toCurrency"
    TO_EXCHANGE = "toExchange"
    UNDERLYING_EXCHANGE_SYMBOL = "underlyingExchangeSymbol"
    UNDERLYING_SYMBOL = "underlyingSymbol"
    STOCK_STORY = "stockStory"

class QuoteSummaryModules:
    ASSET_PROFILE = "assetProfile"
    SEC_FILINGS = "secFilings"
    CALENDAR_EVENTS = "calendarEvents"
    PRICE = "price"
    SUMMARY_DETAIL = "summaryDetail"
    PAGE_VIEWS = "pageViews"
    FINANCIALS_TEMPLATE = "financialsTemplate"
    QUOTE_UNADJUSTED_PERFORMANCE_OVERVIEW = "quoteUnadjustedPerformanceOverview"
    
    # Default modules for comprehensive quote summary
    DEFAULT_MODULES = [
        ASSET_PROFILE,
        SEC_FILINGS,
        CALENDAR_EVENTS,
        PRICE,
        SUMMARY_DETAIL,
        PAGE_VIEWS,
        FINANCIALS_TEMPLATE,
        QUOTE_UNADJUSTED_PERFORMANCE_OVERVIEW
    ]

class YfParams:
    QOUTE_FIELDS = QouteFields
    QUOTE_SUMMARY_MODULES = QuoteSummaryModules