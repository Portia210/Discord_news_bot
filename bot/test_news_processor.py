"""
Simple test script for the news processor.
"""

import os
import sys
import logging
from pathlib import Path

# Add the bot directory to the path
sys.path.append(str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported."""
    try:
        from news_processor import NewsProcessor
        from news_processor.models import NewsArticle, NewsCluster, NewsDigest
        from news_processor.embedding_service import EmbeddingService
        from news_processor.deduplicator import Deduplicator
        from news_processor.clustering import ClusteringService
        from news_processor.summarizer import Summarizer
        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from config import Config
        logger.info(f"✅ Config loaded successfully")
        logger.info(f"   Embedding model: {Config.NEWS_PROCESSOR.EMBEDDING_MODEL}")
        logger.info(f"   Summarization model: {Config.NEWS_PROCESSOR.SUMMARIZATION_MODEL}")
        return True
    except Exception as e:
        logger.error(f"❌ Config test failed: {e}")
        return False

def test_openai_key():
    """Test OpenAI API key availability."""
    if os.getenv("OPENAI_API_KEY"):
        logger.info("✅ OpenAI API key found")
        return True
    else:
        logger.warning("⚠️  OpenAI API key not found in environment variables")
        return False

def test_news_file():
    """Test if news file exists."""
    news_file_path = "data/messages export/news.txt"
    if os.path.exists(news_file_path):
        logger.info(f"✅ News file found: {news_file_path}")
        return True
    else:
        logger.warning(f"⚠️  News file not found: {news_file_path}")
        return False

def main():
    """Run all tests."""
    logger.info("Running news processor tests...")
    
    tests = [
        test_imports,
        test_config,
        test_openai_key,
        test_news_file
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    logger.info(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The news processor is ready to use.")
    else:
        logger.warning("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
