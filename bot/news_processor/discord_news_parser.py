"""
Discord news data parser for extracting structured data from Discord messages.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils.logger import logger


def parse_discord_messages(messages_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse Discord messages into flat article dictionaries.
    
    Args:
        messages_list: List of Discord message dictionaries
        
    Returns:
        List of flat article dictionaries with extracted fields
    """
    articles = []
    for message in messages_list:
        article = parse_single_message(message)
        if article:
            articles.append(article)
    
    logger.debug(f"Parsed {len(articles)} articles from {len(messages_list)} messages")
    return articles


def parse_single_message(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse a single Discord message into a flat article dictionary.
    
    Args:
        message: Discord message dictionary
        
    Returns:
        Flat article dictionary or None if parsing fails
    """
    try:
        content = message.get('content', '')
        
        # Extract data using regex
        pattern = r'Tweeter news account: (\w+)\s+(.*?)\s+—\s+\*([^*]+)\s+\(@\w+\)\s+(\w+\s+\d+,\s+\d+)\s+Link to tweet:\s+(https://[^\s]+)\s+Tweeted at:\s+(.+)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return None
        
        # Extract fields
        headline = match.group(2).strip()
        link = match.group(5)
        tweeter_timestamp = match.group(6).strip()
        
        # Create flat dictionary
        article = {
            'discord_timestamp': message.get('timestamp'),
            'author': message.get('author'),
            'tweeter_timestamp': tweeter_timestamp,
            'raw_message': content,
            'headline': headline,
            'link': link
        }
        
        return article
        
    except Exception as e:
        logger.error(f"Error parsing message: {e}")
        return None


if __name__ == "__main__":
    from utils import read_json_file, write_json_file
    messages = read_json_file("messages_example.json")
    articles = parse_discord_messages(messages)
    write_json_file("articles.json", articles)