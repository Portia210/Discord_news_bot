import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

APP_IS_REMOTE = True if os.getenv("APP_IS_REMOTE") == "true" else False

class Tokens():
    DISCORD = os.getenv("DISCORD_TOKEN")
    OPENAI = os.getenv("OPENAI_API_KEY")

class ChannelIds():
    TWEETER_NEWS = 1328615279697330227
    TWEETER_TRADE_ALERTS = 1229499082884518016
    INVESTING_BOT = 1389349923962491061
    PYTHON_BOT = 1389360754200936538
    DEV = 1394602221206769734

class UserIds():
    IFITT_BOT = 832731781231804447
    PYTHON_BOT = 1358545327551942887
    ADMIN = 949994517774364682

class Proxy():
    HOST = os.getenv("PROXY_HOST", "brd.superproxy.io")
    PORT = os.getenv("PROXY_PORT", "33335")
    CUSTOMER_ID = os.getenv("PROXY_CUSTOMER_ID", "hl_9884942f")
    ZONE = os.getenv("PROXY_ZONE", "isp_proxy1")
    PASSWORD = os.getenv("PROXY_PASSWORD", "ky8psv0nqmev")
    FULL_PROXY = f"http://brd-customer-{CUSTOMER_ID}-zone-{ZONE}:{PASSWORD}@{HOST}:{PORT}"
    APP_PROXY = FULL_PROXY if APP_IS_REMOTE else None

class Timezones():
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL


class Server():
    LOCAL_SERVER_IP = "127.0.0.1"
    PUBLIC_SERVER_IP = "54.165.14.238"
    CURRENT_SERVER_IP = PUBLIC_SERVER_IP if APP_IS_REMOTE else LOCAL_SERVER_IP
    API_TOKEN = os.getenv("SERVER_API_TOKEN")
    PORT = 8000

class Config:
    CHANNEL_IDS = ChannelIds
    USER_IDS = UserIds
    PROXY = Proxy
    TIMEZONES = Timezones
    TOKENS = Tokens
    SERVER = Server
