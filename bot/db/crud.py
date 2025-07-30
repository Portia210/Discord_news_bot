"""
Generic CRUD operations that can be used with any model.
"""

from typing import Any, Dict, List, Optional, Generic, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import Column

from .engine import get_db_sync

# Generic type for any model
ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """Generic CRUD operations for any model."""
    
    def __init__(self, model: type[ModelType]):
        self.model = model
    
    def create(self, db: Session, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by any field."""
        return db.query(self.model).filter(getattr(self.model, field) == value).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, db: Session, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by ID."""
        db_obj = self.get(db, id)
        if db_obj:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def update_by_field(self, db: Session, field: str, value: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by any field."""
        db_obj = self.get_by_field(db, field, value)
        if db_obj:
            for field_name, field_value in obj_in.items():
                if hasattr(db_obj, field_name):
                    setattr(db_obj, field_name, field_value)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete a record by ID."""
        db_obj = self.get(db, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False
    
    def delete_by_field(self, db: Session, field: str, value: Any) -> bool:
        """Delete a record by any field."""
        db_obj = self.get_by_field(db, field, value)
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        from sqlalchemy import text
        db = get_db_sync()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False 