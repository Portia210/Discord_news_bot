"""
Clustering module for the news processing pipeline.
Handles dynamic topic clustering using HDBSCAN.
"""

import numpy as np
from typing import List, Dict, Any
import hdbscan
from sklearn.metrics.pairwise import cosine_distances
from .config import Config

class ArticleClusterer:
    def __init__(self, min_cluster_size: int = None):
        self.min_cluster_size = min_cluster_size or Config.MIN_CLUSTER_SIZE
        self.clusterer = None
        self.cluster_labels = None

    def cluster_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cluster articles using HDBSCAN with optimized parameters for topic-specific clustering"""
        if not articles or len(articles) < 2:
            return articles

        embeddings = np.array([article['embedding'] for article in articles])
        
        # Pre-compute cosine distances
        distance_matrix = cosine_distances(embeddings)
        
        # Optimized HDBSCAN parameters for topic-specific clustering
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=2,  # Minimum 2 articles to form a cluster
            min_samples=1,  # More sensitive to local density
            cluster_selection_epsilon=0.15,  # Tighter clusters - requires closer similarity
            metric='precomputed',
            cluster_selection_method='leaf'  # More conservative clustering
        )
        
        self.cluster_labels = self.clusterer.fit_predict(distance_matrix)
        
        for i, article in enumerate(articles):
            article['cluster_id'] = int(self.cluster_labels[i])
            article['cluster_size'] = self._get_cluster_size(self.cluster_labels[i])
            article['cluster_confidence'] = self._get_cluster_confidence(i)
        
        return articles

    def _get_cluster_size(self, cluster_id: int) -> int:
        """Get size of a cluster"""
        if cluster_id == -1:
            return 1
        return int(np.sum(self.cluster_labels == cluster_id))

    def _get_cluster_confidence(self, article_index: int) -> float:
        """Get confidence score for cluster assignment"""
        if self.clusterer is None:
            return 0.0
        
        cluster_id = self.cluster_labels[article_index]
        if cluster_id == -1:
            return 0.0
        
        return 1.0

    def get_cluster_summary(self, articles: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """Generate summary statistics for each cluster"""
        cluster_summary = {}
        
        for article in articles:
            cluster_id = article.get('cluster_id', -1)
            
            if cluster_id not in cluster_summary:
                cluster_summary[cluster_id] = {
                    'size': 0,
                    'avg_impact_score': 0.0,
                    'sources': set(),
                    'timestamps': []
                }
            
            summary = cluster_summary[cluster_id]
            summary['size'] += 1
            
            if 'impact_score' in article:
                summary['avg_impact_score'] += article['impact_score']
            
            if 'source' in article:
                summary['sources'].add(article['source'])
            
            if 'timestamp' in article:
                summary['timestamps'].append(article['timestamp'])
        
        for cluster_id, summary in cluster_summary.items():
            if summary['size'] > 0:
                summary['avg_impact_score'] /= summary['size']
            summary['sources'] = list(summary['sources'])
            summary['earliest_timestamp'] = min(summary['timestamps']) if summary['timestamps'] else None
            summary['latest_timestamp'] = max(summary['timestamps']) if summary['timestamps'] else None
        
        return cluster_summary
    
    def get_noise_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get articles classified as noise (no cluster)"""
        return [article for article in articles if article.get('cluster_id') == -1]
