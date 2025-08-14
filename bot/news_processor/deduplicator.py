"""
Deduplication service for removing similar articles.
"""

import numpy as np
from typing import List, Tuple
from .models import NewsArticle
from .embedding_service import EmbeddingService
import logging

logger = logging.getLogger(__name__)


class Deduplicator:
    """Service for deduplicating similar news articles."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize the deduplicator.
        
        Args:
            similarity_threshold: Threshold for considering articles similar
        """
        self.similarity_threshold = similarity_threshold
        self.embedding_service = EmbeddingService()
    
    def deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """
        Remove duplicate articles based on similarity.
        
        Args:
            articles: List of articles to deduplicate
            
        Returns:
            List of deduplicated articles
        """
        if len(articles) <= 1:
            return articles
        
        # Generate embeddings for articles that don't have them
        self._ensure_embeddings(articles)
        
        # Find duplicates
        duplicates = self._find_duplicates(articles)
        
        # Remove duplicates, keeping the most important article from each group
        deduplicated = self._remove_duplicates(articles, duplicates)
        
        logger.info(f"Deduplicated {len(articles)} articles to {len(deduplicated)} articles")
        return deduplicated
    
    def _ensure_embeddings(self, articles: List[NewsArticle]) -> None:
        """Ensure all articles have embeddings."""
        texts_to_embed = []
        indices_to_embed = []
        
        for i, article in enumerate(articles):
            if not article.embedding:
                # Use headline + summary for embedding
                text = article.headline
                if article.summary:
                    text += " " + article.summary
                texts_to_embed.append(text)
                indices_to_embed.append(i)
        
        if texts_to_embed:
            embeddings = self.embedding_service.get_embeddings_batch(texts_to_embed)
            for idx, embedding in zip(indices_to_embed, embeddings):
                articles[idx].embedding = embedding
    
    def _find_duplicates(self, articles: List[NewsArticle]) -> List[List[int]]:
        """
        Find groups of duplicate articles.
        
        Returns:
            List of lists, where each inner list contains indices of duplicate articles
        """
        duplicate_groups = []
        processed = set()
        
        for i, article1 in enumerate(articles):
            if i in processed or not article1.embedding:
                continue
                
            current_group = [i]
            processed.add(i)
            
            for j, article2 in enumerate(articles[i+1:], i+1):
                if j in processed or not article2.embedding:
                    continue
                
                similarity = self.embedding_service.cosine_similarity(
                    article1.embedding, article2.embedding
                )
                
                if similarity >= self.similarity_threshold:
                    current_group.append(j)
                    processed.add(j)
            
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
        
        return duplicate_groups
    
    def _remove_duplicates(self, articles: List[NewsArticle], duplicate_groups: List[List[int]]) -> List[NewsArticle]:
        """
        Remove duplicate articles, keeping the most important one from each group.
        
        Args:
            articles: Original list of articles
            duplicate_groups: Groups of duplicate article indices
            
        Returns:
            List of articles with duplicates removed
        """
        to_remove = set()
        
        for group in duplicate_groups:
            # Find the most important article in the group
            best_article_idx = max(group, key=lambda idx: 
                articles[idx].importance_score or 0
            )
            
            # Mark others for removal
            for idx in group:
                if idx != best_article_idx:
                    to_remove.add(idx)
        
        # Return articles not marked for removal
        return [article for i, article in enumerate(articles) if i not in to_remove]
