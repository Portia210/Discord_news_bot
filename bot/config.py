import os
from dotenv import load_dotenv
import discord

# Load environment variables from .env file
load_dotenv(override=True)

REMOTE_SERVER = True if os.getenv("REMOTE_SERVER") == "true" else False
ENABLE_PROXY = True if os.getenv("ENABLE_PROXY") == "true" else False


class NotificationRole:
    """Represents a notification role with all its properties"""
    def __init__(self, name: str, emoji: str, color: discord.Color):
        self.name = name
        self.emoji = emoji  # Emoji for the role (e.g., "📰")
        self.color = color  # Discord color for the role
        self.full_name = f"{emoji} {name}"  # Full role name with emoji
        self.key = name.lower().replace(" ", "_")  # Auto-generated key for backward compatibility

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

class NotificationRoles():
    """All notification roles - add/remove roles here only"""
    
    ECONOMIC_CALENDAR = NotificationRole("Economic Calendar", "📈", discord.Color.dark_grey())
    LIVE_NEWS = NotificationRole("Live News", "📰", discord.Color.red())
    NEWS_REPORT = NotificationRole("News Report", "📊", discord.Color.blue())
    ALL_ROLES = [ECONOMIC_CALENDAR, LIVE_NEWS, NEWS_REPORT]
    
    # Helper methods for easy access
    @classmethod
    def get_by_name(cls, name: str):
        """Get notification role by name (case-insensitive)"""
        name_lower = name.lower()
        return next((role for role in cls.ALL_ROLES if role.name.lower() == name_lower), None)
    
    @classmethod
    def get_by_full_name(cls, full_name: str):
        """Get notification role by full name (with emoji)"""
        return next((role for role in cls.ALL_ROLES if role.full_name == full_name), None)
    
    @classmethod
    def get_names(cls):
        """Get all role names"""
        return [role.name for role in cls.ALL_ROLES]
    
    @classmethod
    def get_full_names(cls):
        """Get all role full names (with emojis)"""
        return [role.full_name for role in cls.ALL_ROLES]
    
    @classmethod
    def get_keys(cls):
        """Get all role keys (for backward compatibility)"""
        return [role.key for role in cls.ALL_ROLES]

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

class Language():
    # Language configuration for the bot
    # Options: "en" (English only), "he" (Hebrew only), "bilingual" (both languages)
    BOT_LANGUAGE = "en"  # Change this to "he" for Hebrew or "bilingual" for both
    
    # You can also set this per user if needed
    USER_LANGUAGES = {
        # "user_id": "he",  # Example: specific user gets Hebrew
        # "another_user_id": "bilingual"  # Example: specific user gets both languages
    }

class Config:
    CHANNEL_IDS = ChannelIds
    USER_IDS = UserIds
    PROXY = Proxy
    TIMEZONES = Timezones
    TOKENS = Tokens
    SERVER = Server
    LANGUAGE = Language
    NOTIFICATION_ROLES = NotificationRoles
