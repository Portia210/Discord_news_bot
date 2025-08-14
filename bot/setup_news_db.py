"""
Database setup script for news processor.
"""

import sys
import logging
from pathlib import Path

# Add the bot directory to the path
sys.path.append(str(Path(__file__).parent))

from db.init_db import init_db, check_db_tables, get_db_info

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Setup the database for news processor."""
    print("="*80)
    print("NEWS PROCESSOR DATABASE SETUP")
    print("="*80)
    
    # Check current database status
    print("\n📊 Current Database Status:")
    db_info = get_db_info()
    print(f"   Database URL: {db_info['database_url']}")
    print(f"   Status: {db_info['status']}")
    print(f"   Tables: {db_info['tables_count']}")
    
    if db_info['tables']:
        print(f"   Existing tables: {', '.join(db_info['tables'])}")
    
    # Initialize database
    print("\n🚀 Initializing database...")
    if init_db():
        print("✅ Database initialization successful!")
    else:
        print("❌ Database initialization failed!")
        return
    
    # Check tables after initialization
    print("\n📋 Checking database tables...")
    tables = check_db_tables()
    
    expected_tables = [
        'symbols_list',
        'news_articles', 
        'news_clusters',
        'news_test',
        'news_processing_logs'
    ]
    
    print(f"\n📊 Database Tables:")
    for table in expected_tables:
        status = "✅" if table in tables else "❌"
        print(f"   {status} {table}")
    
    missing_tables = [table for table in expected_tables if table not in tables]
    if missing_tables:
        print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
    else:
        print(f"\n🎉 All expected tables created successfully!")
    
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print("You can now run the news processor tests:")
    print("   python test_news_processor.py  # Basic test")
    print("   python test_news_db.py         # Database integration test")


if __name__ == "__main__":
    main()
