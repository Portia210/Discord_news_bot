"""
Embeddings module for the news processing pipeline.
Handles OpenAI embeddings and similarity calculations.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from .config import Config

class EmbeddingManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL, 
            openai_api_key=Config.OPENAI_API_KEY
        )

    def embed_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        texts = [article.get('headline', '') for article in articles]
        embeddings_list = self.embeddings.embed_documents(texts)
        
        for article, embedding in zip(articles, embeddings_list):
            article['embedding'] = embedding
        
        return articles
