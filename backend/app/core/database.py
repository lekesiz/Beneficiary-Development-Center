"""Database utilities and helpers."""
from flask import g
from app import db


def get_db():
    """
    Get database session.
    
    Returns:
        SQLAlchemy database session
    """
    return db.session


def init_db():
    """Initialize the database."""
    db.create_all()


def close_db(e=None):
    """Close database connection."""
    db.session.remove()


def commit_db():
    """Commit database transaction."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def rollback_db():
    """Rollback database transaction."""
    db.session.rollback()