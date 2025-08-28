"""
Classifier module for the news processing pipeline.
Handles centroid-based impact scoring using embeddings.
"""

import numpy as np
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from .config import Config
from utils import logger

class ImpactClassifier:
    def __init__(self, impact_threshold: float = 0.15, chunk_size: int = 20):
        self.impact_threshold = impact_threshold
        self.chunk_size = chunk_size
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )
        
        self.economic_vectors = [
            "stock market crash market crash financial crisis economic collapse bear market",
            "federal reserve rate cuts fed rate cuts powell jackson hole monetary policy interest rates",
            "earnings report quarterly earnings s&p 500 earnings corporate results financial performance",
            "market volatility trading volume price movement stock fluctuations market correction",
            "economic data inflation unemployment GDP economic indicators consumer price index",
            "artificial intelligence AI technology gains market impact tech sector performance",
            "cryptocurrency bitcoin digital assets crypto market blockchain technology",
            "presidential schedule executive orders political impact market influence",
            "goldman sachs morgan stanley investment banks financial institutions",
            "market expectations analyst predictions forecast market outlook"
        ]
        
        self.positive_vectors = [
            "earnings beat revenue growth profit increase positive results strong performance",
            "market rally stock gains bullish trend positive outlook optimistic forecast",
            "economic growth GDP increase employment rise positive economic data",
            "innovation breakthrough technological advancement positive development",
            "merger acquisition successful deal positive business combination",
            "rate cut stimulus positive monetary policy economic support",
            "positive earnings surprise strong quarterly results beat expectations",
            "market recovery bounce back positive market movement",
            "positive analyst rating upgrade strong recommendation buy rating",
            "positive economic indicators strong consumer confidence positive data"
        ]
        
        self.negative_vectors = [
            "earnings miss revenue decline profit loss negative results poor performance",
            "market crash stock losses bearish trend negative outlook pessimistic forecast",
            "economic recession GDP decline employment drop negative economic data",
            "financial crisis bank failure credit default negative financial event",
            "layoffs job cuts negative employment news company restructuring",
            "rate hike inflation pressure negative monetary policy economic stress",
            "negative earnings surprise weak quarterly results miss expectations",
            "market correction selloff negative market movement",
            "negative analyst rating downgrade weak recommendation sell rating",
            "negative economic indicators weak consumer confidence negative data"
        ]
        
        self.neutral_vectors = [
            "company announcement corporate news business update general information",
            "market update trading session regular market activity daily movement",
            "economic report data release statistical information factual update",
            "regulatory filing official document compliance update administrative news",
            "product launch new offering service introduction business development",
            "executive appointment management change organizational update",
            "quarterly report financial disclosure routine reporting period update",
            "market analysis research report analytical perspective market commentary",
            "industry news sector update business environment general information",
            "policy announcement government update regulatory change administrative decision"
        ]
        
        self._cache_embeddings()

    def _cache_embeddings(self):
        """Cache embeddings for all vector categories"""
        try:
            self.economic_embeddings = self.embeddings.embed_documents(self.economic_vectors)
            self.positive_embeddings = self.embeddings.embed_documents(self.positive_vectors)
            self.negative_embeddings = self.embeddings.embed_documents(self.negative_vectors)
            self.neutral_embeddings = self.embeddings.embed_documents(self.neutral_vectors)
            logger.info("Cached all centroid embeddings")
        except Exception as e:
            logger.error(f"Failed to cache centroid embeddings: {e}")
            self.economic_embeddings = []
            self.positive_embeddings = []
            self.negative_embeddings = []
            self.neutral_embeddings = []

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    def calculate_centroid_similarity(self, article_embedding: List[float], centroid_embeddings: List[List[float]]) -> float:
        """Calculate similarity to a centroid"""
        if not centroid_embeddings:
            return 0.0
        
        similarities = [self.cosine_similarity(article_embedding, cent_emb) for cent_emb in centroid_embeddings]
        return sum(similarities) / len(similarities)

    def calculate_vector_similarity(self, article: Dict[str, Any]) -> float:
        """Calculate economic relevance similarity"""
        article_embedding = article.get('embedding')
        if not article_embedding or not self.economic_embeddings:
            return 0.0
        
        economic_similarity = self.calculate_centroid_similarity(article_embedding, self.economic_embeddings)
        article['vector_similarity'] = economic_similarity
        return economic_similarity

    def score_article_impact(self, article: Dict[str, Any]) -> float:
        """Score article impact using centroid-based approach"""
        try:
            article_embedding = article.get('embedding')
            if not article_embedding:
                return 0.0
            
            economic_similarity = self.calculate_centroid_similarity(article_embedding, self.economic_embeddings)
            if economic_similarity < self.impact_threshold:
                return 0.0
            
            positive_similarity = self.calculate_centroid_similarity(article_embedding, self.positive_embeddings)
            negative_similarity = self.calculate_centroid_similarity(article_embedding, self.negative_embeddings)
            neutral_similarity = self.calculate_centroid_similarity(article_embedding, self.neutral_embeddings)
            
            max_sentiment = max(positive_similarity, negative_similarity, neutral_similarity)
            if max_sentiment == neutral_similarity:
                return 0.0
            
            if positive_similarity > negative_similarity:
                sentiment_score = positive_similarity
                if positive_similarity > 0.4:
                    sentiment_score *= 1.3
            else:
                sentiment_score = negative_similarity
                if negative_similarity > 0.4:
                    sentiment_score *= 1.5
            
            final_score = (economic_similarity * 0.6) + (sentiment_score * 0.4)
            
            if economic_similarity > 0.5:
                final_score *= 1.2
            
            article['economic_similarity'] = economic_similarity
            article['positive_similarity'] = positive_similarity
            article['negative_similarity'] = negative_similarity
            article['neutral_similarity'] = neutral_similarity
            article['sentiment_score'] = sentiment_score
            
            return min(1.0, final_score)
            
        except Exception as e:
            logger.warning(f"Failed to score article: {e}")
            return 0.0

    def classify_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify articles using centroid-based scoring"""
        logger.info(f"Starting classification of {len(articles)} articles")
        
        for article in articles:
            self.calculate_vector_similarity(article)
        
        logger.info(f"Processing {len(articles)} articles with centroid-based scoring")
        
        for i in range(0, len(articles), self.chunk_size):
            chunk = articles[i:i + self.chunk_size]
            logger.info(f"Processing chunk {i//self.chunk_size + 1} with {len(chunk)} articles")
            
            for article in chunk:
                impact_score = self.score_article_impact(article)
                article['llm_rating'] = impact_score
        
        logger.info("Classification completed")
        return articles

    def filter_by_impact_score(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter articles by impact score threshold"""
        return [
            article for article in articles 
            if article.get('impact_score', 0) >= Config.IMPACT_SCORE_THRESHOLD
        ]
