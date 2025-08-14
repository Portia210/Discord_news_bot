"""
Database test utility for news processor.
"""

import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..db.models.news_test import NewsTest, NewsProcessingLog
from ..db.models.news_models import NewsArticle, NewsCluster
from .processor import NewsProcessor
from ..config import Config
import logging

logger = logging.getLogger(__name__)


class NewsProcessorDBTest:
    """Database test utility for news processor."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the database test utility.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.run_id = str(uuid.uuid4())
    
    def log_processing_start(self, config: Dict[str, Any]) -> None:
        """Log the start of a processing run."""
        log_entry = NewsProcessingLog(
            run_id=self.run_id,
            status='started',
            step='initialization',
            config_used=config,
            created_at=datetime.now()
        )
        self.db_session.add(log_entry)
        self.db_session.commit()
        logger.info(f"Started processing run: {self.run_id}")
    
    def log_processing_step(self, step: str, articles_count: int = 0, clusters_count: int = 0) -> None:
        """Log a processing step."""
        log_entry = NewsProcessingLog(
            run_id=self.run_id,
            status='in_progress',
            step=step,
            articles_count=articles_count,
            clusters_count=clusters_count,
            created_at=datetime.now()
        )
        self.db_session.add(log_entry)
        self.db_session.commit()
        logger.info(f"Processing step: {step} - Articles: {articles_count}, Clusters: {clusters_count}")
    
    def log_processing_complete(self, articles_count: int, clusters_count: int, processing_time: float) -> None:
        """Log the completion of a processing run."""
        log_entry = NewsProcessingLog(
            run_id=self.run_id,
            status='completed',
            step='completed',
            articles_count=articles_count,
            clusters_count=clusters_count,
            processing_time=processing_time,
            completed_at=datetime.now()
        )
        self.db_session.add(log_entry)
        self.db_session.commit()
        logger.info(f"Completed processing run: {self.run_id} - Time: {processing_time:.2f}s")
    
    def log_processing_error(self, error_message: str, step: str = "unknown") -> None:
        """Log a processing error."""
        log_entry = NewsProcessingLog(
            run_id=self.run_id,
            status='failed',
            step=step,
            error_message=error_message,
            completed_at=datetime.now()
        )
        self.db_session.add(log_entry)
        self.db_session.commit()
        logger.error(f"Processing failed: {error_message}")
    
    def create_test_record(self, test_name: str, test_data: str, config: Dict[str, Any]) -> NewsTest:
        """Create a test record."""
        test_record = NewsTest(
            test_name=test_name,
            test_data=test_data,
            test_config=config,
            success=False,
            created_at=datetime.now()
        )
        self.db_session.add(test_record)
        self.db_session.flush()  # Get the ID
        return test_record
    
    def update_test_record(self, test_record: NewsTest, success: bool, 
                          processing_time: float, articles_processed: int, 
                          clusters_created: int, error_message: Optional[str] = None) -> None:
        """Update a test record with results."""
        test_record.success = success
        test_record.processing_time = processing_time
        test_record.articles_processed = articles_processed
        test_record.clusters_created = clusters_created
        test_record.error_message = error_message
        test_record.updated_at = datetime.now()
        self.db_session.commit()
    
    def test_news_processing(self, news_text: str, test_name: str = "default_test") -> Dict[str, Any]:
        """
        Test the news processing pipeline and log results to database.
        
        Args:
            news_text: News text to process
            test_name: Name of the test
            
        Returns:
            Dictionary with test results
        """
        start_time = time.time()
        test_record = None
        
        try:
            # Create test record
            config = {
                'embedding_model': Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
                'summarization_model': Config.NEWS_PROCESSOR.SUMMARIZATION_MODEL,
                'similarity_threshold': Config.NEWS_PROCESSOR.SIMILARITY_THRESHOLD,
                'min_cluster_size': Config.NEWS_PROCESSOR.MIN_CLUSTER_SIZE,
                'top_n_clusters': Config.NEWS_PROCESSOR.TOP_N_CLUSTERS
            }
            
            test_record = self.create_test_record(test_name, news_text[:500], config)
            
            # Log processing start
            self.log_processing_start(config)
            
            # Initialize processor
            processor = NewsProcessor(
                embedding_model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
                summarization_model=Config.NEWS_PROCESSOR.SUMMARIZATION_MODEL,
                similarity_threshold=Config.NEWS_PROCESSOR.SIMILARITY_THRESHOLD,
                min_cluster_size=Config.NEWS_PROCESSOR.MIN_CLUSTER_SIZE,
                top_n_clusters=Config.NEWS_PROCESSOR.TOP_N_CLUSTERS
            )
            
            # Process news text
            self.log_processing_step("processing", 0, 0)
            digest = processor.process_news_text(news_text)
            
            # Log completion
            processing_time = time.time() - start_time
            self.log_processing_complete(
                digest.total_articles, 
                len(digest.clusters), 
                processing_time
            )
            
            # Update test record
            self.update_test_record(
                test_record, 
                True, 
                processing_time, 
                digest.total_articles, 
                len(digest.clusters)
            )
            
            return {
                'success': True,
                'processing_time': processing_time,
                'articles_processed': digest.total_articles,
                'clusters_created': len(digest.clusters),
                'run_id': self.run_id,
                'test_id': test_record.id,
                'digest': digest
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_message = str(e)
            
            # Log error
            self.log_processing_error(error_message)
            
            # Update test record if it exists
            if test_record:
                self.update_test_record(
                    test_record, 
                    False, 
                    processing_time, 
                    0, 
                    0, 
                    error_message
                )
            
            return {
                'success': False,
                'processing_time': processing_time,
                'error_message': error_message,
                'run_id': self.run_id,
                'test_id': test_record.id if test_record else None
            }
    
    def get_test_history(self, limit: int = 10) -> list:
        """Get recent test history."""
        tests = self.db_session.query(NewsTest).order_by(
            NewsTest.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': test.id,
                'test_name': test.test_name,
                'success': test.success,
                'processing_time': test.processing_time,
                'articles_processed': test.articles_processed,
                'clusters_created': test.clusters_created,
                'created_at': test.created_at,
                'error_message': test.error_message
            }
            for test in tests
        ]
    
    def get_processing_logs(self, run_id: Optional[str] = None, limit: int = 20) -> list:
        """Get processing logs."""
        query = self.db_session.query(NewsProcessingLog)
        
        if run_id:
            query = query.filter(NewsProcessingLog.run_id == run_id)
        
        logs = query.order_by(NewsProcessingLog.created_at.desc()).limit(limit).all()
        
        return [
            {
                'id': log.id,
                'run_id': log.run_id,
                'status': log.status,
                'step': log.step,
                'articles_count': log.articles_count,
                'clusters_count': log.clusters_count,
                'processing_time': log.processing_time,
                'created_at': log.created_at,
                'completed_at': log.completed_at,
                'error_message': log.error_message
            }
            for log in logs
        ]
