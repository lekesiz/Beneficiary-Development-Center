"""
Modèles de données pour les modèles d'IA
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ModelType(str, Enum):
    """Types de modèles d'IA"""
    CLAUDE = "claude"
    OPENAI_GPT = "openai_gpt"
    GEMINI = "gemini"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    LLAMA = "llama"
    MISTRAL = "mistral"
    OFFLINE_CUSTOM = "offline_custom"


class ModelStatus(str, Enum):
    """Statuts des modèles d'IA"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    OFFLINE = "offline"


class Capability(str, Enum):
    """Capacités des modèles d'IA"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    RESEARCH = "research"
    MATH_REASONING = "math_reasoning"
    LOGICAL_REASONING = "logical_reasoning"
    MULTIMODAL = "multimodal"
    FUNCTION_CALLING = "function_calling"


class ModelMetrics(BaseModel):
    """Métriques de performance d'un modèle"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    last_request_time: Optional[datetime] = None
    uptime_percentage: float = 100.0
    
    # Métriques de qualité
    average_confidence: float = 0.0
    validation_success_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    
    # Métriques de coût
    cost_per_token: float = 0.0
    cost_per_request: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Taux de succès des requêtes"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def failure_rate(self) -> float:
        """Taux d'échec des requêtes"""
        return 100.0 - self.success_rate


class RateLimitConfig(BaseModel):
    """Configuration des limites de taux"""
    requests_per_minute: int = 60
    requests_per_hour: int = 3600
    requests_per_day: int = 86400
    tokens_per_minute: int = 150000
    concurrent_requests: int = 10
    
    # Backoff configuration
    initial_backoff: float = 1.0
    max_backoff: float = 60.0
    backoff_multiplier: float = 2.0


class AIModel(BaseModel):
    """Modèle principal pour les modèles d'IA"""
    id: str = Field(..., description="Identifiant unique du modèle")
    name: str = Field(..., description="Nom du modèle")
    type: ModelType = Field(..., description="Type du modèle")
    version: str = Field(default="1.0", description="Version du modèle")
    
    # Configuration
    capabilities: List[Capability] = Field(default_factory=list)
    max_tokens: int = Field(default=4096, description="Nombre maximum de tokens")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    
    # Statut et disponibilité
    status: ModelStatus = ModelStatus.ACTIVE
    is_available: bool = True
    priority: int = Field(default=1, ge=1, le=10, description="Priorité (1=haute, 10=basse)")
    
    # Configuration API
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # Limites et coûts
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)
    cost_per_1k_tokens: float = 0.0
    
    # Métriques
    metrics: ModelMetrics = Field(default_factory=ModelMetrics)
    
    # Métadonnées
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_health_check: Optional[datetime] = None
    
    # Configuration spécialisée
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        protected_namespaces = ()  # Pydantic warning'i düzeltmek için
    
    def has_capability(self, capability: Capability) -> bool:
        """Vérifier si le modèle a une capacité spécifique"""
        return capability in self.capabilities
    
    def is_suitable_for_task(self, task_type: str, required_capabilities: List[Capability] = None) -> bool:
        """Vérifier si le modèle convient pour un type de tâche"""
        if not self.is_available or self.status != ModelStatus.ACTIVE:
            return False
        
        if required_capabilities:
            return all(self.has_capability(cap) for cap in required_capabilities)
        
        # Mapping basique des types de tâches aux capacités
        task_capability_mapping = {
            "text_generation": [Capability.TEXT_GENERATION],
            "code_generation": [Capability.CODE_GENERATION],
            "analysis": [Capability.ANALYSIS],
            "translation": [Capability.TRANSLATION],
            "summarization": [Capability.SUMMARIZATION],
            "question_answering": [Capability.QUESTION_ANSWERING],
            "creative_writing": [Capability.CREATIVE_WRITING],
            "research": [Capability.RESEARCH]
        }
        
        required_caps = task_capability_mapping.get(task_type, [])
        return all(self.has_capability(cap) for cap in required_caps)
    
    def update_metrics(self, success: bool, response_time: float, tokens_used: int = 0, cost: float = 0.0, confidence: float = 0.0) -> None:
        """Mettre à jour les métriques du modèle"""
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.utcnow()
        
        if success:
            self.metrics.successful_requests += 1
            if confidence > 0:
                # Mise à jour de la confiance moyenne
                total_confidence = self.metrics.average_confidence * (self.metrics.successful_requests - 1) + confidence
                self.metrics.average_confidence = total_confidence / self.metrics.successful_requests
        else:
            self.metrics.failed_requests += 1
        
        # Mise à jour du temps de réponse moyen
        total_time = self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time
        self.metrics.average_response_time = total_time / self.metrics.total_requests
        
        # Mise à jour des tokens et coûts
        self.metrics.total_tokens_used += tokens_used
        self.metrics.total_cost += cost
        
        if self.metrics.total_requests > 0:
            self.metrics.cost_per_request = self.metrics.total_cost / self.metrics.total_requests
        
        if self.metrics.total_tokens_used > 0:
            self.metrics.cost_per_token = self.metrics.total_cost / self.metrics.total_tokens_used
        
        self.updated_at = datetime.utcnow()
    
    def set_status(self, status: ModelStatus, reason: str = "") -> None:
        """Changer le statut du modèle"""
        self.status = status
        self.is_available = status == ModelStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        
        # Log le changement de statut dans la config
        if "status_history" not in self.config:
            self.config["status_history"] = []
        
        self.config["status_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": status.value,
            "reason": reason
        })
        
        # Garder seulement les 100 derniers changements
        self.config["status_history"] = self.config["status_history"][-100:]
    
    def health_check(self) -> bool:
        """Effectuer un contrôle de santé du modèle"""
        self.last_health_check = datetime.utcnow()
        
        # Logique de base pour déterminer la santé
        if self.status == ModelStatus.ERROR:
            return False
        
        # Vérifier le taux de succès récent
        if self.metrics.total_requests > 10 and self.metrics.success_rate < 50:
            self.set_status(ModelStatus.ERROR, "Low success rate")
            return False
        
        # Vérifier si le modèle répond dans un délai raisonnable
        if self.metrics.average_response_time > 30.0:
            self.set_status(ModelStatus.MAINTENANCE, "High response time")
            return False
        
        if self.status != ModelStatus.ACTIVE:
            self.set_status(ModelStatus.ACTIVE, "Health check passed")
        
        return True
    
    @property
    def efficiency_score(self) -> float:
        """Score d'efficacité basé sur les métriques"""
        if self.metrics.total_requests == 0:
            return 0.0
        
        # Facteurs: taux de succès, temps de réponse, coût, confiance
        success_factor = self.metrics.success_rate / 100.0
        time_factor = max(0, 1 - (self.metrics.average_response_time / 30.0))  # 30s comme référence
        confidence_factor = self.metrics.average_confidence
        
        # Score pondéré
        score = (success_factor * 0.4 + time_factor * 0.3 + confidence_factor * 0.3)
        return min(1.0, max(0.0, score))

