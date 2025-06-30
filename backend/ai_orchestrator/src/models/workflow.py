"""
Modèles de données pour les workflows
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Statuts d'exécution des workflows"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowStep(BaseModel):
    """Étape d'un workflow"""
    id: str
    name: str
    description: str = ""
    step_type: str = "task"  # task, condition, loop, etc.
    
    # Configuration de l'étape
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # IDs des étapes prérequises
    
    # État d'exécution
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Résultats
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Métadonnées
    retry_count: int = 0
    max_retries: int = 3
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowExecution(BaseModel):
    """Exécution d'un workflow"""
    id: UUID = Field(default_factory=uuid4)
    workflow_id: str
    name: str
    description: str = ""
    
    # Configuration
    steps: List[WorkflowStep] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    
    # État d'exécution
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_step: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Résultats
    final_output: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Métadonnées
    created_by: str
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

