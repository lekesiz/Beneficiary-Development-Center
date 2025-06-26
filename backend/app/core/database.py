"""Database utilities and helpers."""

from flask import g, current_app


def get_db():
    """
    Get database session.

    Returns:
        SQLAlchemy database session
    """
    from app import db

    return db.session


def init_db():
    """Initialize the database."""
    from app import db

    db.create_all()


def close_db(e=None):
    """Close database connection."""
    from app import db

    db.session.remove()


def commit_db():
    """Commit database transaction."""
    from app import db

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def rollback_db():
    """Rollback database transaction."""
    from app import db

    db.session.rollback()
