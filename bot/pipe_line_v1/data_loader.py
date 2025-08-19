import re
from typing import List, Dict, Any, Optional

class ArticleLoader:
    def __init__(self):
        pass
    
    def load_from_messages(self, messages_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        articles = []
        for message in messages_list:
            article = self._parse_discord_message(message)
            if article:
                articles.append(article)
        return articles
    
    def _parse_discord_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            content = message.get('content', '')
            
            pattern = r'Tweeter news account: (\w+)\s+(.*?)\s+—\s+\*([^*]+)\s+\(@\w+\)\s+(\w+\s+\d+,\s+\d+)\s+Link to tweet:\s+(https://[^\s]+)\s+Tweeted at:\s+(.+)'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                return None
            
            headline = match.group(2).strip()
            link = match.group(5)
            tweeter_timestamp = match.group(6)
            
            article = {
                'discord_timestamp': message.get('timestamp'),
                'author': message.get('author'),
                'tweeter_timestamp': tweeter_timestamp,
                'raw_message': content,
                'headline': headline,
                'link': link
            }
            
            return article
            
        except Exception:
            return None
    
    def _preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text
    
    def load_sample_articles(self) -> List[Dict[str, Any]]:
        sample_articles = [
            {
                "discord_timestamp": "2025-01-15T18:30:00Z",
                "author": "Sample",
                "tweeter_timestamp": "2025-01-15T18:30:00Z",
                "raw_message": "Sample message content",
                "headline": "apple q4 earnings beat expectations",
                "link": "https://example.com/apple-earnings"
            },
            {
                "discord_timestamp": "2025-01-15T19:00:00Z",
                "author": "Sample",
                "tweeter_timestamp": "2025-01-15T19:00:00Z",
                "raw_message": "Sample message content",
                "headline": "federal reserve signals potential rate cut",
                "link": "https://example.com/fed-news"
            }
        ]
        return sample_articles