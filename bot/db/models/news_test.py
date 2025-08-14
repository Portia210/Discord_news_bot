"""
Test model for news processor database integration.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.sql import func

from ..engine import Base


class NewsTest(Base):
    """Test model for news processing pipeline."""
    __tablename__ = "news_test"
    
    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(200), nullable=False)
    test_data = Column(Text, nullable=True)
    test_config = Column(JSON, nullable=True)  # Store test configuration as JSON
    success = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    articles_processed = Column(Integer, default=0)
    clusters_created = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NewsProcessingLog(Base):
    """Log model for tracking news processing runs."""
    __tablename__ = "news_processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # 'started', 'completed', 'failed'
    step = Column(String(100), nullable=True)  # Current processing step
    articles_count = Column(Integer, default=0)
    clusters_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    config_used = Column(JSON, nullable=True)  # Configuration used for this run
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
