"""
Main news processor that orchestrates the entire pipeline.
"""

import os
import re
from datetime import datetime
from typing import List, Optional
from .models import NewsArticle, NewsCluster, NewsDigest
from .embedding_service import EmbeddingService
from .deduplicator import Deduplicator
from .clustering import ClusteringService
from .summarizer import Summarizer
import logging

logger = logging.getLogger(__name__)


class NewsProcessor:
    """Main processor for the news pipeline."""
    
    def __init__(self, 
                 embedding_model: str = "text-embedding-3-small",
                 summarization_model: str = "gpt-4o-mini",
                 similarity_threshold: float = 0.85,
                 min_cluster_size: int = 2,
                 top_n_clusters: int = 10):
        """
        Initialize the news processor.
        
        Args:
            embedding_model: OpenAI embedding model to use
            summarization_model: OpenAI model for summarization
            similarity_threshold: Threshold for deduplication
            min_cluster_size: Minimum cluster size for HDBSCAN
            top_n_clusters: Number of top clusters to include in digest
        """
        self.embedding_service = EmbeddingService(embedding_model)
        self.deduplicator = Deduplicator(similarity_threshold)
        self.clustering_service = ClusteringService(min_cluster_size)
        self.summarizer = Summarizer(summarization_model)
        self.top_n_clusters = top_n_clusters
    
    def process_news_text(self, news_text: str) -> NewsDigest:
        """
        Process news text and generate a digest.
        
        Args:
            news_text: Raw news text to process
            
        Returns:
            News digest with top clusters
        """
        logger.info("Starting news processing pipeline")
        
        # Step 1: Parse news text into articles
        articles = self._parse_news_text(news_text)
        logger.info(f"Parsed {len(articles)} articles from text")
        
        if not articles:
            logger.warning("No articles found in news text")
            return NewsDigest([], 0, datetime.now(), "empty")
        
        # Step 2: Generate embeddings
        articles = self._generate_embeddings(articles)
        logger.info(f"Generated embeddings for {len(articles)} articles")
        
        # Step 3: Deduplicate articles
        articles = self.deduplicator.deduplicate_articles(articles)
        logger.info(f"After deduplication: {len(articles)} articles")
        
        # Step 4: Cluster articles
        clusters = self.clustering_service.cluster_articles(articles)
        logger.info(f"Created {len(clusters)} clusters")
        
        # Step 5: Generate summaries
        clusters = self.summarizer.summarize_clusters(clusters)
        logger.info("Generated cluster summaries")
        
        # Step 6: Rank and select top clusters
        top_clusters = self._rank_and_select_clusters(clusters)
        logger.info(f"Selected top {len(top_clusters)} clusters")
        
        # Step 7: Create digest
        digest = NewsDigest(
            clusters=top_clusters,
            total_articles=len(articles),
            generated_at=datetime.now(),
            digest_id=f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        logger.info("News processing pipeline completed")
        return digest
    
    def _parse_news_text(self, news_text: str) -> List[NewsArticle]:
        """
        Parse news text into structured articles.
        
        Args:
            news_text: Raw news text
            
        Returns:
            List of parsed articles
        """
        articles = []
        lines = news_text.strip().split('\n')
        
        current_article = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new article (starts with timestamp)
            timestamp_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
            
            if timestamp_match:
                # Save previous article if exists
                if current_article:
                    articles.append(current_article)
                
                # Start new article
                timestamp_str = timestamp_match.group(1)
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    timestamp = datetime.now()
                
                # Extract headline (everything after the timestamp and source)
                headline = line[line.find(']') + 1:].strip()
                if ':' in headline:
                    headline = headline.split(':', 1)[1].strip()
                
                current_article = NewsArticle(
                    id=f"article_{len(articles)}",
                    headline=headline,
                    timestamp=timestamp,
                    source="IFTTT",
                    importance_score=0.5  # Default importance
                )
            elif current_article:
                # Add content to current article
                if not current_article.content:
                    current_article.content = line
                else:
                    current_article.content += "\n" + line
        
        # Add the last article
        if current_article:
            articles.append(current_article)
        
        return articles
    
    def _generate_embeddings(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Generate embeddings for articles that don't have them.
        
        Args:
            articles: List of articles
            
        Returns:
            Articles with embeddings
        """
        for article in articles:
            if not article.embedding:
                # Use headline + summary for embedding
                text = article.headline
                if article.summary:
                    text += " " + article.summary
                elif article.content:
                    # Use first 200 characters of content
                    text += " " + article.content[:200]
                
                article.embedding = self.embedding_service.get_embedding(text)
        
        return articles
    
    def _rank_and_select_clusters(self, clusters: List[NewsCluster]) -> List[NewsCluster]:
        """
        Rank clusters by importance and select top N.
        
        Args:
            clusters: List of all clusters
            
        Returns:
            Top N clusters sorted by importance
        """
        # Sort by importance score (descending)
        sorted_clusters = sorted(clusters, key=lambda c: c.importance_score, reverse=True)
        
        # Return top N clusters
        return sorted_clusters[:self.top_n_clusters]
    
    def save_to_database(self, digest: NewsDigest, db_session) -> None:
        """
        Save digest to database.
        
        Args:
            digest: News digest to save
            db_session: Database session
        """
        try:
            from ..db.models.news_models import NewsArticle as DBNewsArticle, NewsCluster as DBNewsCluster
            
            # Save clusters first
            for cluster in digest.clusters:
                db_cluster = DBNewsCluster(
                    summary=cluster.summary,
                    tags=cluster.tags,
                    importance_score=cluster.importance_score,
                    merged_content=cluster.merged_content,
                    cluster_size=cluster.cluster_size
                )
                db_session.add(db_cluster)
                db_session.flush()  # Get the cluster ID
                
                # Save articles in this cluster
                for article in cluster.articles:
                    db_article = DBNewsArticle(
                        headline=article.headline,
                        summary=article.summary,
                        content=article.content,
                        tags=article.tags,
                        importance_score=article.importance_score,
                        source=article.source,
                        url=article.url,
                        timestamp=article.timestamp,
                        embedding=article.embedding,
                        cluster_id=db_cluster.id
                    )
                    db_session.add(db_article)
            
            db_session.commit()
            logger.info(f"Saved digest {digest.digest_id} to database")
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error saving to database: {e}")
            raise
