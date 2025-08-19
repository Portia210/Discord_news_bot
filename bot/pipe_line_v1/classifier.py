"""
Classifier module for the news processing pipeline.
Handles optional OpenAI-based impact scoring for borderline cases.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from .config import Config
from utils import logger

class ImpactClassifier:
    def __init__(self, impact_threshold: float = 0.25, chunk_size: int = 20):
        self.impact_threshold = impact_threshold
        self.chunk_size = chunk_size
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL, 
            openai_api_key=Config.OPENAI_API_KEY, 
            temperature=0.1
        )
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )
        self.scoring_template = ChatPromptTemplate.from_template(
            """Rate how the volatilty that this article could cause to the stock market:
            Article: {article_text}
            Respond with a float number between 0-1:"""
        )
        
        # Predefined volatility vectors - event-driven market volatility (adjusted based on LLM alignment)
        self.volatility_vectors = [
            # Fed/Policy Events (reduced weight - was too strong)
            "fed rate cut announcement powell speech jackson hole federal reserve decision interest rates",
            
            # Market Crash Events (keep strong - matches LLM well)
            "stock market crash flash crash circuit breaker triggered market halt bear market",
            
            # Earnings Surprises (keep strong - matches LLM well)
            "earnings beat miss expectations revenue surprise profit loss announcement s&p 500 earnings",
            
            # Major Company Events (strengthened - Tesla, Apple, etc.)
            "tesla stock split apple earnings microsoft revenue google profit amazon sales company announcement",
            
            # Financial Crisis Events (keep moderate)
            "bank failure financial crisis credit default swap collapse investment banks",
            
            # Political/Policy Events (reduced weight - was too strong)
            "executive order signed presidential announcement policy change regulation government decision",
            
            # Economic Data Surprises (keep moderate)
            "inflation report unemployment data GDP announcement economic surprise consumer price index",
            
            # Tech/AI Breakthrough Events (strengthened - was too weak)
            "AI breakthrough artificial intelligence announcement tech innovation machine learning technology gains",
            
            # Crypto Market Events (strengthened - was too weak)
            "bitcoin crash rally cryptocurrency announcement digital currency blockchain microstrategy crypto",
            
            # Merger/Acquisition Events (keep moderate)
            "merger acquisition takeover bid hostile buyout corporate deal business combination"
        ]
        self._cache_volatility_embeddings()

    def _cache_volatility_embeddings(self):
        """Cache the embeddings for volatility vectors"""
        try:
            self.volatility_embeddings = self.embeddings.embed_documents(self.volatility_vectors)
            logger.info("Cached volatility vector embeddings")
        except Exception as e:
            logger.error(f"Failed to cache volatility embeddings: {e}")
            self.volatility_embeddings = []

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0

    def similarity_boost(self, similarities: List[float], threshold: float = 0.25, alpha: float = 0.5) -> float:
        """Calculate boost based on similarities above threshold"""
        boost = sum(max(0, sim - threshold) for sim in similarities)
        return 1 + alpha * boost

    def calculate_vector_similarity(self, article: Dict[str, Any]) -> float:
        """Calculate similarity between article embedding and volatility vectors"""
        article_embedding = article.get('embedding')
        if not article_embedding or not self.volatility_embeddings:
            return 0.0
        
        # Calculate similarity with each volatility vector
        similarities = []
        for vol_embedding in self.volatility_embeddings:
            similarity = self.cosine_similarity(article_embedding, vol_embedding)
            similarities.append(similarity)
        
        # Find the maximum similarity
        max_similarity = max(similarities) if similarities else 0.0
        
        # Apply boost based on similarities above threshold
        boost_factor = self.similarity_boost(similarities, threshold=0.25, alpha=0.5)
        final_similarity = min(1.0, max_similarity * boost_factor)
        
        # Store debugging info
        article['vector_similarity'] = final_similarity
        article['max_similarity'] = max_similarity
        article['boost_factor'] = boost_factor
        article['all_similarities'] = similarities
        
        return final_similarity

    def score_article_impact(self, article: Dict[str, Any]) -> float:
        try:
            article_text = article.get('full_text', article.get('headline', ''))
            response = self.llm.invoke(self.scoring_template.format(article_text=article_text))
            score = float(response.content.strip())
            return score
        except Exception as e:
            logger.warning(f"Failed to score article: {e}")
            return 0.0

    def classify_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Starting classification of {len(articles)} articles")
        
        # Step 1: Calculate vector similarity for all articles
        for article in articles:
            similarity = self.calculate_vector_similarity(article)
            logger.debug(f"Article: {article.get('headline', '')[:50]}... -> Vector similarity: {similarity:.4f}")
        
        # Step 2: Filter articles above threshold
        high_impact_articles = [
            article for article in articles 
            if article.get('vector_similarity', 0) >= self.impact_threshold
        ]
        logger.info(f"Found {len(high_impact_articles)} articles above threshold {self.impact_threshold}")
        
        # Step 3: Process in chunks for LLM scoring
        for i in range(0, len(high_impact_articles), self.chunk_size):
            chunk = high_impact_articles[i:i + self.chunk_size]
            logger.info(f"Processing chunk {i//self.chunk_size + 1} with {len(chunk)} articles")
            
            for article in chunk:
                rating = self.score_article_impact(article)
                article['llm_rating'] = rating
        
        # Step 4: Add default ratings for low-impact articles
        for article in articles:
            if 'llm_rating' not in article:
                article['llm_rating'] = 0.0
        
        logger.info("Classification completed")
        return articles

    def filter_by_impact_score(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            article for article in articles 
            if article.get('impact_score', 0) >= Config.IMPACT_SCORE_THRESHOLD
        ]
