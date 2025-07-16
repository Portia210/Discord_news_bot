import os
from enum import StrEnum, IntEnum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Tokens(StrEnum):
    DISCORD = os.getenv("DISCORD_TOKEN")
    OPENAI = os.getenv("OPENAI_API_KEY")

class ChannelIds(IntEnum):
    TWEETER_NEWS = 1328615279697330227
    TWEETER_TRADE_ALERTS = 1229499082884518016
    INVESTING_BOT = 1389349923962491061
    PYTHON_BOT = 1389360754200936538
    DEV = 1394602221206769734

class UserIds(IntEnum):
    IFITT_BOT = 832731781231804447
    PYTHON_BOT = 1358545327551942887
    ADMIN = 949994517774364682

class Proxy(StrEnum):
    HOST = os.getenv("PROXY_HOST", "brd.superproxy.io")
    PORT = os.getenv("PROXY_PORT", "33335")
    CUSTOMER_ID = os.getenv("PROXY_CUSTOMER_ID", "hl_9884942f")
    ZONE = os.getenv("PROXY_ZONE", "isp_proxy1")
    PASSWORD = os.getenv("PROXY_PASSWORD", "ky8psv0nqmev")

class Timezones(StrEnum):
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL

class Config:
    CHANNEL_IDS = ChannelIds
    USER_IDS = UserIds
    PROXY = Proxy
    TIMEZONES = Timezones
    TOKENS = Tokens

