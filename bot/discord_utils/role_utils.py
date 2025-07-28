"""
Role utility functions for Discord bot
"""

import discord
from utils.logger import logger


async def get_role_mention(bot, role_name: str) -> str:
    """Get role mention string for a given role name"""
    try:
        if not bot:
            return ""
        
        # Get the first guild (assuming single server setup)
        guild = bot.guilds[0] if bot.guilds else None
        if not guild:
            return ""
        
        # Find the role by name
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            return role.mention
        else:
            logger.warning(f"⚠️ Role '{role_name}' not found in guild")
            return ""
            
    except Exception as e:
        logger.error(f"❌ Error getting role mention for '{role_name}': {e}")
        return "" 