"""
News processing pipeline for clustering and summarizing articles.
"""

from .processor import NewsProcessor
from .models import NewsArticle, NewsCluster

__all__ = ['NewsProcessor', 'NewsArticle', 'NewsCluster']
