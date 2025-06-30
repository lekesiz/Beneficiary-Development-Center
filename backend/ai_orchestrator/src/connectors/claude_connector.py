"""
Connecteur pour Claude (Anthropic)
"""

import asyncio
import json
from typing import Dict, List, Optional, Any

import httpx
from loguru import logger

from .base import BaseAIConnector, AIResponse


class ClaudeConnector(BaseAIConnector):
    """
    Connecteur pour l'API Claude d'Anthropic
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        super().__init__(model_id, config)
        
        # Configuration spécifique à Claude
        self.api_key = config.get('api_key')
        self.api_base = config.get('api_base', 'https://api.anthropic.com')
        self.model_name = config.get('model_name', 'claude-3-sonnet-20240229')
        self.api_version = config.get('api_version', '2023-06-01')
        
        # Limites spécifiques à Claude
        self.rate_limit_requests_per_minute = config.get('rate_limit_rpm', 50)
        self.rate_limit_tokens_per_minute = config.get('rate_limit_tpm', 100000)
        
        # Client HTTP
        self.client = None
        
        if not self.api_key:
            logger.error("Clé API Claude manquante")
            raise ValueError("Clé API Claude requise")
    
    async def connect(self) -> bool:
        """Établir la connexion avec l'API Claude"""
        try:
            # Créer le client HTTP
            self.client = httpx.AsyncClient(
                base_url=self.api_base,
                headers={
                    'x-api-key': self.api_key,
                    'anthropic-version': self.api_version,
                    'content-type': 'application/json'
                },
                timeout=httpx.Timeout(self.timeout_seconds)
            )
            
            # Tester la connexion
            health_check = await self.health_check()
            
            if health_check:
                self.is_connected = True
                logger.info(f"Connexion établie avec Claude ({self.model_name})")
                return True
            else:
                logger.error("Échec du test de connexion Claude")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Claude: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Fermer la connexion avec l'API Claude"""
        if self.client:
            await self.client.aclose()
            self.client = None
        
        self.is_connected = False
        logger.info("Connexion Claude fermée")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """Générer une réponse avec Claude"""
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion Claude non établie")
        
        try:
            # Préparer les messages pour Claude
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Paramètres de la requête
            request_data = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "messages": messages
            }
            
            # Ajouter les paramètres optionnels
            if 'system' in kwargs:
                request_data['system'] = kwargs['system']
            
            if 'stop_sequences' in kwargs:
                request_data['stop_sequences'] = kwargs['stop_sequences']
            
            logger.debug(f"Requête Claude: {json.dumps(request_data, indent=2)}")
            
            # Effectuer la requête
            response = await self.client.post(
                '/v1/messages',
                json=request_data
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            logger.debug(f"Réponse Claude: {json.dumps(response_data, indent=2)}")
            
            # Extraire le contenu de la réponse
            content = ""
            if 'content' in response_data and response_data['content']:
                # Claude retourne une liste de blocs de contenu
                for block in response_data['content']:
                    if block.get('type') == 'text':
                        content += block.get('text', '')
            
            # Calculer les tokens utilisés
            tokens_used = response_data.get('usage', {}).get('output_tokens', 0)
            input_tokens = response_data.get('usage', {}).get('input_tokens', 0)
            total_tokens = tokens_used + input_tokens
            
            # Calculer le coût (approximatif)
            cost = self._calculate_cost(input_tokens, tokens_used)
            
            # Calculer la confiance
            confidence = self._calculate_confidence(response_data)
            
            # Métadonnées
            metadata = {
                'model': response_data.get('model', self.model_name),
                'finish_reason': response_data.get('stop_reason'),
                'input_tokens': input_tokens,
                'output_tokens': tokens_used,
                'total_tokens': total_tokens,
                'request_id': response.headers.get('request-id'),
                'api_version': self.api_version
            }
            
            return AIResponse(
                content=content,
                confidence=confidence,
                tokens_used=total_tokens,
                cost=cost,
                model_info={
                    'model_name': self.model_name,
                    'provider': 'anthropic'
                },
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP Claude: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Erreur API Claude: {e.response.status_code}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération Claude: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Vérifier la santé de la connexion Claude"""
        try:
            if not self.client:
                return False
            
            # Test simple avec un prompt minimal
            test_data = {
                "model": self.model_name,
                "max_tokens": 10,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hi"
                    }
                ]
            }
            
            response = await self.client.post('/v1/messages', json=test_data)
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Health check Claude échoué: {e}")
            return False
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculer le coût approximatif de la requête
        
        Args:
            input_tokens: Nombre de tokens d'entrée
            output_tokens: Nombre de tokens de sortie
            
        Returns:
            float: Coût en USD
        """
        # Tarifs approximatifs Claude (à ajuster selon les tarifs réels)
        if 'claude-3-opus' in self.model_name:
            input_cost_per_1k = 0.015
            output_cost_per_1k = 0.075
        elif 'claude-3-sonnet' in self.model_name:
            input_cost_per_1k = 0.003
            output_cost_per_1k = 0.015
        elif 'claude-3-haiku' in self.model_name:
            input_cost_per_1k = 0.00025
            output_cost_per_1k = 0.00125
        else:
            # Tarifs par défaut
            input_cost_per_1k = 0.003
            output_cost_per_1k = 0.015
        
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def _calculate_confidence(self, response_data: Dict[str, Any]) -> float:
        """Calculer la confiance pour Claude"""
        base_confidence = 0.85  # Claude a généralement une bonne qualité
        
        # Ajustements basés sur la raison d'arrêt
        stop_reason = response_data.get('stop_reason')
        if stop_reason == 'end_turn':
            base_confidence += 0.1
        elif stop_reason == 'max_tokens':
            base_confidence -= 0.15
        elif stop_reason == 'stop_sequence':
            base_confidence += 0.05
        
        # Ajustements basés sur la longueur de la réponse
        if 'content' in response_data and response_data['content']:
            total_length = sum(
                len(block.get('text', '')) 
                for block in response_data['content'] 
                if block.get('type') == 'text'
            )
            
            if total_length < 10:
                base_confidence -= 0.2
            elif total_length > 2000:
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
        Générer une réponse en streaming avec Claude
        
        Yields:
            str: Chunks de la réponse au fur et à mesure
        """
        if not self.is_connected or not self.client:
            raise ConnectionError("Connexion Claude non établie")
        
        try:
            # Préparer les messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Paramètres de la requête avec streaming
            request_data = {
                "model": self.model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "messages": messages,
                "stream": True
            }
            
            # Ajouter les paramètres optionnels
            if 'system' in kwargs:
                request_data['system'] = kwargs['system']
            
            # Effectuer la requête streaming
            async with self.client.stream(
                'POST',
                '/v1/messages',
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
                            
                            if data.get('type') == 'content_block_delta':
                                delta = data.get('delta', {})
                                if delta.get('type') == 'text_delta':
                                    text = delta.get('text', '')
                                    if text:
                                        yield text
                                        
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"Erreur lors du streaming Claude: {e}")
            raise
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Obtenir les informations sur le modèle Claude"""
        return {
            'model_name': self.model_name,
            'provider': 'anthropic',
            'api_version': self.api_version,
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
            'languages': ['fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
            'strengths': [
                'Raisonnement complexe',
                'Analyse détaillée',
                'Sécurité et éthique',
                'Créativité',
                'Code de qualité'
            ]
        }
    
    def _get_context_length(self) -> int:
        """Obtenir la longueur du contexte selon le modèle"""
        if 'claude-3' in self.model_name:
            return 200000  # 200k tokens pour Claude 3
        else:
            return 100000  # Valeur par défaut
    
    async def analyze_prompt_safety(self, prompt: str) -> Dict[str, Any]:
        """
        Analyser la sécurité d'un prompt avant envoi
        
        Args:
            prompt: Le prompt à analyser
            
        Returns:
            Dict contenant l'analyse de sécurité
        """
        # Implémentation basique - peut être étendue
        safety_issues = []
        
        # Vérifications basiques
        if len(prompt) > 50000:
            safety_issues.append("Prompt très long, risque de timeout")
        
        # Mots-clés potentiellement problématiques
        sensitive_keywords = [
            'hack', 'exploit', 'bypass', 'jailbreak',
            'ignore instructions', 'forget previous'
        ]
        
        prompt_lower = prompt.lower()
        for keyword in sensitive_keywords:
            if keyword in prompt_lower:
                safety_issues.append(f"Mot-clé sensible détecté: {keyword}")
        
        return {
            'is_safe': len(safety_issues) == 0,
            'issues': safety_issues,
            'risk_level': 'low' if len(safety_issues) == 0 else 'medium' if len(safety_issues) <= 2 else 'high'
        }

