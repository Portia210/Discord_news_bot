"""
Embedding service for generating article embeddings.
"""

import os
import numpy as np
from typing import List, Optional
import openai
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from text."""
    
    def __init__(self, model_name: str = "text-embedding-3-small"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name
        self.openai_client = None
        self.local_model = None
        
        # Try to use OpenAI first, fallback to local model
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info(f"Using OpenAI embedding model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if not self.openai_client:
            # Fallback to local model
            try:
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Using local embedding model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.error(f"Failed to initialize local embedding model: {e}")
                raise
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for given text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if failed
        """
        if not text or not text.strip():
            return None
            
        try:
            if self.openai_client:
                return self._get_openai_embedding(text)
            elif self.local_model:
                return self._get_local_embedding(text)
            else:
                logger.error("No embedding model available")
                return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def _get_openai_embedding(self, text: str) -> List[float]:
        """Get embedding using OpenAI API."""
        response = self.openai_client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    def _get_local_embedding(self, text: str) -> List[float]:
        """Get embedding using local model."""
        embedding = self.local_model.encode(text)
        return embedding.tolist()
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score
        """
        if not embedding1 or not embedding2:
            return 0.0
            
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
