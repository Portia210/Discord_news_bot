"""
Clustering service using HDBSCAN for grouping similar articles.
"""

import numpy as np
from typing import List, Dict, Any
import hdbscan
from sklearn.preprocessing import StandardScaler
from .models import NewsArticle, NewsCluster
import logging

logger = logging.getLogger(__name__)


class ClusteringService:
    """Service for clustering news articles using HDBSCAN."""
    
    def __init__(self, min_cluster_size: int = 2, min_samples: int = 1, cluster_selection_epsilon: float = 0.1):
        """
        Initialize the clustering service.
        
        Args:
            min_cluster_size: Minimum size for a cluster
            min_samples: Minimum number of samples for core points
            cluster_selection_epsilon: Distance threshold for cluster selection
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.cluster_selection_epsilon = cluster_selection_epsilon
    
    def cluster_articles(self, articles: List[NewsArticle]) -> List[NewsCluster]:
        """
        Cluster articles based on their embeddings.
        
        Args:
            articles: List of articles to cluster
            
        Returns:
            List of clusters
        """
        if len(articles) < 2:
            # If only one article, create a single cluster
            if articles:
                cluster = NewsCluster(
                    summary=articles[0].headline,
                    tags=articles[0].tags or [],
                    importance_score=articles[0].importance_score or 0.0,
                    merged_content=self._merge_article_content(articles),
                    cluster_size=1,
                    articles=articles
                )
                return [cluster]
            return []
        
        # Extract embeddings
        embeddings = []
        valid_articles = []
        
        for article in articles:
            if article.embedding:
                embeddings.append(article.embedding)
                valid_articles.append(article)
        
        if not embeddings:
            logger.warning("No valid embeddings found for clustering")
            return []
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Standardize embeddings
        scaler = StandardScaler()
        embeddings_scaled = scaler.fit_transform(embeddings_array)
        
        # Perform clustering
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            cluster_selection_epsilon=self.cluster_selection_epsilon,
            metric='euclidean'
        )
        
        cluster_labels = clusterer.fit_predict(embeddings_scaled)
        
        # Group articles by cluster
        clusters = self._group_articles_by_cluster(valid_articles, cluster_labels)
        
        logger.info(f"Clustered {len(articles)} articles into {len(clusters)} clusters")
        return clusters
    
    def _group_articles_by_cluster(self, articles: List[NewsArticle], cluster_labels: np.ndarray) -> List[NewsCluster]:
        """
        Group articles by their cluster labels.
        
        Args:
            articles: List of articles
            cluster_labels: Cluster labels from HDBSCAN
            
        Returns:
            List of clusters
        """
        # Group articles by cluster label
        cluster_groups = {}
        
        for article, label in zip(articles, cluster_labels):
            if label not in cluster_groups:
                cluster_groups[label] = []
            cluster_groups[label].append(article)
        
        # Create cluster objects
        clusters = []
        
        for label, group_articles in cluster_groups.items():
            if label == -1:
                # Noise points - create individual clusters
                for article in group_articles:
                    cluster = NewsCluster(
                        summary=article.headline,
                        tags=article.tags or [],
                        importance_score=article.importance_score or 0.0,
                        merged_content=article.content or article.summary or "",
                        cluster_size=1,
                        articles=[article]
                    )
                    clusters.append(cluster)
            else:
                # Regular cluster
                cluster = NewsCluster(
                    summary="",  # Will be filled by summarizer
                    tags=self._merge_tags(group_articles),
                    importance_score=self._calculate_cluster_importance(group_articles),
                    merged_content=self._merge_article_content(group_articles),
                    cluster_size=len(group_articles),
                    articles=group_articles
                )
                clusters.append(cluster)
        
        return clusters
    
    def _merge_tags(self, articles: List[NewsArticle]) -> List[str]:
        """Merge tags from all articles in a cluster."""
        all_tags = set()
        for article in articles:
            if article.tags:
                all_tags.update(article.tags)
        return list(all_tags)
    
    def _calculate_cluster_importance(self, articles: List[NewsArticle]) -> float:
        """Calculate importance score for a cluster based on its articles."""
        if not articles:
            return 0.0
        
        # Average importance of articles in cluster
        total_importance = sum(article.importance_score or 0.0 for article in articles)
        avg_importance = total_importance / len(articles)
        
        # Boost importance based on cluster size
        size_boost = min(len(articles) * 0.1, 0.5)  # Max 50% boost
        
        return avg_importance * (1 + size_boost)
    
    def _merge_article_content(self, articles: List[NewsArticle]) -> str:
        """Merge content from all articles in a cluster."""
        content_parts = []
        
        for article in articles:
            if article.content:
                content_parts.append(article.content)
            elif article.summary:
                content_parts.append(article.summary)
            else:
                content_parts.append(article.headline)
        
        return "\n\n".join(content_parts)
