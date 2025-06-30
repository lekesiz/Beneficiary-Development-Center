"""
Modèles de données pour les utilisateurs
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Role(str, Enum):
    """Rôles utilisateur"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class Permission(str, Enum):
    """Permissions système"""
    CREATE_TASK = "create_task"
    VIEW_TASK = "view_task"
    CANCEL_TASK = "cancel_task"
    MANAGE_MODELS = "manage_models"
    VIEW_METRICS = "view_metrics"
    ADMIN_SYSTEM = "admin_system"


class User(BaseModel):
    """Modèle utilisateur"""
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: str
    full_name: str = ""
    
    # Authentification
    is_active: bool = True
    role: Role = Role.USER
    permissions: List[Permission] = Field(default_factory=list)
    
    # Métadonnées
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

