"""
Modèles de données pour les tâches
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Priority(str, Enum):
    """Priorité des tâches"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types de tâches"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    RESEARCH = "research"
    CUSTOM = "custom"


class TaskStatus(str, Enum):
    """Statuts des tâches"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TaskResult(BaseModel):
    """Résultat d'une tâche par un modèle d'IA"""
    model_id: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    execution_time: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        protected_namespaces = ()  # Pydantic warning'i düzeltmek için


class ValidationResult(BaseModel):
    """Résultat de validation croisée"""
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    consensus_score: float = Field(ge=0.0, le=1.0)
    discrepancies: List[str] = Field(default_factory=list)
    recommended_result: Optional[str] = None
    validation_notes: str = ""
    
    class Config:
        protected_namespaces = ()  # Pydantic warning'i düzeltmek için


class Task(BaseModel):
    """Modèle principal pour les tâches"""
    id: UUID = Field(default_factory=uuid4)
    type: TaskType
    priority: Priority = Priority.MEDIUM
    title: str
    description: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    
    # Configuration
    max_retries: int = 3
    timeout_seconds: int = 300
    require_validation: bool = True
    min_consensus_score: float = 0.7
    
    # Assignation
    assigned_models: List[str] = Field(default_factory=list)
    preferred_models: List[str] = Field(default_factory=list)
    excluded_models: List[str] = Field(default_factory=list)
    
    # Résultats
    results: List[TaskResult] = Field(default_factory=list)
    validation: Optional[ValidationResult] = None
    final_result: Optional[str] = None
    
    # Métadonnées
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Historique
    retry_count: int = 0
    error_messages: List[str] = Field(default_factory=list)
    execution_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
        protected_namespaces = ()  # Pydantic warning'i düzeltmek için
    
    def add_result(self, result: TaskResult) -> None:
        """Ajouter un résultat de modèle d'IA"""
        self.results.append(result)
        self.updated_at = datetime.utcnow()
        
        # Log l'ajout du résultat
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "result_added",
            "model_id": result.model_id,
            "confidence": result.confidence
        })
    
    def set_validation(self, validation: ValidationResult) -> None:
        """Définir le résultat de validation"""
        self.validation = validation
        self.updated_at = datetime.utcnow()
        
        if validation.is_valid and validation.recommended_result:
            self.final_result = validation.recommended_result
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.utcnow()
        
        # Log la validation
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "validation_completed",
            "is_valid": validation.is_valid,
            "consensus_score": validation.consensus_score
        })
    
    def mark_failed(self, error_message: str) -> None:
        """Marquer la tâche comme échouée"""
        self.status = TaskStatus.FAILED
        self.error_messages.append(error_message)
        self.updated_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()
        
        # Log l'échec
        self.execution_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "task_failed",
            "error": error_message,
            "retry_count": self.retry_count
        })
    
    def can_retry(self) -> bool:
        """Vérifier si la tâche peut être relancée"""
        return self.retry_count < self.max_retries and self.status in [TaskStatus.FAILED, TaskStatus.RETRY]
    
    def prepare_retry(self) -> None:
        """Préparer la tâche pour une nouvelle tentative"""
        if self.can_retry():
            self.retry_count += 1
            self.status = TaskStatus.RETRY
            self.results.clear()
            self.validation = None
            self.final_result = None
            self.updated_at = datetime.utcnow()
            
            # Log la préparation du retry
            self.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "retry_prepared",
                "retry_count": self.retry_count
            })
    
    @property
    def is_completed(self) -> bool:
        """Vérifier si la tâche est terminée"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
    
    @property
    def execution_duration(self) -> Optional[float]:
        """Durée d'exécution en secondes"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

