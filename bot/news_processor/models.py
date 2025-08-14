"""
Data models for news processing.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class NewsArticle:
    """Represents a news article."""
    id: str
    headline: str
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    importance_score: Optional[float] = None
    source: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    embedding: Optional[List[float]] = None


@dataclass
class NewsCluster:
    """Represents a cluster of news articles."""
    id: Optional[int] = None
    summary: str = ""
    tags: Optional[List[str]] = None
    importance_score: float = 0.0
    merged_content: str = ""
    cluster_size: int = 0
    articles: Optional[List[NewsArticle]] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.articles is None:
            self.articles = []
        if self.tags is None:
            self.tags = []


@dataclass
class NewsDigest:
    """Represents a news digest with top clusters."""
    clusters: List[NewsCluster]
    total_articles: int
    generated_at: datetime
    digest_id: str
