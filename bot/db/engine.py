"""
SQLAlchemy engine and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import DATABASE_URL, DB_ECHO

# Create SQLAlchemy engine
if "sqlite" in DATABASE_URL.lower():
    engine = create_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL, echo=DB_ECHO)

# Create session factory and base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_sync() -> Session:
    """Get a database session."""
    return SessionLocal() 