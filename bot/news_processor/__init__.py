"""
News processing pipeline for clustering and summarizing news articles.
"""

from .data_loader import DiscordNewsLoader
from .pipeline import NewsProcessorPipeline

__all__ = ['DiscordNewsLoader', 'NewsProcessorPipeline']
