"""
Classe de base pour tous les connecteurs d'IA
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from loguru import logger


@dataclass
class AIResponse:
    """Réponse standardisée d'un modèle d'IA"""
    content: str
    confidence: float = 0.8
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    model_info: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.model_info is None:
            self.model_info = {}
        if self.metadata is None:
            self.metadata = {}


class BaseAIConnector(ABC):
    """
    Classe de base pour tous les connecteurs d'IA
    
    Définit l'interface commune que tous les connecteurs doivent implémenter
    """
    
    def __init__(self, model_id: str, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config
        self.is_connected = False
        self.last_request_time = None
        self.request_count = 0
        self.error_count = 0
        
        # Configuration des limites
        self.rate_limit_requests_per_minute = config.get('rate_limit_rpm', 60)
        self.rate_limit_tokens_per_minute = config.get('rate_limit_tpm', 150000)
        self.max_retries = config.get('max_retries', 3)
        self.timeout_seconds = config.get('timeout', 30)
        
        # Historique des requêtes pour le rate limiting
        self.request_history = []
        self.token_history = []
        
        logger.info(f"Connecteur {self.__class__.__name__} initialisé pour {model_id}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Établir la connexion avec le service d'IA
        
        Returns:
            bool: True si la connexion est établie, False sinon
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Fermer la connexion avec le service d'IA"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """
        Générer une réponse à partir d'un prompt
        
        Args:
            prompt: Le prompt d'entrée
            max_tokens: Nombre maximum de tokens à générer
            temperature: Température pour la génération (0.0 à 2.0)
            top_p: Paramètre top-p pour la génération
            **kwargs: Paramètres additionnels spécifiques au modèle
            
        Returns:
            AIResponse: La réponse du modèle
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Vérifier la santé de la connexion
        
        Returns:
            bool: True si le service est accessible, False sinon
        """
        pass
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> AIResponse:
        """
        Générer une réponse avec retry automatique
        
        Args:
            prompt: Le prompt d'entrée
            max_tokens: Nombre maximum de tokens à générer
            temperature: Température pour la génération
            top_p: Paramètre top-p pour la génération
            **kwargs: Paramètres additionnels
            
        Returns:
            AIResponse: La réponse du modèle
            
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Vérifier les limites de taux avant la requête
                await self._check_rate_limits(max_tokens)
                
                # Effectuer la requête
                response = await asyncio.wait_for(
                    self.generate(prompt, max_tokens, temperature, top_p, **kwargs),
                    timeout=self.timeout_seconds
                )
                
                # Mettre à jour les statistiques
                self._update_request_stats(success=True, tokens_used=response.tokens_used)
                
                return response
                
            except asyncio.TimeoutError as e:
                last_exception = e
                logger.warning(f"Timeout lors de la tentative {attempt + 1} pour {self.model_id}")
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Erreur lors de la tentative {attempt + 1} pour {self.model_id}: {e}")
                
                # Mettre à jour les statistiques d'erreur
                self._update_request_stats(success=False)
                
                # Attendre avant le retry (backoff exponentiel)
                if attempt < self.max_retries:
                    wait_time = (2 ** attempt) * 1.0  # 1s, 2s, 4s, etc.
                    await asyncio.sleep(wait_time)
        
        # Toutes les tentatives ont échoué
        logger.error(f"Toutes les tentatives ont échoué pour {self.model_id}")
        raise last_exception
    
    async def _check_rate_limits(self, tokens_needed: int = 0) -> None:
        """
        Vérifier et respecter les limites de taux
        
        Args:
            tokens_needed: Nombre de tokens estimés pour la requête
        """
        current_time = datetime.utcnow()
        
        # Nettoyer l'historique (garder seulement la dernière minute)
        cutoff_time = current_time.timestamp() - 60
        self.request_history = [t for t in self.request_history if t > cutoff_time]
        self.token_history = [(t, tokens) for t, tokens in self.token_history if t > cutoff_time]
        
        # Vérifier la limite de requêtes par minute
        if len(self.request_history) >= self.rate_limit_requests_per_minute:
            wait_time = 60 - (current_time.timestamp() - min(self.request_history))
            if wait_time > 0:
                logger.info(f"Rate limit atteint pour {self.model_id}, attente de {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        # Vérifier la limite de tokens par minute
        total_tokens_last_minute = sum(tokens for _, tokens in self.token_history)
        if total_tokens_last_minute + tokens_needed > self.rate_limit_tokens_per_minute:
            # Calculer le temps d'attente nécessaire
            oldest_token_time = min(t for t, _ in self.token_history) if self.token_history else current_time.timestamp()
            wait_time = 60 - (current_time.timestamp() - oldest_token_time)
            if wait_time > 0:
                logger.info(f"Limite de tokens atteinte pour {self.model_id}, attente de {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
    
    def _update_request_stats(self, success: bool, tokens_used: int = 0) -> None:
        """
        Mettre à jour les statistiques de requêtes
        
        Args:
            success: Si la requête a réussi
            tokens_used: Nombre de tokens utilisés
        """
        current_time = datetime.utcnow().timestamp()
        
        self.request_count += 1
        self.last_request_time = current_time
        
        if success:
            self.request_history.append(current_time)
            if tokens_used > 0:
                self.token_history.append((current_time, tokens_used))
        else:
            self.error_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtenir les statistiques du connecteur
        
        Returns:
            Dict contenant les statistiques
        """
        current_time = datetime.utcnow().timestamp()
        
        # Calculer les requêtes de la dernière minute
        recent_requests = len([t for t in self.request_history if current_time - t <= 60])
        recent_tokens = sum(tokens for t, tokens in self.token_history if current_time - t <= 60)
        
        success_rate = 0.0
        if self.request_count > 0:
            success_rate = ((self.request_count - self.error_count) / self.request_count) * 100
        
        return {
            'model_id': self.model_id,
            'is_connected': self.is_connected,
            'total_requests': self.request_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'last_request_time': self.last_request_time,
            'requests_last_minute': recent_requests,
            'tokens_last_minute': recent_tokens,
            'rate_limit_rpm': self.rate_limit_requests_per_minute,
            'rate_limit_tpm': self.rate_limit_tokens_per_minute
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Tester la connexion avec un prompt simple
        
        Returns:
            Dict contenant les résultats du test
        """
        test_prompt = "Répondez simplement 'Test réussi' pour confirmer que la connexion fonctionne."
        
        try:
            start_time = datetime.utcnow()
            response = await self.generate_with_retry(
                prompt=test_prompt,
                max_tokens=50,
                temperature=0.1
            )
            end_time = datetime.utcnow()
            
            response_time = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'response_time': response_time,
                'response_content': response.content[:100],  # Premiers 100 caractères
                'tokens_used': response.tokens_used,
                'confidence': response.confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response_time': None
            }
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimer le nombre de tokens dans un texte
        
        Args:
            text: Le texte à analyser
            
        Returns:
            int: Estimation du nombre de tokens
        """
        # Estimation approximative : 1 token ≈ 4 caractères pour l'anglais
        # Ajustement pour le français : 1 token ≈ 3.5 caractères
        return max(1, len(text) // 4)
    
    def _calculate_confidence(self, response_data: Dict[str, Any]) -> float:
        """
        Calculer un score de confiance basé sur les données de réponse
        
        Args:
            response_data: Données de réponse du modèle
            
        Returns:
            float: Score de confiance entre 0.0 et 1.0
        """
        # Implémentation par défaut - peut être surchargée par les connecteurs spécifiques
        base_confidence = 0.8
        
        # Ajustements basés sur la longueur de la réponse
        content_length = len(response_data.get('content', ''))
        if content_length < 10:
            base_confidence -= 0.2
        elif content_length > 1000:
            base_confidence += 0.1
        
        # Ajustements basés sur les métadonnées du modèle
        if 'finish_reason' in response_data:
            if response_data['finish_reason'] == 'stop':
                base_confidence += 0.1
            elif response_data['finish_reason'] == 'length':
                base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    async def __aenter__(self):
        """Support pour async context manager"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Support pour async context manager"""
        await self.disconnect()

