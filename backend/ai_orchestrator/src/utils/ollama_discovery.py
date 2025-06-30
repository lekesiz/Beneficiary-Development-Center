"""
Service de découverte automatique des modèles Ollama
"""

import asyncio
from typing import Dict, List, Optional, Any
from loguru import logger

from ..models.ai_model import AIModel, ModelType, Capability
from ..connectors.ollama_connector import OllamaConnector


class OllamaDiscoveryService:
    """
    Service pour découvrir automatiquement les modèles Ollama disponibles
    """
    
    def __init__(self, api_base: str = "http://localhost:11434"):
        self.api_base = api_base
        self.connector = None
        
        # Mapping des modèles connus vers leurs capacités
        self.model_capabilities = {
            # Modèles de base
            'llama2': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION
            ],
            'llama3': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION
            ],
            'llama3.2': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION
            ],
            
            # Modèles de code
            'codellama': [
                Capability.CODE_GENERATION,
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.QUESTION_ANSWERING
            ],
            'deepseek-coder': [
                Capability.CODE_GENERATION,
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.QUESTION_ANSWERING,
                Capability.MATH_REASONING
            ],
            'qwen2.5-coder': [
                Capability.CODE_GENERATION,
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.QUESTION_ANSWERING,
                Capability.MATH_REASONING
            ],
            
            # Modèles généralistes
            'qwen2.5': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION,
                Capability.MATH_REASONING,
                Capability.LOGICAL_REASONING
            ],
            'qwen3': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION,
                Capability.MATH_REASONING,
                Capability.LOGICAL_REASONING
            ],
            'deepseek': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION,
                Capability.MATH_REASONING,
                Capability.LOGICAL_REASONING
            ],
            'deepseek-r1': [
                Capability.TEXT_GENERATION,
                Capability.ANALYSIS,
                Capability.CREATIVE_WRITING,
                Capability.QUESTION_ANSWERING,
                Capability.SUMMARIZATION,
                Capability.TRANSLATION,
                Capability.CODE_GENERATION,
                Capability.MATH_REASONING,
                Capability.LOGICAL_REASONING
            ]
        }
    
    async def discover_models(self) -> List[Dict[str, Any]]:
        """
        Découvrir tous les modèles Ollama disponibles
        
        Returns:
            List[Dict]: Liste des modèles découverts
        """
        try:
            # Créer un connecteur temporaire pour la découverte
            temp_connector = OllamaConnector("discovery", {
                'api_base': self.api_base
            })
            
            # Se connecter
            if not await temp_connector.connect():
                logger.warning("Impossible de se connecter à Ollama pour la découverte")
                return []
            
            # Lister les modèles
            models = await temp_connector.list_available_models()
            
            # Fermer la connexion
            await temp_connector.disconnect()
            
            logger.info(f"Découvert {len(models)} modèles Ollama")
            return models
            
        except Exception as e:
            logger.error(f"Erreur lors de la découverte des modèles Ollama: {e}")
            return []
    
    def _get_model_capabilities(self, model_name: str) -> List[Capability]:
        """
        Déterminer les capacités d'un modèle basé sur son nom
        
        Args:
            model_name: Nom du modèle
            
        Returns:
            List[Capability]: Liste des capacités
        """
        # Nettoyer le nom du modèle
        base_name = model_name.split(':')[0].lower()
        
        # Chercher dans le mapping
        for pattern, capabilities in self.model_capabilities.items():
            if pattern in base_name:
                return capabilities
        
        # Capacités par défaut si le modèle n'est pas reconnu
        return [
            Capability.TEXT_GENERATION,
            Capability.ANALYSIS,
            Capability.QUESTION_ANSWERING
        ]
    
    def _get_model_priority(self, model_name: str, model_size: int) -> int:
        """
        Déterminer la priorité d'un modèle
        
        Args:
            model_name: Nom du modèle
            model_size: Taille du modèle en bytes
            
        Returns:
            int: Priorité (1=haute, 10=basse)
        """
        # Priorité basée sur la taille (plus grand = plus prioritaire)
        if model_size > 30 * 1024 * 1024 * 1024:  # > 30GB
            return 1
        elif model_size > 10 * 1024 * 1024 * 1024:  # > 10GB
            return 2
        elif model_size > 5 * 1024 * 1024 * 1024:   # > 5GB
            return 3
        elif model_size > 1 * 1024 * 1024 * 1024:   # > 1GB
            return 4
        else:
            return 5
    
    async def create_ai_model(self, model_info: Dict[str, Any]) -> Optional[AIModel]:
        """
        Créer un objet AIModel à partir des informations d'un modèle Ollama
        
        Args:
            model_info: Informations du modèle
            
        Returns:
            AIModel: Modèle d'IA configuré
        """
        try:
            model_name = model_info.get('name', '')
            model_size = model_info.get('size', 0)
            
            # Déterminer les capacités
            capabilities = self._get_model_capabilities(model_name)
            
            # Déterminer la priorité
            priority = self._get_model_priority(model_name, model_size)
            
            # Créer le modèle
            ai_model = AIModel(
                id=f"ollama-{model_name}",
                name=f"Ollama {model_name}",
                type=ModelType.OFFLINE_CUSTOM,
                capabilities=capabilities,
                priority=priority,
                description=f"Modèle local Ollama: {model_name} ({model_size / (1024**3):.1f}GB)",
                api_endpoint=self.api_base,
                config={
                    'ollama_model_name': model_name,
                    'model_size': model_size,
                    'discovered_at': asyncio.get_event_loop().time()
                }
            )
            
            return ai_model
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du modèle {model_info.get('name', 'unknown')}: {e}")
            return None
    
    async def create_connector(self, model_name: str) -> Optional[OllamaConnector]:
        """
        Créer un connecteur pour un modèle Ollama
        
        Args:
            model_name: Nom du modèle
            
        Returns:
            OllamaConnector: Connecteur configuré
        """
        try:
            config = {
                'api_base': self.api_base,
                'model_name': model_name,
                'rate_limit_rpm': 100,
                'rate_limit_tpm': 500000
            }
            
            connector = OllamaConnector(f"ollama-{model_name}", config)
            
            # Tester la connexion
            if await connector.connect():
                return connector
            else:
                logger.warning(f"Impossible de se connecter au modèle {model_name}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la création du connecteur pour {model_name}: {e}")
            return None
    
    async def auto_discover_and_register(self, orchestrator_engine) -> List[str]:
        """
        Découvrir automatiquement et enregistrer tous les modèles Ollama
        
        Args:
            orchestrator_engine: Instance de l'orchestrateur
            
        Returns:
            List[str]: Liste des modèles enregistrés
        """
        logger.info("Démarrage de la découverte automatique des modèles Ollama")
        
        # Découvrir les modèles
        models = await self.discover_models()
        
        registered_models = []
        
        for model_info in models:
            model_name = model_info.get('name', '')
            
            try:
                # Créer le modèle d'IA
                ai_model = await self.create_ai_model(model_info)
                if not ai_model:
                    continue
                
                # Créer le connecteur
                connector = await self.create_connector(model_name)
                if not connector:
                    continue
                
                # Enregistrer dans l'orchestrateur
                orchestrator_engine.register_model(ai_model)
                orchestrator_engine.register_connector(ai_model.id, connector)
                
                registered_models.append(model_name)
                logger.info(f"Modèle Ollama enregistré: {model_name}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement du modèle {model_name}: {e}")
        
        logger.info(f"Découverte terminée: {len(registered_models)} modèles enregistrés")
        return registered_models 