"""
SymbolsList model definition.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func

from ..engine import Base


class SymbolsList(Base):
    """Model for storing symbol information."""
    __tablename__ = "symbols_list"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    english_description = Column(Text, nullable=True)
    hebrew_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

