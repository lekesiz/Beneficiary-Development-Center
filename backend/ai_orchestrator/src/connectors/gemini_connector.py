"""
Connecteur pour Google Gemini
"""

import asyncio
import json
from typing import Dict, List, Optional, Any

import httpx
from loguru import logger

from .base import BaseAIConnector, AIResponse


class GeminiConnector(BaseAIConnector):
    """
    Connecteur pour l'API Google Gemini
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Configuration spécifique à Gemini
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base', 'https://generativelanguage.googleapis.com/v1beta')
        self.model_name = config.get('model_name', 'gemini-1.5-flash')
        
        # Limites spécifiques à Gemini
        self.rate_limit_requests_per_minute = config.get('rate_limit_rpm', 300)
        self.rate_limit_tokens_per_minute = config.get('rate_limit_tpm', 100000)
        
        # Client HTTP
        self.client = None
        
        if not self.api_key:
            logger.error("Clé API Gemini manquante")
            raise ValueError("Clé API Gemini requise")
    
    async def connect(self) -> bool:
        """Établir la connexion avec l'API Gemini"""
        try:
            # Créer le client HTTP
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                timeout=httpx.Timeout(self.timeout_seconds)
            )
            
            # Tester la connexion
            health_check = await self.health_check()
            
            if health_check:
                self.is_connected = True
                logger.info(f"Connexion établie avec Gemini ({self.model_name})")
                return True
            else:
                logger.error("Échec du test de connexion Gemini")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Gemini: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Fermer la connexion avec l'API Gemini"""
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.is_connected = False
        logger.info("Connexion Gemini fermée")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """Générer une réponse avec Gemini"""
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion Gemini non établie")
        
        try:
            # Préparer le contenu
            contents = [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
            
            # Paramètres de la requête
            request_data = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature,
                    "topP": top_p
                }
            }
            
            # Paramètres optionnels
            if 'system_instruction' in kwargs:
                request_data["systemInstruction"] = {
                    "parts": [
                        {
                            "text": kwargs['system_instruction']
                        }
                    ]
                }
            
            if 'safety_settings' in kwargs:
                request_data["safetySettings"] = kwargs['safety_settings']
            
            logger.debug(f"Requête Gemini: {json.dumps(request_data, indent=2)}")
            
            # Effectuer la requête
            response = await self.client.post(
                f'/models/{self.model_name}:generateContent',
                params={'key': self.api_key},
                json=request_data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Réponse Gemini: {json.dumps(response_data, indent=2)}")
            
            # Extraire le contenu de la réponse
            content = ""
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and candidate['content']['parts']:
                    content = candidate['content']['parts'][0].get('text', '')
            
            # Calculer les tokens utilisés
            usage_metadata = response_data.get('usageMetadata', {})
            prompt_tokens = usage_metadata.get('promptTokenCount', 0)
            response_tokens = usage_metadata.get('candidatesTokenCount', 0)
            total_tokens = usage_metadata.get('totalTokenCount', prompt_tokens + response_tokens)
            
            # Calculer le coût
            cost = self._calculate_cost(prompt_tokens, response_tokens)
            
            # Calculer la confiance
            confidence = self._calculate_confidence(response_data)
            
            # Métadonnées
            metadata = {
                'model': self.model_name,
                'finish_reason': response_data.get('candidates', [{}])[0].get('finishReason'),
                'prompt_tokens': prompt_tokens,
                'response_tokens': response_tokens,
                'total_tokens': total_tokens,
                'safety_ratings': response_data.get('candidates', [{}])[0].get('safetyRatings', [])
            }
            
            return AIResponse(
                content=content,
                confidence=confidence,
                tokens_used=total_tokens,
                cost=cost,
                model_info={
                    'model_name': self.model_name,
                    'provider': 'google',
                    'type': 'gemini'
                },
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP Gemini: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erreur API Gemini: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération Gemini: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Vérifier la santé de la connexion Gemini"""
        try:
            if not self.client:
                return False
            
            # Test simple avec un prompt minimal
            test_data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Hi"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 5
                }
            }
            
            response = await self.client.post(
                f'/models/{self.model_name}:generateContent',
                params={'key': self.api_key},
                json=test_data
            )
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Health check Gemini échoué: {e}")
            return False
    
    def _calculate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Calculer le coût pour Gemini"""
        # Tarifs Gemini (approximatifs, à ajuster selon les tarifs actuels)
        # Input: $0.00025 / 1K tokens
        # Output: $0.0005 / 1K tokens
        
        input_cost = (prompt_tokens / 1000) * 0.00025
        output_cost = (response_tokens / 1000) * 0.0005
        
        return input_cost + output_cost
    
    def _calculate_confidence(self, response_data: Dict[str, Any]) -> float:
        """Calculer la confiance basée sur la réponse"""
        # Pour Gemini, on peut utiliser les safety ratings comme indicateur
        candidates = response_data.get('candidates', [])
        if not candidates:
            return 0.5
        
        candidate = candidates[0]
        safety_ratings = candidate.get('safetyRatings', [])
        
        # Plus de safety ratings = plus de confiance
        if safety_ratings:
            # Vérifier si tous les ratings sont "HARM_CATEGORY_UNSPECIFIED"
            all_safe = all(
                rating.get('category') == 'HARM_CATEGORY_UNSPECIFIED' 
                for rating in safety_ratings
            )
            return 0.9 if all_safe else 0.7
        
        return 0.8  # Confiance par défaut
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le modèle"""
        try:
            if not self.client:
                return {}
            
            response = await self.client.get(
                f'/models/{self.model_name}',
                params={'key': self.api_key}
            )
            response.raise_for_status()
            
            model_info = response.json()
            
            return {
                'name': model_info.get('name', self.model_name),
                'display_name': model_info.get('displayName', ''),
                'description': model_info.get('description', ''),
                'version': model_info.get('version', ''),
                'supported_generation_methods': model_info.get('supportedGenerationMethods', []),
                'temperature': model_info.get('temperature', {}),
                'top_p': model_info.get('topP', {}),
                'top_k': model_info.get('topK', {})
            }
            
        except Exception as e:
            logger.warning(f"Impossible d'obtenir les infos du modèle {self.model_name}: {e}")
            return {}
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """Lister tous les modèles disponibles"""
        try:
            if not self.client:
                return []
            
            response = await self.client.get(
                '/models',
                params={'key': self.api_key}
            )
            response.raise_for_status()
            
            models_data = response.json()
            models = models_data.get('models', [])
            
            return [
                {
                    'name': model.get('name', ''),
                    'display_name': model.get('displayName', ''),
                    'description': model.get('description', ''),
                    'supported_generation_methods': model.get('supportedGenerationMethods', [])
                }
                for model in models
            ]
            
        except Exception as e:
            logger.warning(f"Impossible de lister les modèles Gemini: {e}")
            return []
    
    async def create_embedding(self, text: str) -> List[float]:
        """Créer des embeddings avec Gemini"""
        try:
            if not self.client:
                raise ConnectionError("Connexion Gemini non établie")
            
            request_data = {
                "model": "models/embedding-001",
                "text": text
            }
            
            response = await self.client.post(
                '/models/embedding-001:embedText',
                params={'key': self.api_key},
                json=request_data
            )
            response.raise_for_status()
            
            response_data = response.json()
            embedding = response_data.get('embedding', {}).get('values', [])
            
            return embedding
            
        except Exception as e:
            logger.error(f"Erreur lors de la création d'embedding Gemini: {e}")
            raise 