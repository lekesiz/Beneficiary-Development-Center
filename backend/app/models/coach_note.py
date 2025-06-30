from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class CoachNote(BaseModel):
    """
    Coach Notes Model for BDC Platform
    
    Allows coaches/trainers to create and manage notes about students,
    track progress, observations, and development recommendations.
    """
    __tablename__ = 'coach_notes'
    
    id = Column(Integer, primary_key=True)
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    coach_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False, index=True)
    
    # Note Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default='general')
    
    # Note Settings
    is_private = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default='medium', nullable=False)  # low, medium, high, urgent
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    student = relationship("User", foreign_keys=[student_id], backref="received_notes")
    coach = relationship("User", foreign_keys=[coach_id], backref="created_notes")
    tenant = relationship("Tenant", backref="coach_notes")
    
    def __repr__(self):
        return f'<CoachNote {self.id}: {self.title} by {self.coach_id} for {self.student_id}>'
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'coach_id': self.coach_id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_private': self.is_private,
            'is_archived': self.is_archived,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student_name': f"{self.student.first_name} {self.student.last_name}" if self.student else None,
            'coach_name': f"{self.coach.first_name} {self.coach.last_name}" if self.coach else None
        }
    
    @classmethod
    def get_categories(cls):
        """Get available note categories"""
        return [
            'general',
            'progress',
            'observation',
            'recommendation', 
            'concern',
            'achievement',
            'behavior',
            'skill_development',
            'goal_setting',
            'feedback'
        ]
    
    @classmethod
    def get_priorities(cls):
        """Get available priority levels"""
        return ['low', 'medium', 'high', 'urgent']