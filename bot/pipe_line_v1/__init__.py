"""
News Processing Pipeline v1.0

A comprehensive news processing pipeline that filters, clusters, and summarizes 
market-impacting news articles using LangChain, OpenAI, and HDBSCAN.

Main components:
- Article loading and preprocessing
- Hybrid impact filtering (embeddings + OpenAI)
- Dynamic clustering with HDBSCAN
- Intelligent labeling with spaCy NER
- Cluster summarization with OpenAI LLM
- Database storage with SQLAlchemy
- LangChain orchestration
"""

from .pipeline import NewsProcessingPipeline, PipelineResult
from .data_loader import ArticleLoader
from .embeddings import EmbeddingManager
from .classifier import ImpactClassifier
from .clustering import ArticleClusterer
from .labeler import ClusterLabeler
from .summarizer import ClusterSummarizer
from .database import DatabaseManager
from .config import Config

__version__ = "1.0.0"
__author__ = "Discord Bot Project"

__all__ = [
    "NewsProcessingPipeline",
    "PipelineResult", 
    "ArticleLoader",
    "EmbeddingManager",
    "ImpactClassifier",
    "ArticleClusterer",
    "ClusterLabeler",
    "ClusterSummarizer",
    "DatabaseManager",
    "Config"
]
