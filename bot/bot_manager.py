"""
Bot Manager - Provides global access to the Discord bot instance
"""

from utils.logger import logger

# Global bot instance
_discord_bot_instance = None

def get_bot():
    """Get the global Discord bot instance"""
    global _discord_bot_instance
    if not _discord_bot_instance:
        logger.error("❌ No Discord bot instance available")
    return _discord_bot_instance

def set_bot(bot):
    """Set the global Discord bot instance"""
    global _discord_bot_instance
    _discord_bot_instance = bot
