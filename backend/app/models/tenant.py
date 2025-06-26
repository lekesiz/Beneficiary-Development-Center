"""Tenant model for multi-tenancy support."""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.models.base import BaseModel
from app.extensions import db


class Tenant(BaseModel):
    """Tenant model."""

    __tablename__ = "tenants"

    # Basic fields
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    domain = Column(String(100), unique=True)
    logo_url = Column(String(500))

    # Status and settings
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)

    # Subscription information
    subscription_plan = Column(String(50), default="basic")
    subscription_expires_at = Column(DateTime)
    max_users = Column(Integer, default=10)
    max_beneficiaries = Column(Integer, default=100)

    # Contact information
    contact_name = Column(String(100))
    contact_email = Column(String(255))
    contact_phone = Column(String(20))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="France")

    # Features and limits
    features = Column(JSON, default=dict)
    
    # Relationships
    users = relationship("User", back_populates="tenant")

    def __init__(self, **kwargs):
        """Initialize tenant with default settings."""
        super().__init__(**kwargs)

        # Set default settings if not provided
        if not self.settings:
            self.settings = {
                "language": "fr",
                "timezone": "Europe/Paris",
                "date_format": "DD/MM/YYYY",
                "currency": "EUR",
                "theme": "light",
                "email_notifications": True,
                "sms_notifications": False,
                "two_factor_auth": False,
            }

        # Set default features if not provided
        if not self.features:
            self.features = {
                "ai_enabled": True,
                "custom_branding": False,
                "api_access": False,
                "advanced_reporting": False,
                "white_label": False,
                "sso_enabled": False,
                "custom_fields": False,
            }

    def is_subscription_active(self):
        """Check if subscription is active."""
        if not self.is_active:
            return False

        if self.subscription_expires_at:
            from datetime import datetime

            return datetime.utcnow() < self.subscription_expires_at

        return True

    def can_add_user(self):
        """Check if tenant can add more users."""
        from app.models.user import User

        current_users = db.session.query(User).filter_by(tenant_id=self.id, is_active=True).count()
        return current_users < self.max_users

    def can_add_beneficiary(self):
        """Check if tenant can add more beneficiaries."""
        from app.models.beneficiary import Beneficiary

        current_beneficiaries = db.session.query(Beneficiary).filter_by(tenant_id=self.id, status="active").count()
        return current_beneficiaries < self.max_beneficiaries

    def get_usage_stats(self):
        """Get tenant usage statistics."""
        from app.models.user import User
        from app.models.beneficiary import Beneficiary
        from app.models.program import Program
        from app.models.evaluation import Evaluation

        return {
            "users": {
                "current": db.session.query(User).filter_by(tenant_id=self.id, is_active=True).count(),
                "max": self.max_users,
            },
            "beneficiaries": {
                "current": db.session.query(Beneficiary).filter_by(tenant_id=self.id, status="active").count(),
                "max": self.max_beneficiaries,
            },
            "programs": db.session.query(Program).filter_by(tenant_id=self.id, is_active=True).count(),
            "evaluations": db.session.query(Evaluation).filter_by(tenant_id=self.id, is_active=True).count(),
        }

    def update_settings(self, settings_dict):
        """Update tenant settings."""
        if self.settings is None:
            self.settings = {}
        self.settings.update(settings_dict)
        return self.save()

    def enable_feature(self, feature_name):
        """Enable a specific feature."""
        if self.features is None:
            self.features = {}
        self.features[feature_name] = True
        return self.save()

    def disable_feature(self, feature_name):
        """Disable a specific feature."""
        if self.features is None:
            self.features = {}
        self.features[feature_name] = False
        return self.save()

    def has_feature(self, feature_name):
        """Check if tenant has a specific feature enabled."""
        if not self.features:
            return False
        return self.features.get(feature_name, False)

    def to_dict(self, exclude=None):
        """Convert to dictionary with additional fields."""
        exclude = exclude or []
        data = super().to_dict(exclude=exclude)

        # Add computed fields
        data["is_subscription_active"] = self.is_subscription_active()
        data["usage_stats"] = self.get_usage_stats()

        # Convert UUID to string
        if "uuid" in data:
            data["uuid"] = str(data["uuid"])

        return data

    def __repr__(self):
        """String representation."""
        return f"<Tenant {self.name}>"
