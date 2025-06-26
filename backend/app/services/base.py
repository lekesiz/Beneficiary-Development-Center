"""Base service class."""

from typing import TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class for common operations."""

    def __init__(self, model_class: T = None, db_session: Session = None):
        """Initialize service."""
        self.model_class = model_class
        if db_session is None:
            from app.extensions import db

            self.db = db.session
        else:
            self.db = db_session
