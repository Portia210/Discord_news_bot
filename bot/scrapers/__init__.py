"""
Scrapers Package - Centralized access to all scraping functionality
"""

# Investing Scraper
from .investing.investing_scraper import InvestingScraper
from .investing.economic_calendar_to_text import economic_calendar_to_text
from .investing.investing_params import InvestingParams

# Yahoo Finance Scraper
from .yf.yf_scraper import YfScraper
from .yf.yf_params import QouteFields

# Symbols List Scraper
from .sybmols_list import get_symbols_list

# CNBC Scraper
from .cnbc.cnbc_scraper import (
    get_cnbc_world_assets,
    get_article_body,
    extract_s_data_dict_from_html,
    get_all_modules,
    get_clean_assets
)

# Reuters Scraper
from .company_info import (
    get_company_info,
    get_info_async,
    get_companies_info
)


# Main classes and functions to expose
__all__ = [
    # Investing
    'InvestingScraper',
    'economic_calendar_to_text',
    'InvestingParams',
    
    # Yahoo Finance
    'YfScraper',
    'QouteFields',
    
    # CNBC
    'get_cnbc_world_assets',
    'get_article_body',
    'extract_s_data_dict_from_html',
    'get_all_modules',
    'get_clean_assets',
    
    # Reuters
    'get_company_info',
    'get_info_async',
    'get_companies_info',
]

