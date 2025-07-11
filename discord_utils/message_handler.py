import discord
from datetime import datetime, timezone, timedelta
from utils.logger import logger
from config import config
import os

class MessageHandler:
    def __init__(self, bot):
        """
        Initialize MessageHandler with Discord bot instance
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        self._setup_directories()
    
    def _setup_directories(self):
        """Initialize and setup required directories"""
        self.data_dir = os.path.join("data", "messages export")
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def _get_timestamp(self):
        """Get current timestamp in milliseconds"""
        return int(datetime.now(config.app_timezone).timestamp() * 1000)
    
    def _get_user_names(self, user_ids: list) -> list:
        """Get user names from user IDs"""
        if not user_ids:
            return []
        return [self.bot.get_user(user_id).name for user_id in user_ids if self.bot.get_user(user_id)]

    def _format_filename(self, channel_name: str, hours_back: int, user_ids: list = None) -> str:
        """
        Generate filename for export
        
        Args:
            channel_name (str): Name of the channel
            hours_back (int): Number of hours to look back
            user_ids (list): List of user IDs to filter by
        
        Returns:
            str: Formatted filename
        """
        timestamp = self._get_timestamp()
        filename = f"{channel_name}_last_{hours_back}_hours"
        
        if user_ids:
            filename += f"_filtered_{len(user_ids)}users"
        
        filename += f"_{timestamp}.txt"
        return filename
    
    async def read_channel_messages(self, channel_id: int, hours_back: int = 24, user_ids: list = None):
        """
        Read messages from a channel
        
        Args:
            channel_id (int): Discord channel ID
            hours_back (int): Number of hours to look back (default: 24)
            user_ids (list): List of user IDs to filter by (default: None - all users)
        
        Returns:
            tuple: (messages_list, channel_name) or ([], None) if failed
        """
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                logger.error(f"Channel with ID {channel_id} not found")
                return [], None
            
            # Calculate the time threshold
            threshold_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            
            # Read messages
            messages_list = []
            
            async for message in channel.history(limit=None, after=threshold_time):
                # Filter by user if user_ids is provided
                if user_ids and message.author.id not in user_ids:
                    continue
                    
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = message.author.display_name
                content = message.content.replace('\n', ' ').strip()
                
                if content:  # Only include messages with content
                    messages_list.append({
                        'timestamp': timestamp,
                        'author': author,
                        'content': content
                    })
            
            logger.info(f"Read {len(messages_list)} messages from {channel.name}")
            return messages_list, channel.name
            
        except Exception as e:
            logger.error(f"Error reading channel {channel_id}: {e}")
            return [], None

    async def save_messages_to_file(self, messages_list: list, channel_name: str, hours_back: int, user_ids: list = None):
        """
        Save messages to a text file
        
        Args:
            messages_list (list): List of message dictionaries
            channel_name (str): Name of the channel
            hours_back (int): Number of hours looked back
            user_ids (list): List of user IDs that were filtered by
        
        Returns:
            str: Path to the saved file, or None if failed
        """
        try:
            filename = self._format_filename(channel_name, hours_back, user_ids)
            filepath = os.path.join(self.data_dir, filename)
            
            user_names = ", ".join(self._get_user_names(user_ids)) if user_ids else "all users"
            
            # Write messages to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Channel: {channel_name}\n")
                f.write(f"Exported: {datetime.now(config.app_timezone).strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Messages from last {hours_back} hours\n")
                f.write(f"Written by: {user_names}\n")
                f.write("=" * 50 + "\n\n")
                
                for message in messages_list:
                    f.write(f"[{message['timestamp']}] {message['author']}: {message['content']}\n")
            
            logger.info(f"Saved {len(messages_list)} messages to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving messages to file: {e}")
            return None

    async def export_channel_to_text(self, channel_id: int, hours_back: int = 24, user_ids: list = None):
        """
        Read messages from a channel and save to a text file
        
        Args:
            channel_id (int): Discord channel ID
            hours_back (int): Number of hours to look back (default: 24)
            user_ids (list): List of user IDs to filter by (default: None - all users)
        
        Returns:
            str: Path to the saved file, or None if failed
        """
        # Read messages
        messages_list, channel_name = await self.read_channel_messages(channel_id, hours_back, user_ids)
        
        if not channel_name:
            return None
        
        # Save messages to file
        filepath = await self.save_messages_to_file(messages_list, channel_name, hours_back, user_ids)
        
        return filepath

# Global message handler instance
_message_handler = None





def get_message_handler(bot):
    """
    Get or create the global message handler instance
    
    Args:
        bot: Discord bot instance
    
    Returns:
        MessageHandler: Global message handler instance
    """
    global _message_handler
    if _message_handler is None:
        _message_handler = MessageHandler(bot)
    return _message_handler 