"""Notification model for storing user notifications."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from app.models.base import BaseModel


class Notification(BaseModel):
    """Model for user notifications."""
    
    __tablename__ = 'notifications'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default='general')
    priority = Column(String(20), nullable=False, default='normal')  # low, normal, high, urgent
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    action_url = Column(String(500), nullable=True)
    extra_data = Column(Text, nullable=True)  # JSON string for additional data
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'category': self.category,
            'priority': self.priority,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'action_url': self.action_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'