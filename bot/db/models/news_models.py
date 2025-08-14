"""
News models for storing articles and clusters.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..engine import Base


class NewsArticle(Base):
    """Model for storing news articles."""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    headline = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    importance_score = Column(Float, nullable=True)
    source = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    embedding = Column(JSON, nullable=True)  # Store embedding as JSON array
    cluster_id = Column(Integer, ForeignKey("news_clusters.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    cluster = relationship("NewsCluster", back_populates="articles")


class NewsCluster(Base):
    """Model for storing news clusters."""
    __tablename__ = "news_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    summary = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    importance_score = Column(Float, nullable=False)
    merged_content = Column(Text, nullable=True)
    cluster_size = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    articles = relationship("NewsArticle", back_populates="cluster")
