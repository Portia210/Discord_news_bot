import os
from dotenv import load_dotenv
from config_ext import NotificationRoles, Tokens, ChannelIds, UserIds, Language, Schedule, Colors

# Load environment variables from .env file
load_dotenv(override=True)

REMOTE_SERVER = True if os.getenv("REMOTE_SERVER") == "true" else False
ENABLE_PROXY = True if os.getenv("ENABLE_PROXY") == "true" else False




class Proxy():
    HOST = os.getenv("PROXY_HOST", "brd.superproxy.io")
    PORT = os.getenv("PROXY_PORT", "33335")
    CUSTOMER_ID = os.getenv("PROXY_CUSTOMER_ID", "hl_9884942f")
    ZONE = os.getenv("PROXY_ZONE", "isp_proxy1")
    PASSWORD = os.getenv("PROXY_PASSWORD", "ky8psv0nqmev")
    FULL_PROXY = f"http://brd-customer-{CUSTOMER_ID}-zone-{ZONE}:{PASSWORD}@{HOST}:{PORT}"
    APP_PROXY = FULL_PROXY if ENABLE_PROXY else None

class Timezones():
    EASTERN_US = "America/New_York"
    ISRAEL = "Asia/Jerusalem"
    APP_TIMEZONE = ISRAEL


class Server():
    LOCAL_SERVER_IP = "127.0.0.1"
    PUBLIC_SERVER_IP = "54.165.14.238"
    CURRENT_SERVER_IP = PUBLIC_SERVER_IP if REMOTE_SERVER else LOCAL_SERVER_IP
    API_TOKEN = os.getenv("SERVER_API_TOKEN")
    PORT = 8000


class Config:
    CHANNEL_IDS = ChannelIds
    USER_IDS = UserIds
    PROXY = Proxy
    TIMEZONES = Timezones
    TOKENS = Tokens
    SERVER = Server
    LANGUAGE = Language
    NOTIFICATION_ROLES = NotificationRoles
    SCHEDULE = Schedule
    COLORS = Colors