"""
Connecteur pour Ollama (modèles locaux)
"""

import asyncio
import json
from typing import Dict, List, Optional, Any

import httpx
from loguru import logger

from .base import BaseAIConnector, AIResponse


class OllamaConnector(BaseAIConnector):
    """
    Connecteur pour l'API Ollama (modèles locaux)
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Configuration spécifique à Ollama
        self.api_base = config.get('api_base', 'http://localhost:11434')
        self.model_name = config.get('model_name', model_id)
        self.api_key = config.get('api_key')  # Optionnel pour Ollama
        
        # Limites spécifiques à Ollama (plus élevées car local)
        self.rate_limit_requests_per_minute = config.get('rate_limit_rpm', 100)
        self.rate_limit_tokens_per_minute = config.get('rate_limit_tpm', 500000)
        
        # Client HTTP
        self.client = None
        
        logger.info(f"OllamaConnector initialisé pour {model_id} ({self.model_name})")
    
    async def connect(self) -> bool:
        """Établir la connexion avec l'API Ollama"""
        try:
            # Créer le client HTTP
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                headers=headers,
                timeout=httpx.Timeout(self.timeout_seconds)
            )
            
            # Tester la connexion
            health_check = await self.health_check()
            
            if health_check:
                self.is_connected = True
                logger.info(f"Connexion établie avec Ollama ({self.model_name})")
                return True
            else:
                logger.error("Échec du test de connexion Ollama")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Ollama: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Fermer la connexion avec l'API Ollama"""
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.is_connected = False
        logger.info("Connexion Ollama fermée")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """Générer une réponse avec Ollama"""
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion Ollama non établie")
        
        try:
            # Préparer la requête pour Ollama
            request_data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            }
            
            # Ajouter les paramètres optionnels
            if 'system' in kwargs:
                request_data['system'] = kwargs['system']
            
            if 'stop' in kwargs:
                request_data['stop'] = kwargs['stop']
            
            logger.debug(f"Requête Ollama: {json.dumps(request_data, indent=2)}")
            
            # Effectuer la requête
            response = await self.client.post(
                '/api/generate',
                json=request_data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Réponse Ollama: {json.dumps(response_data, indent=2)}")
            
            # Extraire le contenu de la réponse
            content = response_data.get('response', '')
            
            # Calculer les tokens utilisés
            tokens_used = response_data.get('eval_count', 0)
            prompt_tokens = response_data.get('prompt_eval_count', 0)
            total_tokens = tokens_used + prompt_tokens
            
            # Calculer le coût (0 pour les modèles locaux)
            cost = 0.0
            
            # Calculer la confiance
            confidence = self._calculate_confidence(response_data)
            
            # Métadonnées
            metadata = {
                'model': response_data.get('model', self.model_name),
                'done': response_data.get('done', True),
                'prompt_tokens': prompt_tokens,
                'response_tokens': tokens_used,
                'total_tokens': total_tokens,
                'total_duration': response_data.get('total_duration', 0),
                'load_duration': response_data.get('load_duration', 0),
                'prompt_eval_duration': response_data.get('prompt_eval_duration', 0),
                'eval_duration': response_data.get('eval_duration', 0)
            }
            
            return AIResponse(
                content=content,
                confidence=confidence,
                tokens_used=total_tokens,
                cost=cost,
                model_info={
                    'model_name': self.model_name,
                    'provider': 'ollama',
                    'type': 'local'
                },
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP Ollama: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erreur API Ollama: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération Ollama: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Vérifier la santé de la connexion Ollama"""
        try:
            if not self.client:
                return False
            
            # Test simple avec l'endpoint /api/tags
            response = await self.client.get('/api/tags')
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Health check Ollama échoué: {e}")
            return False
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculer le coût (0 pour les modèles locaux)"""
        return 0.0  # Modèles locaux = pas de coût
    
    def _calculate_confidence(self, response_data: Dict[str, Any]) -> float:
        """Calculer la confiance basée sur la réponse"""
        # Pour Ollama, on peut utiliser la durée d'évaluation comme indicateur
        eval_duration = response_data.get('eval_duration', 0)
        total_duration = response_data.get('total_duration', 1)
        
        if total_duration > 0:
            # Plus rapide = plus confiant (dans une certaine limite)
            speed_ratio = min(eval_duration / total_duration, 1.0)
            return 0.7 + (speed_ratio * 0.3)  # Base 0.7 + bonus jusqu'à 1.0
        
        return 0.8  # Confiance par défaut
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le modèle"""
        try:
            if not self.client:
                return {}
            
            response = await self.client.get(f'/api/show', params={'name': self.model_name})
            response.raise_for_status()
            
            model_info = response.json()
            
            return {
                'name': model_info.get('name', self.model_name),
                'model': model_info.get('model', ''),
                'size': model_info.get('size', 0),
                'modified_at': model_info.get('modified_at', ''),
                'parameters': model_info.get('parameter_size', ''),
                'format': model_info.get('format', ''),
                'family': model_info.get('family', ''),
                'license': model_info.get('license', '')
            }
            
        except Exception as e:
            logger.warning(f"Impossible d'obtenir les infos du modèle {self.model_name}: {e}")
            return {}
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """Lister tous les modèles disponibles"""
        try:
            if not self.client:
                return []
            
            response = await self.client.get('/api/tags')
            response.raise_for_status()
            
            models_data = response.json()
            models = models_data.get('models', [])
            
            return [
                {
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'modified_at': model.get('modified_at', ''),
                    'digest': model.get('digest', '')
                }
                for model in models
            ]
            
        except Exception as e:
            logger.warning(f"Impossible de lister les modèles Ollama: {e}")
            return [] 