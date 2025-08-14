"""
Database initialization module.
"""

import logging
from .engine import engine, Base
from .config import DATABASE_URL

logger = logging.getLogger(__name__)


def init_db() -> bool:
    """Initialize the database by creating all tables."""
    try:
        logger.info(f"Initializing database: {DATABASE_URL}")
        
        from .models import SymbolsList  # noqa: F401
        from .models.news_models import NewsArticle, NewsCluster  # noqa: F401
        from .models.news_test import NewsTest, NewsProcessingLog  # noqa: F401
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def drop_db() -> bool:
    """Drop all tables from the database."""
    try:
        logger.warning("Dropping all database tables")
        
        from .models import SymbolsList  # noqa: F401
        from .models.news_models import NewsArticle, NewsCluster  # noqa: F401
        from .models.news_test import NewsTest, NewsProcessingLog  # noqa: F401
        Base.metadata.drop_all(bind=engine)
        
        logger.info("All database tables dropped successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database drop failed: {e}")
        return False


def reset_db() -> bool:
    """Reset the database by dropping and recreating all tables."""
    try:
        logger.warning("Resetting database")
        
        if not drop_db():
            return False
        
        if not init_db():
            return False
        
        logger.info("Database reset completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        return False


def check_db_tables() -> list:
    """Check which tables exist in the database."""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Found {len(tables)} tables in database: {tables}")
        return tables
        
    except Exception as e:
        logger.error(f"Failed to check database tables: {e}")
        return []


def get_db_info() -> dict:
    """Get database information and status."""
    try:
        tables = check_db_tables()
        return {
            "database_url": DATABASE_URL,
            "tables_count": len(tables),
            "tables": tables,
            "status": "connected" if tables is not None else "error"
        }
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "database_url": DATABASE_URL,
            "tables_count": 0,
            "tables": [],
            "status": "error",
            "error": str(e)
        } 