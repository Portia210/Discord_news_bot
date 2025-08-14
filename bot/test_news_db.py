"""
Test script for news processor with database integration.
"""

import os
import sys
import logging
from pathlib import Path

# Add the bot directory to the path
sys.path.append(str(Path(__file__).parent))

from news_processor.db_test import NewsProcessorDBTest
from db.engine import SessionLocal
from db.models.news_test import NewsTest, NewsProcessingLog

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_news_text(file_path: str) -> str:
    """Load news text from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading news text: {e}")
        return ""


def print_test_results(results: dict):
    """Print test results in a readable format."""
    print("\n" + "="*80)
    print("NEWS PROCESSOR DATABASE TEST RESULTS")
    print("="*80)
    
    if results['success']:
        print(f"✅ Test PASSED")
        print(f"   Processing Time: {results['processing_time']:.2f} seconds")
        print(f"   Articles Processed: {results['articles_processed']}")
        print(f"   Clusters Created: {results['clusters_created']}")
        print(f"   Run ID: {results['run_id']}")
        print(f"   Test ID: {results['test_id']}")
        
        # Print digest summary
        digest = results['digest']
        print(f"\n📊 DIGEST SUMMARY:")
        print(f"   Total Articles: {digest.total_articles}")
        print(f"   Top Clusters: {len(digest.clusters)}")
        print(f"   Generated At: {digest.generated_at}")
        
        for i, cluster in enumerate(digest.clusters[:3], 1):  # Show top 3 clusters
            print(f"\n   {i}. Cluster (Importance: {cluster.importance_score:.2f})")
            print(f"      Size: {cluster.cluster_size} articles")
            print(f"      Tags: {', '.join(cluster.tags) if cluster.tags else 'None'}")
            print(f"      Summary: {cluster.summary[:100]}...")
    else:
        print(f"❌ Test FAILED")
        print(f"   Error: {results['error_message']}")
        print(f"   Processing Time: {results['processing_time']:.2f} seconds")
        print(f"   Run ID: {results['run_id']}")
        print(f"   Test ID: {results['test_id']}")


def print_test_history(db_test: NewsProcessorDBTest):
    """Print test history."""
    print("\n" + "="*80)
    print("TEST HISTORY")
    print("="*80)
    
    history = db_test.get_test_history(limit=5)
    
    if not history:
        print("No test history found.")
        return
    
    for test in history:
        status = "✅ PASS" if test['success'] else "❌ FAIL"
        print(f"\n{status} - {test['test_name']}")
        print(f"   ID: {test['id']}")
        print(f"   Created: {test['created_at']}")
        print(f"   Processing Time: {test['processing_time']:.2f}s" if test['processing_time'] else "   Processing Time: N/A")
        print(f"   Articles: {test['articles_processed']}")
        print(f"   Clusters: {test['clusters_created']}")
        if test['error_message']:
            print(f"   Error: {test['error_message']}")


def print_processing_logs(db_test: NewsProcessorDBTest, run_id: str):
    """Print processing logs for a specific run."""
    print(f"\n" + "="*80)
    print(f"PROCESSING LOGS FOR RUN: {run_id}")
    print("="*80)
    
    logs = db_test.get_processing_logs(run_id=run_id)
    
    if not logs:
        print("No processing logs found for this run.")
        return
    
    for log in logs:
        status_emoji = {
            'started': '🚀',
            'in_progress': '⏳',
            'completed': '✅',
            'failed': '❌'
        }.get(log['status'], '❓')
        
        print(f"\n{status_emoji} {log['status'].upper()} - {log['step']}")
        print(f"   Created: {log['created_at']}")
        if log['articles_count'] > 0 or log['clusters_count'] > 0:
            print(f"   Articles: {log['articles_count']}, Clusters: {log['clusters_count']}")
        if log['processing_time']:
            print(f"   Processing Time: {log['processing_time']:.2f}s")
        if log['error_message']:
            print(f"   Error: {log['error_message']}")


def main():
    """Main function to run the database test."""
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required")
        return
    
    # Load news text
    news_file_path = "data/messages export/news.txt"
    if not os.path.exists(news_file_path):
        logger.error(f"News file not found: {news_file_path}")
        return
    
    news_text = load_news_text(news_file_path)
    if not news_text:
        logger.error("No news text loaded")
        return
    
    logger.info(f"Loaded {len(news_text)} characters of news text")
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Initialize database test utility
        db_test = NewsProcessorDBTest(db)
        
        # Run the test
        logger.info("Starting news processor database test...")
        results = db_test.test_news_processing(news_text, "full_pipeline_test")
        
        # Print results
        print_test_results(results)
        
        # Print test history
        print_test_history(db_test)
        
        # Print processing logs for this run
        if results['run_id']:
            print_processing_logs(db_test, results['run_id'])
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        if results['success']:
            print("🎉 News processor database test completed successfully!")
            print(f"   The pipeline processed {results['articles_processed']} articles")
            print(f"   and created {results['clusters_created']} clusters")
            print(f"   in {results['processing_time']:.2f} seconds")
        else:
            print("💥 News processor database test failed!")
            print(f"   Error: {results['error_message']}")
        
    except Exception as e:
        logger.error(f"Error during database test: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
