"""
Connecteurs pour les différents modèles d'IA
"""

from .base import BaseAIConnector, AIResponse
from .claude_connector import ClaudeConnector
from .openai_connector import OpenAIConnector
from .demo_connector import DemoConnector

__all__ = [
    "BaseAIConnector",
    "AIResponse",
    "ClaudeConnector",
    "OpenAIConnector", 
    "DemoConnector"
]

