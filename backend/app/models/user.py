"""User model with role-based access control."""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Table, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
import uuid
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.models.base import TenantBaseModel
from app import db

# Password hasher instance
ph = PasswordHasher()

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    db.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'))
)


class Role(db.Model):
    """Role model for RBAC."""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    permissions = Column(JSON, default=list)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    
    # Relationships
    users = relationship('User', 
                        secondary=user_roles,
                        primaryjoin="Role.id == user_roles.c.role_id",
                        secondaryjoin="User.id == user_roles.c.user_id",
                        back_populates='roles')
    
    # Predefined system roles
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    TRAINER = 'trainer'
    STUDENT = 'student'
    
    @classmethod
    def get_default_permissions(cls, role_name):
        """Get default permissions for a role."""
        permissions_map = {
            cls.SUPER_ADMIN: [
                'manage_tenants',
                'manage_all_users',
                'manage_all_data',
                'access_all_tenants',
                'view_system_logs',
                'manage_subscriptions'
            ],
            cls.ADMIN: [
                'manage_users',
                'manage_beneficiaries',
                'manage_programs',
                'manage_evaluations',
                'view_reports',
                'manage_settings',
                'manage_ai_features'
            ],
            cls.TRAINER: [
                'view_assigned_beneficiaries',
                'create_evaluations',
                'grade_evaluations',
                'create_appointments',
                'view_program_content',
                'send_messages'
            ],
            cls.STUDENT: [
                'view_own_profile',
                'take_evaluations',
                'view_own_results',
                'view_assigned_programs',
                'book_appointments',
                'upload_documents'
            ]
        }
        return permissions_map.get(role_name, [])
    
    def has_permission(self, permission):
        """Check if role has a specific permission."""
        return permission in self.permissions
    
    def __repr__(self):
        """String representation."""
        return f"<Role {self.name}>"


class User(TenantBaseModel):
    """User model with authentication and role management."""
    __tablename__ = 'users'
    
    # Basic fields
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    
    # Profile fields
    avatar_url = Column(String(500))
    phone = Column(String(20))
    job_title = Column(String(100))
    department = Column(String(100))
    bio = Column(Text)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    
    # Security fields
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(255))
    last_login_at = Column(DateTime)
    last_login_ip = Column(INET)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    notification_settings = Column(JSON, default=dict)
    
    # Password reset
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime)
    
    # API access
    api_key = Column(String(255))
    api_key_created_at = Column(DateTime)
    
    # Relationships
    roles = relationship('Role', 
                        secondary=user_roles,
                        primaryjoin="User.id == user_roles.c.user_id",
                        secondaryjoin="Role.id == user_roles.c.role_id",
                        back_populates='users')
    created_beneficiaries = relationship('Beneficiary', foreign_keys='Beneficiary.created_by')
    assigned_beneficiaries = relationship('Beneficiary', foreign_keys='Beneficiary.assigned_trainer_id')
    # appointments_as_trainer = relationship('Appointment', foreign_keys='Appointment.trainer_id')
    created_programs = relationship('Program', foreign_keys='Program.created_by')
    # notifications = relationship('Notification', back_populates='user')
    # activity_logs = relationship('ActivityLog', back_populates='user')
    
    # Add unique constraint for email within tenant
    __table_args__ = (
        db.UniqueConstraint('email', 'tenant_id', name='_email_tenant_uc'),
    )
    
    def __init__(self, **kwargs):
        """Initialize user with default settings."""
        password = kwargs.pop('password', None)
        super().__init__(**kwargs)
        
        if password:
            self.set_password(password)
        
        # Set default preferences
        if not self.preferences:
            self.preferences = {
                'language': 'fr',
                'theme': 'light',
                'email_frequency': 'daily',
                'timezone': 'Europe/Paris'
            }
        
        # Set default notification settings
        if not self.notification_settings:
            self.notification_settings = {
                'email': True,
                'in_app': True,
                'sms': False,
                'evaluation_reminders': True,
                'appointment_reminders': True,
                'new_content': True
            }
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = ph.hash(password)
    
    def verify_password(self, password):
        """Verify password against hash."""
        try:
            ph.verify(self.password_hash, password)
            # If verification is successful, check if rehashing is needed
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                self.save()
            return True
        except VerifyMismatchError:
            return False
    
    @property
    def full_name(self):
        """Get user's full name."""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return ' '.join(parts) if parts else self.email
    
    @property
    def role(self):
        """Get primary role (for backward compatibility)."""
        if self.roles:
            # Return the highest priority role
            role_priority = [Role.SUPER_ADMIN, Role.ADMIN, Role.TRAINER, Role.STUDENT]
            for role_name in role_priority:
                if any(r.name == role_name for r in self.roles):
                    return role_name
        return Role.STUDENT  # Default role
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def has_any_role(self, *role_names):
        """Check if user has any of the specified roles."""
        return any(self.has_role(role) for role in role_names)
    
    def has_permission(self, permission):
        """Check if user has a specific permission."""
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False
    
    def add_role(self, role):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            self.save()
    
    def remove_role(self, role):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.save()
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.has_any_role(Role.SUPER_ADMIN, Role.ADMIN)
    
    def is_trainer(self):
        """Check if user is a trainer."""
        return self.has_role(Role.TRAINER)
    
    def is_student(self):
        """Check if user is a student."""
        return self.has_role(Role.STUDENT)
    
    def can_access_tenant(self, tenant_id):
        """Check if user can access a specific tenant."""
        if self.has_role(Role.SUPER_ADMIN):
            return True
        return self.tenant_id == tenant_id
    
    def update_last_login(self, ip_address=None):
        """Update last login information."""
        self.last_login_at = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        self.failed_login_attempts = 0
        self.save()
    
    def increment_failed_login(self):
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        self.save()
    
    def is_locked(self):
        """Check if account is locked."""
        if self.locked_until:
            if datetime.utcnow() < self.locked_until:
                return True
            else:
                # Unlock if time has passed
                self.locked_until = None
                self.failed_login_attempts = 0
                self.save()
        return False
    
    def generate_api_key(self):
        """Generate a new API key."""
        import secrets
        self.api_key = secrets.token_urlsafe(32)
        self.api_key_created_at = datetime.utcnow()
        self.save()
        return self.api_key
    
    def to_dict(self, exclude=None, include_roles=True):
        """Convert to dictionary."""
        exclude = exclude or []
        exclude.extend(['password_hash', 'two_factor_secret', 'reset_token', 'api_key'])
        
        data = super().to_dict(exclude=exclude)
        
        # Add computed fields
        data['full_name'] = self.full_name
        data['primary_role'] = self.role
        
        # Add roles if requested
        if include_roles:
            data['roles'] = [{'id': r.id, 'name': r.name} for r in self.roles]
        
        # Convert UUID to string
        if 'uuid' in data:
            data['uuid'] = str(data['uuid'])
        
        return data
    
    def __repr__(self):
        """String representation."""
        return f"<User {self.email}>"