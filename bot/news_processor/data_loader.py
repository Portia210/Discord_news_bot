"""
Discord news data loader for processing news messages from Discord channels.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from discord_utils.message_handler import get_message_handler
from config import Config
from utils.logger import logger


class DiscordNewsLoader:
    """Loads and parses news messages from Discord channels."""
    
    def __init__(self, bot):
        """Initialize the loader with a Discord bot instance."""
        self.bot = bot
        self.message_handler = get_message_handler(bot)
    
    async def load_news_messages(self, hours_back: int = 24, 
                                channel_id: int = Config.CHANNEL_IDS.TWEETER_NEWS,
                                user_ids: List[int] = None) -> List[Dict[str, Any]]:
        """
        Load news messages from Discord channel and parse them into structured articles.
        
        Args:
            hours_back: Number of hours to look back for messages
            channel_id: Discord channel ID to read from
            user_ids: List of user IDs to filter messages from
            
        Returns:
            List of parsed news articles with structured data ready for processing
        """
        if user_ids is None:
            user_ids = [Config.USER_IDS.IFITT_BOT]
        
        try:
            logger.info(f"Loading news messages from Discord (hours_back: {hours_back})")
            
            # Get messages from Discord
            messages_list, _ = await self.message_handler.read_channel_messages(
                channel_id, hours_back, user_ids
            )
            
            if not messages_list:
                logger.warning("No messages found to process")
                return []
            
            logger.debug(f"Retrieved {len(messages_list)} messages from Discord")
            
            # Parse messages into structured articles
            articles = []
            for message in messages_list:
                article = self._parse_message_to_article(message)
                if article:
                    articles.append(article)
            
            logger.debug(f"Successfully loaded and parsed {len(articles)} news articles from {len(messages_list)} messages")
            return articles
            
        except Exception as e:
            logger.error(f"Error loading news messages: {e}")
            return []
    
    def _parse_message_to_article(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a Discord message into a structured news article.
        
        Args:
            message: Discord message dictionary with timestamp, author, content
            
        Returns:
            Parsed article dictionary or None if parsing fails
        """
        try:
            content = message.get('content', '')
            
            # Parse the content using regex patterns
            parsed_data = self._extract_news_data(content)
            if not parsed_data:
                return None
            
            # Create structured article
            article = {
                'headline': parsed_data['headline'],
                'summary': None,  # Will be generated later
                'content': content,
                'tags': None,  # Will be generated later
                'importance_score': None,  # Will be calculated later
                'source': parsed_data['source'],
                'url': parsed_data['url'],
                'timestamp': parsed_data['timestamp'].isoformat(),  # Convert to ISO format
                'embedding': None,  # Will be generated later
                'raw_message': message  # Keep original message for reference
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def _extract_news_data(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from news message content.
        
        Args:
            content: Raw message content string
            
        Returns:
            Dictionary with extracted data or None if parsing fails
        """
        try:
            # Pattern to match the news format
            # Example: "Tweeter news account: DeItaone  HEADLINE    — *Author (@handle)   Date  Link to tweet: URL  Tweeted at: TIMESTAMP"
            pattern = r'Tweeter news account: (\w+)\s+(.*?)\s+—\s+\*([^*]+)\s+\(@\w+\)\s+(\w+\s+\d+,\s+\d+)\s+Link to tweet:\s+(https://[^\s]+)\s+Tweeted at:\s+(.+)'
            
            match = re.search(pattern, content, re.DOTALL)
            if not match:
                logger.debug(f"Could not parse content: {content[:100]}...")
                return None
            
            source = match.group(1)
            headline = match.group(2).strip()
            author = match.group(3).strip()
            date_str = match.group(4)
            url = match.group(5)
            tweet_timestamp = match.group(6).strip()
            
            # Parse timestamp
            try:
                # Parse "August 13, 2025 at 08:28PM" format
                timestamp = datetime.strptime(tweet_timestamp, "%B %d, %Y at %I:%M%p")
            except ValueError:
                # Fallback to message timestamp
                timestamp = datetime.now()
            
            return {
                'headline': headline,
                'source': source,
                'author': author,
                'url': url,
                'timestamp': timestamp,
                'date_str': date_str,
                'tweet_timestamp': tweet_timestamp
            }
            
        except Exception as e:
            logger.error(f"Error extracting news data: {e}")
            return None
    

