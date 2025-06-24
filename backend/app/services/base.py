"""Base service class."""
from typing import TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseService(Generic[T]):
    """Base service class for common operations."""
    
    def __init__(self, model_class: T, db_session: Session):
        """Initialize service."""
        self.model_class = model_class
        self.db = db_session