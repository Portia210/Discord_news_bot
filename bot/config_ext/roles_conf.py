import discord

class NotificationRole:
    """Represents a notification role with all its properties"""
    def __init__(self, name: str, emoji: str, color: discord.Color):
        self.name = name
        self.emoji = emoji  # Emoji for the role (e.g., "📰")
        self.color = color  # Discord color for the role
        self.full_name = f"{emoji} {name}"  # Full role name with emoji
        self.key = name.lower().replace(" ", "_")  # Auto-generated key for backward compatibility

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