"""
Connecteur pour OpenAI (ChatGPT, GPT-4, etc.)
"""

import asyncio
import json
from typing import Dict, List, Optional, Any

import httpx
from loguru import logger

from .base import BaseAIConnector, AIResponse


class OpenAIConnector(BaseAIConnector):
    """
    Connecteur pour l'API OpenAI
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Configuration spécifique à OpenAI
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base', 'https://api.openai.com/v1')
        self.model_name = config.get('model_name', 'gpt-4')
        self.organization = config.get('organization')
        
        # Limites spécifiques à OpenAI
        self.rate_limit_requests_per_minute = config.get('rate_limit_rpm', 500)
        self.rate_limit_tokens_per_minute = config.get('rate_limit_tpm', 150000)
        
        # Client HTTP
        self.client = None
        
        if not self.api_key:
            logger.error("Clé API OpenAI manquante")
            raise ValueError("Clé API OpenAI requise")
    
    async def connect(self) -> bool:
        """Établir la connexion avec l'API OpenAI"""
        try:
            # Préparer les headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            if self.organization:
                headers['OpenAI-Organization'] = self.organization
            
            # Créer le client HTTP
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                headers=headers,
                timeout=httpx.Timeout(self.timeout_seconds)
            )
            
            # Tester la connexion
            health_check = await self.health_check()
            
            if health_check:
                self.is_connected = True
                logger.info(f"Connexion établie avec OpenAI ({self.model_name})")
                return True
            else:
                logger.error("Échec du test de connexion OpenAI")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à OpenAI: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Fermer la connexion avec l'API OpenAI"""
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.is_connected = False
        logger.info("Connexion OpenAI fermée")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """Générer une réponse avec OpenAI"""
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion OpenAI non établie")
        
        try:
            # Préparer les messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Ajouter un message système si fourni
            if 'system_message' in kwargs:
                messages.insert(0, {
                    "role": "system",
                    "content": kwargs['system_message']
                })
            
            # Paramètres de la requête
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Paramètres optionnels
            if 'frequency_penalty' in kwargs:
                request_data['frequency_penalty'] = kwargs['frequency_penalty']
            
            if 'presence_penalty' in kwargs:
                request_data['presence_penalty'] = kwargs['presence_penalty']
            
            if 'stop' in kwargs:
                request_data['stop'] = kwargs['stop']
            
            if 'functions' in kwargs:
                request_data['functions'] = kwargs['functions']
                if 'function_call' in kwargs:
                    request_data['function_call'] = kwargs['function_call']
            
            logger.debug(f"Requête OpenAI: {json.dumps(request_data, indent=2)}")
            
            # Effectuer la requête
            response = await self.client.post(
                '/chat/completions',
                json=request_data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Réponse OpenAI: {json.dumps(response_data, indent=2)}")
            
            # Extraire le contenu de la réponse
            choice = response_data['choices'][0]
            message = choice['message']
            
            content = message.get('content', '')
            
            # Gérer les appels de fonction
            function_call = message.get('function_call')
            if function_call:
                content = json.dumps(function_call)
            
            # Calculer les tokens utilisés
            usage = response_data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            # Calculer le coût
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            
            # Calculer la confiance
            confidence = self._calculate_confidence(response_data)
            
            # Métadonnées
            metadata = {
                'model': response_data.get('model', self.model_name),
                'finish_reason': choice.get('finish_reason'),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'request_id': response.headers.get('x-request-id'),
                'function_call': function_call is not None
            }
            
            return AIResponse(
                content=content,
                confidence=confidence,
                tokens_used=total_tokens,
                cost=cost,
                model_info={
                    'model_name': self.model_name,
                    'provider': 'openai'
                },
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP OpenAI: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erreur API OpenAI: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Vérifier la santé de la connexion OpenAI"""
        try:
            if not self.client:
                return False
            
            # Tester avec l'endpoint des modèles
            response = await self.client.get('/models')
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Health check OpenAI échoué: {e}")
            return False
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculer le coût approximatif de la requête
        
        Args:
            prompt_tokens: Nombre de tokens du prompt
            completion_tokens: Nombre de tokens de la completion
            
        Returns:
            float: Coût en USD
        """
        # Tarifs approximatifs OpenAI (à ajuster selon les tarifs réels)
        if 'gpt-4' in self.model_name.lower():
            if 'turbo' in self.model_name.lower():
                prompt_cost_per_1k = 0.001
                completion_cost_per_1k = 0.002
            else:
                prompt_cost_per_1k = 0.03
                completion_cost_per_1k = 0.06
        elif 'gpt-3.5' in self.model_name.lower():
            prompt_cost_per_1k = 0.0005
            completion_cost_per_1k = 0.0015
        else:
            # Tarifs par défaut (GPT-3.5)
            prompt_cost_per_1k = 0.0005
            completion_cost_per_1k = 0.0015
        
        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000) * completion_cost_per_1k
        
        return prompt_cost + completion_cost
    
    def _calculate_confidence(self, response_data: Dict[str, Any]) -> float:
        """Calculer la confiance pour OpenAI"""
        base_confidence = 0.8
        
        choice = response_data['choices'][0]
        
        # Ajustements basés sur la raison d'arrêt
        finish_reason = choice.get('finish_reason')
        if finish_reason == 'stop':
            base_confidence += 0.1
        elif finish_reason == 'length':
            base_confidence -= 0.15
        elif finish_reason == 'function_call':
            base_confidence += 0.05
        elif finish_reason == 'content_filter':
            base_confidence -= 0.3
        
        # Ajustements basés sur la longueur de la réponse
        content = choice.get('message', {}).get('content', '')
        if len(content) < 10:
            base_confidence -= 0.2
        elif len(content) > 2000:
            base_confidence += 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    async def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ):
        """
        Générer une réponse en streaming avec OpenAI
        
        Yields:
            str: Chunks de la réponse au fur et à mesure
        """
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion OpenAI non établie")
        
        try:
            # Préparer les messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            if 'system_message' in kwargs:
                messages.insert(0, {
                    "role": "system",
                    "content": kwargs['system_message']
                })
            
            # Paramètres de la requête avec streaming
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": True
            }
            
            # Effectuer la requête streaming
            async with self.client.stream(
                'POST',
                '/chat/completions',
                json=request_data
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data_str = line[6:]  # Enlever 'data: '
                        
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content')
                                
                                if content:
                                    yield content
                                    
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Erreur lors du streaming OpenAI: {e}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Obtenir la liste des modèles disponibles"""
        try:
            if not self.client:
                return []
            
            response = await self.client.get('/models')
            response.raise_for_status()
            
            models_data = response.json()
            return models_data.get('data', [])
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le modèle OpenAI"""
        return {
            'model_name': self.model_name,
            'provider': 'openai',
            'context_length': self._get_context_length(),
            'capabilities': [
                'text_generation',
                'analysis',
                'creative_writing',
                'code_generation',
                'question_answering',
                'summarization',
                'translation',
                'function_calling'
            ],
            'languages': ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar'],
            'strengths': [
                'Polyvalence',
                'Créativité',
                'Code de qualité',
                'Raisonnement logique',
                'Multilingue'
            ]
        }
    
    def _get_context_length(self) -> int:
        """Obtenir la longueur du contexte selon le modèle"""
        if 'gpt-4-turbo' in self.model_name.lower():
            return 128000
        elif 'gpt-4' in self.model_name.lower():
            return 8192
        elif 'gpt-3.5-turbo-16k' in self.model_name.lower():
            return 16384
        elif 'gpt-3.5' in self.model_name.lower():
            return 4096
        else:
            return 4096  # Valeur par défaut
    
    async def create_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Créer un embedding pour un texte
        
        Args:
            text: Le texte à encoder
            model: Le modèle d'embedding à utiliser
            
        Returns:
            List[float]: Le vecteur d'embedding
        """
        try:
            if not self.client:
                raise ConnectionError("Connexion OpenAI non établie")
            
            request_data = {
                "input": text,
                "model": model
            }
            
            response = await self.client.post('/embeddings', json=request_data)
            response.raise_for_status()
            
            response_data = response.json()
            return response_data['data'][0]['embedding']
            
        except Exception as e:
            logger.error(f"Erreur lors de la création d'embedding: {e}")
            raise
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Modérer du contenu avec l'API de modération OpenAI
        
        Args:
            text: Le texte à modérer
            
        Returns:
            Dict contenant les résultats de modération
        """
        try:
            if not self.client:
                raise ConnectionError("Connexion OpenAI non établie")
            
            request_data = {
                "input": text
            }
            
            response = await self.client.post('/moderations', json=request_data)
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data['results'][0]
            
            return {
                'flagged': result['flagged'],
                'categories': result['categories'],
                'category_scores': result['category_scores']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la modération: {e}")
            return {'flagged': False, 'categories': {}, 'category_scores': {}}

