from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class AuditLog(BaseModel):
    """
    Audit Log Model for BDC Platform
    
    Tracks all significant actions performed by users in the system
    for security, compliance, and monitoring purposes.
    """
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    
    # User and Tenant Information
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for system actions
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Action Information
    action = Column(String(100), nullable=False, index=True)  # e.g., 'create', 'update', 'delete', 'login', 'logout'
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., 'user', 'course', 'evaluation', 'coach_note'
    resource_id = Column(String(50), nullable=True, index=True)  # ID of the affected resource
    
    # Request Information
    endpoint = Column(String(200), nullable=True)  # API endpoint called
    http_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client information
    
    # Action Details
    details = Column(JSON, nullable=True)  # Additional context and metadata
    old_values = Column(JSON, nullable=True)  # Previous values for updates
    new_values = Column(JSON, nullable=True)  # New values for creates/updates
    
    # Status and Outcome
    status = Column(String(20), default='success', nullable=False)  # success, failure, error
    error_message = Column(Text, nullable=True)  # Error details if status is failure/error
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds
    
    # Security Context
    session_id = Column(String(128), nullable=True)  # User session identifier
    risk_score = Column(Integer, default=0, nullable=False)  # Risk assessment score (0-100)
    
    # Relationships
    user = relationship("User", backref="audit_logs")
    tenant = relationship("Tenant", backref="audit_logs")
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} on {self.resource_type} by {self.user_id}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'details': self.details,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'duration_ms': self.duration_ms,
            'session_id': self.session_id,
            'risk_score': self.risk_score,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else 'System'
        }
    
    @classmethod
    def create_log(cls, action, resource_type, user_id=None, tenant_id=None, 
                   resource_id=None, details=None, old_values=None, new_values=None,
                   endpoint=None, http_method=None, ip_address=None, user_agent=None,
                   session_id=None, risk_score=0, status='success', error_message=None):
        """
        Create a new audit log entry
        
        Args:
            action: Action performed (e.g., 'create', 'update', 'delete')
            resource_type: Type of resource affected (e.g., 'user', 'course')
            user_id: ID of user performing action
            tenant_id: ID of tenant
            resource_id: ID of affected resource
            details: Additional context information
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            endpoint: API endpoint called
            http_method: HTTP method used
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: User session ID
            risk_score: Risk assessment score (0-100)
            status: Action status ('success', 'failure', 'error')
            error_message: Error details if applicable
            
        Returns:
            Created AuditLog instance
        """
        log_entry = cls(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            tenant_id=tenant_id,
            resource_id=resource_id,
            endpoint=endpoint,
            http_method=http_method,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            old_values=old_values,
            new_values=new_values,
            status=status,
            error_message=error_message,
            session_id=session_id,
            risk_score=risk_score,
            timestamp=datetime.utcnow()
        )
        
        return log_entry
    
    @classmethod
    def get_actions(cls):
        """Get list of standard audit actions"""
        return [
            'create', 'read', 'update', 'delete',
            'login', 'logout', 'login_failed',
            'password_change', 'password_reset',
            'permission_granted', 'permission_denied',
            'export', 'import', 'download', 'upload',
            'search', 'view', 'approve', 'reject',
            'archive', 'restore', 'activate', 'deactivate'
        ]
    
    @classmethod
    def get_resource_types(cls):
        """Get list of standard resource types"""
        return [
            'user', 'tenant', 'role', 'permission',
            'beneficiary', 'program', 'course', 'course_session',
            'evaluation', 'question', 'response',
            'learning_path', 'milestone',
            'coach_note', 'chat_message', 'conversation',
            'file', 'report', 'setting', 'system'
        ]
    
    @classmethod
    def calculate_risk_score(cls, action, resource_type, user_role=None, 
                           ip_change=False, time_anomaly=False, bulk_operation=False):
        """
        Calculate risk score for an action
        
        Args:
            action: Action being performed
            resource_type: Type of resource
            user_role: Role of user performing action
            ip_change: Whether IP address changed from previous session
            time_anomaly: Whether action time is unusual for user
            bulk_operation: Whether this is a bulk operation
            
        Returns:
            Risk score (0-100)
        """
        base_score = 0
        
        # Action-based risk
        high_risk_actions = ['delete', 'permission_granted', 'export', 'password_reset']
        medium_risk_actions = ['create', 'update', 'upload', 'approve']
        
        if action in high_risk_actions:
            base_score += 30
        elif action in medium_risk_actions:
            base_score += 15
        else:
            base_score += 5
        
        # Resource-based risk
        sensitive_resources = ['user', 'role', 'permission', 'tenant']
        if resource_type in sensitive_resources:
            base_score += 20
        
        # Context-based risk factors
        if ip_change:
            base_score += 15
        if time_anomaly:
            base_score += 10
        if bulk_operation:
            base_score += 15
        
        # User role modifier
        if user_role == 'admin':
            base_score = max(0, base_score - 10)  # Admins get lower risk scores
        elif user_role == 'student':
            base_score += 5  # Students get slightly higher risk scores
        
        return min(100, base_score)  # Cap at 100