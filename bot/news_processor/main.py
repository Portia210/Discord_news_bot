"""
Main script to test the news processor.
"""

import os
import sys
import logging
from pathlib import Path

# Add the bot directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from news_processor import NewsProcessor
from config import Config
from db.engine import SessionLocal
from db.models.news_models import NewsArticle as DBNewsArticle, NewsCluster as DBNewsCluster

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


def print_digest(digest):
    """Print the news digest in a readable format."""
    print("\n" + "="*80)
    print(f"NEWS DIGEST - {digest.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Articles: {digest.total_articles}")
    print(f"Top Clusters: {len(digest.clusters)}")
    print("="*80)
    
    for i, cluster in enumerate(digest.clusters, 1):
        print(f"\n{i}. CLUSTER (Importance: {cluster.importance_score:.2f})")
        print(f"   Size: {cluster.cluster_size} articles")
        print(f"   Tags: {', '.join(cluster.tags) if cluster.tags else 'None'}")
        print(f"   Summary: {cluster.summary}")
        print(f"   Articles:")
        for article in cluster.articles:
            print(f"     - {article.headline}")
        print("-" * 60)


def main():
    """Main function to run the news processor."""
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
    
    # Initialize processor with config
    processor = NewsProcessor(
        embedding_model=Config.NEWS_PROCESSOR.EMBEDDING_MODEL,
        summarization_model=Config.NEWS_PROCESSOR.SUMMARIZATION_MODEL,
        similarity_threshold=Config.NEWS_PROCESSOR.SIMILARITY_THRESHOLD,
        min_cluster_size=Config.NEWS_PROCESSOR.MIN_CLUSTER_SIZE,
        top_n_clusters=Config.NEWS_PROCESSOR.TOP_N_CLUSTERS
    )
    
    try:
        # Process news
        digest = processor.process_news_text(news_text)
        
        # Print results
        print_digest(digest)
        
        # Save to database
        try:
            db = SessionLocal()
            processor.save_to_database(digest, db)
            logger.info("Successfully saved to database")
        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing news: {e}")
        raise


if __name__ == "__main__":
    main()
