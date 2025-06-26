"""Base models and mixins."""

from datetime import datetime
from flask import g
from sqlalchemy import Column, Integer, DateTime, ForeignKey, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query, Session


class Base:
    """Base model class."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)

    @classmethod
    def query(cls) -> Query:
        """Return query object."""
        from app.extensions import db

        return db.session.query(cls)

    def save(self, commit=True):
        """Save the record."""
        from app.extensions import db

        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, **kwargs):
        """Update record with given fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()

    def delete(self, commit=True):
        """Delete the record."""
        from app.extensions import db

        db.session.delete(self)
        if commit:
            db.session.commit()

    def to_dict(self, exclude=None):
        """Convert model to dictionary."""
        exclude = exclude or []
        data = {}

        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[column.name] = value

        return data

    @classmethod
    def create(cls, **kwargs):
        """Create a new record."""
        instance = cls(**kwargs)
        return instance.save()

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        return cls.query.get(record_id)

    @classmethod
    def get_or_404(cls, record_id):
        """Get record by ID or raise 404."""
        return cls.query.get_or_404(record_id)

    def __repr__(self):
        """String representation."""
        return f"<{self.__class__.__name__} {self.id}>"


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # For soft deletes


class TenantMixin:
    """Mixin for multi-tenant support."""

    @declared_attr
    def tenant_id(cls):
        """Tenant ID column."""
        return Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    @declared_attr
    def __table_args__(cls):
        """Add tenant_id index."""
        from app.extensions import db

        return (db.Index(f"idx_{cls.__tablename__}_tenant_id", "tenant_id"),)


# Query class for tenant filtering
class TenantQuery(Query):
    """Custom query class that filters by tenant."""

    def __init__(self, entities, session=None):
        """Initialize query."""
        super().__init__(entities, session)

    def __iter__(self):
        """Apply tenant filter before iteration."""
        return super().__iter__()

    def _apply_tenant_filter(self):
        """Apply tenant filter to query."""
        if hasattr(g, "tenant_id") and g.tenant_id:
            # Check if the main entity has tenant_id
            main_entity = self._mapper_zero().class_
            if hasattr(main_entity, "tenant_id"):
                return self.filter(main_entity.tenant_id == g.tenant_id)
        return self


# Event listeners for automatic tenant assignment
@event.listens_for(Session, "before_flush")
def receive_before_flush(session, flush_context, instances):
    """Set tenant_id on new objects before flush."""
    for obj in session.new:
        if hasattr(obj, "tenant_id") and obj.tenant_id is None:
            if hasattr(g, "tenant_id"):
                obj.tenant_id = g.tenant_id


# Create base models without db.Model inheritance first
class _BaseModelMixin(Base, TimestampMixin):
    """Base model mixin with timestamps."""

    __abstract__ = True


class _TenantBaseModelMixin(Base, TimestampMixin, TenantMixin):
    """Base model mixin with timestamps and tenant support."""

    __abstract__ = True

    @classmethod
    def query(cls):
        """Return tenant-filtered query."""
        from app.extensions import db

        query = TenantQuery(cls, session=db.session)
        return query._apply_tenant_filter()


# Import db from extensions to avoid circular imports
from app.extensions import db


class BaseModel(db.Model, _BaseModelMixin):
    """Base model with timestamps."""

    __abstract__ = True


class TenantBaseModel(db.Model, _TenantBaseModelMixin):
    """Base model with timestamps and tenant support."""

    __abstract__ = True
