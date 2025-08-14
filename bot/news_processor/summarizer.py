"""
Summarization service using OpenAI to generate cluster summaries.
"""

import os
import openai
from typing import List, Optional
from .models import NewsCluster
import logging

logger = logging.getLogger(__name__)


class Summarizer:
    """Service for generating summaries using OpenAI."""
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the summarizer.
        
        Args:
            model_name: Name of the OpenAI model to use
        """
        self.model_name = model_name
        self.client = None
        
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info(f"Using OpenAI model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        else:
            logger.error("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY is required")
    
    def summarize_clusters(self, clusters: List[NewsCluster]) -> List[NewsCluster]:
        """
        Generate summaries for all clusters.
        
        Args:
            clusters: List of clusters to summarize
            
        Returns:
            List of clusters with summaries
        """
        for cluster in clusters:
            if cluster.cluster_size > 1:  # Only summarize multi-article clusters
                try:
                    summary, tags, importance = self._summarize_cluster(cluster)
                    cluster.summary = summary
                    cluster.tags = tags
                    cluster.importance_score = importance
                except Exception as e:
                    logger.error(f"Error summarizing cluster: {e}")
                    # Fallback to simple summary
                    cluster.summary = self._create_fallback_summary(cluster)
        
        return clusters
    
    def _summarize_cluster(self, cluster: NewsCluster) -> tuple[str, List[str], float]:
        """
        Generate summary, tags, and importance for a cluster.
        
        Args:
            cluster: Cluster to summarize
            
        Returns:
            Tuple of (summary, tags, importance_score)
        """
        prompt = self._create_summary_prompt(cluster)
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional news analyst. Create concise, accurate summaries of news clusters."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the response
        try:
            summary, tags, importance = self._parse_summary_response(result)
            return summary, tags, importance
        except Exception as e:
            logger.error(f"Error parsing summary response: {e}")
            return self._create_fallback_summary(cluster), cluster.tags or [], cluster.importance_score
    
    def _create_summary_prompt(self, cluster: NewsCluster) -> str:
        """Create prompt for summarizing a cluster."""
        headlines = [article.headline for article in cluster.articles]
        content = cluster.merged_content[:2000]  # Limit content length
        
        prompt = f"""
Please analyze the following news cluster and provide:

1. A concise summary (2-3 sentences) that captures the main story
2. 3-5 relevant tags/keywords
3. An importance score (0.0 to 1.0) based on:
   - Market impact
   - Geopolitical significance
   - Economic implications
   - Public interest

Headlines:
{chr(10).join(f"- {headline}" for headline in headlines)}

Content:
{content}

Please respond in this exact format:
SUMMARY: [your summary here]
TAGS: [tag1, tag2, tag3, tag4, tag5]
IMPORTANCE: [score between 0.0 and 1.0]
"""
        return prompt
    
    def _parse_summary_response(self, response: str) -> tuple[str, List[str], float]:
        """Parse the summary response from OpenAI."""
        lines = response.split('\n')
        summary = ""
        tags = []
        importance = 0.0
        
        for line in lines:
            line = line.strip()
            if line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("TAGS:"):
                tags_str = line.replace("TAGS:", "").strip()
                tags = [tag.strip() for tag in tags_str.strip('[]').split(',')]
            elif line.startswith("IMPORTANCE:"):
                importance_str = line.replace("IMPORTANCE:", "").strip()
                try:
                    importance = float(importance_str)
                except ValueError:
                    importance = 0.5
        
        return summary, tags, importance
    
    def _create_fallback_summary(self, cluster: NewsCluster) -> str:
        """Create a simple fallback summary when AI summarization fails."""
        if cluster.cluster_size == 1:
            return cluster.articles[0].headline
        
        # Use the most important article's headline
        best_article = max(cluster.articles, key=lambda a: a.importance_score or 0)
        return f"Multiple articles about: {best_article.headline}"
