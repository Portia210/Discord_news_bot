"""
Message Utilities for Discord
"""

import discord
from utils.logger import logger
from config import Config


def split_long_message(message: str, max_length: int = 1900) -> list:
    """
    Split a long message into chunks that fit within Discord's limits
    
    Args:
        message: The message to split
        max_length: Maximum length per chunk (default 1900 to leave room for formatting)
    
    Returns:
        List of message chunks
    """
    if len(message) <= max_length:
        return [message]
    
    chunks = []
    current_chunk = ""
    
    # Split by lines to avoid breaking in the middle of content
    lines = message.split('\n')
    
    for line in lines:
        # If adding this line would exceed the limit, start a new chunk
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                # Single line is too long, split it
                while len(line) > max_length:
                    chunks.append(line[:max_length])
                    line = line[max_length:]
                current_chunk = line
        else:
            current_chunk += '\n' + line if current_chunk else line
    
    # Add the last chunk if it has content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


async def send_message(bot: discord.Client, channel_id: int, message: str, color: int = 0x00ff00, title: str = "📅 Alert", error_context: str = "send_message"):
    """
    Send a message to a specific channel with splitting support
    
    Args:
        bot: Discord bot instance
        channel_id: Target channel ID
        message: Message content
        color: Embed color (hex)
        title: Embed title
        error_context: Context for error logging
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            logger.error(f"❌ Could not find channel with ID: {channel_id} in {error_context}")
            return False
        
        # Split message if it's too long
        message_chunks = split_long_message(message)
        
        for i, chunk in enumerate(message_chunks):
            # Create embed
            embed = discord.Embed(
                title=title,
                description=chunk,
                color=color
            )
            
            # Add footer for split messages
            if len(message_chunks) > 1:
                embed.set_footer(text=f"Part {i+1} of {len(message_chunks)}")
            
            await channel.send(embed=embed)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending message to channel {channel_id} in {error_context}: {e}")
        return False


async def send_dev_alert(bot: discord.Client, message: str, color: int = 0x00ff00, title: str = "🔧 Dev Alert"):
    """
    Send a message to the dev channel
    
    Args:
        bot: Discord bot instance
        message: Message content
        color: Embed color (hex)
        title: Embed title
    
    Returns:
        bool: True if successful, False otherwise
    """
    dev_channel_id = Config.CHANNEL_IDS.DEV
    return await send_message(bot, dev_channel_id, message, color, title, "send_dev_alert")


async def send_alert(bot: discord.Client, message: str, color: int = 0x00ff00, title: str = "📅 Alert"):
    """
    Send a message to the alert channel
    
    Args:
        bot: Discord bot instance
        message: Message content
        color: Embed color (hex)
        title: Embed title
    
    Returns:
        bool: True if successful, False otherwise
    """
    alert_channel_id = Config.CHANNEL_IDS.PYTHON_BOT
    return await send_message(bot, alert_channel_id, message, color, title, "send_alert") 