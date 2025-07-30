"""
Database configuration module.
"""

import os

# Database URL - defaults to SQLite, can be changed to PostgreSQL
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bot_data.db")

# Enable SQL query logging
DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true" 