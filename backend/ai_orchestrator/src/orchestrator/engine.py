"""
Moteur d'orchestration principal
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID
import logging

from loguru import logger

from ..models.task import Task, TaskStatus, TaskType, TaskResult, ValidationResult
from ..models.ai_model import AIModel, ModelStatus
from .task_manager import TaskManager
from .decision_engine import DecisionEngine
from ..connectors.base import BaseAIConnector
from ..utils.metrics import MetricsCollector
from ..utils.config import Config


class OrchestratorEngine:
    """
    Moteur principal d'orchestration des IA
    
    Responsabilités:
    - Coordination des tâches entre les différents modèles d'IA
    - Gestion du cycle de vie des tâches
    - Validation croisée des résultats
    - Prise de décision basée sur le consensus
    - Monitoring et métriques
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.task_manager = TaskManager(config)
        self.decision_engine = DecisionEngine(config)
        self.metrics = MetricsCollector()
        
        # Connecteurs vers les modèles d'IA
        self.connectors: Dict[str, BaseAIConnector] = {}
        self.models: Dict[str, AIModel] = {}
        
        # État du système
        self.is_running = False
        self.active_tasks: Dict[UUID, Task] = {}
        self.task_queue = asyncio.Queue()
        
        # Callbacks pour les événements
        self.event_callbacks: Dict[str, List[Callable]] = {
            'task_created': [],
            'task_started': [],
            'task_completed': [],
            'task_failed': [],
            'model_status_changed': []
        }
        
        logger.info("OrchestratorEngine initialisé")
    
    async def start(self) -> None:
        """Démarrer le moteur d'orchestration"""
        if self.is_running:
            logger.warning("Le moteur est déjà en cours d'exécution")
            return
        
        self.is_running = True
        logger.info("Démarrage du moteur d'orchestration")
        
        # Démarrer les tâches de fond
        await asyncio.gather(
            self._task_processor(),
            self._health_monitor(),
            self._metrics_collector()
        )
    
    async def stop(self) -> None:
        """Arrêter le moteur d'orchestration"""
        logger.info("Arrêt du moteur d'orchestration")
        self.is_running = False
        
        # Attendre que les tâches actives se terminent
        if self.active_tasks:
            logger.info(f"Attente de la fin de {len(self.active_tasks)} tâches actives")
            await asyncio.gather(*[
                self._wait_for_task_completion(task_id) 
                for task_id in list(self.active_tasks.keys())
            ], return_exceptions=True)
    
    def register_connector(self, model_id: str, connector: BaseAIConnector) -> None:
        """Enregistrer un connecteur pour un modèle d'IA"""
        self.connectors[model_id] = connector
        logger.info(f"Connecteur enregistré pour le modèle {model_id}")
    
    def register_model(self, model: AIModel) -> None:
        """Enregistrer un modèle d'IA"""
        self.models[model.id] = model
        logger.info(f"Modèle {model.name} ({model.id}) enregistré")
        
        # Déclencher l'événement
        self._trigger_event('model_status_changed', model=model)
    
    def add_event_callback(self, event: str, callback: Callable) -> None:
        """Ajouter un callback pour un événement"""
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
    
    def _trigger_event(self, event: str, **kwargs) -> None:
        """Déclencher un événement"""
        for callback in self.event_callbacks.get(event, []):
            try:
                callback(**kwargs)
            except Exception as e:
                logger.error(f"Erreur dans le callback {callback}: {e}")
    
    async def submit_task(self, task: Task) -> UUID:
        """Soumettre une nouvelle tâche"""
        logger.info(f"Nouvelle tâche soumise: {task.title} (ID: {task.id})")
        
        # Valider la tâche
        if not self._validate_task(task):
            raise ValueError("Tâche invalide")
        
        # Ajouter à la queue
        await self.task_queue.put(task)
        self._trigger_event('task_created', task=task)
        
        return task.id
    
    async def get_task_status(self, task_id: UUID) -> Optional[Task]:
        """Obtenir le statut d'une tâche"""
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Chercher dans l'historique via le task manager
        return await self.task_manager.get_task(task_id)
    
    async def cancel_task(self, task_id: UUID) -> bool:
        """Annuler une tâche"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Tâche {task_id} annulée")
            self._trigger_event('task_failed', task=task, reason="Cancelled by user")
            
            # Sauvegarder
            await self.task_manager.save_task(task)
            del self.active_tasks[task_id]
            
            return True
        
        return False
    
    def _validate_task(self, task: Task) -> bool:
        """Valider une tâche avant soumission"""
        # Vérifications de base
        if not task.title or not task.description:
            logger.error("Tâche invalide: titre ou description manquant")
            return False
        
        # Vérifier que des modèles appropriés sont disponibles
        suitable_models = self._find_suitable_models(task)
        if not suitable_models:
            logger.error(f"Aucun modèle approprié trouvé pour la tâche {task.type}")
            return False
        
        return True
    
    def _find_suitable_models(self, task: Task) -> List[AIModel]:
        """Trouver les modèles appropriés pour une tâche"""
        suitable_models = []
        
        for model in self.models.values():
            if model.is_suitable_for_task(task.type.value):
                # Vérifier les préférences et exclusions
                if task.preferred_models and model.id not in task.preferred_models:
                    continue
                if task.excluded_models and model.id in task.excluded_models:
                    continue
                
                suitable_models.append(model)
        
        # Trier par priorité et efficacité
        suitable_models.sort(key=lambda m: (m.priority, -m.efficiency_score))
        
        return suitable_models
    
    async def _task_processor(self) -> None:
        """Processeur principal des tâches"""
        logger.info("Processeur de tâches démarré")
        
        while self.is_running:
            try:
                # Attendre une nouvelle tâche avec timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Traiter la tâche de manière asynchrone
                asyncio.create_task(self._process_task(task))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erreur dans le processeur de tâches: {e}")
    
    async def _process_task(self, task: Task) -> None:
        """Traiter une tâche individuelle"""
        task_id = task.id
        self.active_tasks[task_id] = task
        
        try:
            logger.info(f"Début du traitement de la tâche {task_id}")
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            
            self._trigger_event('task_started', task=task)
            
            # Trouver les modèles appropriés
            suitable_models = self._find_suitable_models(task)
            if not suitable_models:
                raise Exception("Aucun modèle approprié disponible")
            
            # Sélectionner les modèles à utiliser
            selected_models = self._select_models_for_task(task, suitable_models)
            task.assigned_models = [m.id for m in selected_models]
            
            logger.info(f"Modèles sélectionnés pour la tâche {task_id}: {task.assigned_models}")
            
            # Exécuter la tâche sur les modèles sélectionnés
            results = await self._execute_task_on_models(task, selected_models)
            
            # Ajouter les résultats à la tâche
            for result in results:
                task.add_result(result)
            
            # Validation croisée si requise
            if task.require_validation and len(results) > 1:
                validation = await self.decision_engine.validate_results(task, results)
                task.set_validation(validation)
                
                if not validation.is_valid:
                    # Retry si possible
                    if task.can_retry():
                        logger.warning(f"Validation échouée pour la tâche {task_id}, retry")
                        task.prepare_retry()
                        await self.task_queue.put(task)
                        return
                    else:
                        raise Exception("Validation échouée et plus de retry possible")
            else:
                # Pas de validation requise, prendre le meilleur résultat
                if results:
                    best_result = max(results, key=lambda r: r.confidence)
                    task.final_result = best_result.content
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
            
            logger.info(f"Tâche {task_id} terminée avec succès")
            self._trigger_event('task_completed', task=task)
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la tâche {task_id}: {e}")
            task.mark_failed(str(e))
            self._trigger_event('task_failed', task=task, error=str(e))
        
        finally:
            # Sauvegarder la tâche
            await self.task_manager.save_task(task)
            
            # Nettoyer
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def _select_models_for_task(self, task: Task, suitable_models: List[AIModel]) -> List[AIModel]:
        """Sélectionner les modèles à utiliser pour une tâche"""
        # Configuration par défaut
        max_models = self.config.get('orchestrator.max_models_per_task', 3)
        min_models = self.config.get('orchestrator.min_models_per_task', 1)
        
        # Ajuster selon la priorité de la tâche
        if task.priority.value == 'critical':
            max_models = min(max_models + 2, len(suitable_models))
        elif task.priority.value == 'low':
            max_models = max(1, max_models - 1)
        
        # Sélectionner les meilleurs modèles
        selected = suitable_models[:max_models]
        
        # S'assurer d'avoir au moins le minimum requis
        if len(selected) < min_models:
            logger.warning(f"Seulement {len(selected)} modèles disponibles, minimum requis: {min_models}")
        
        return selected
    
    async def _execute_task_on_models(self, task: Task, models: List[AIModel]) -> List[TaskResult]:
        """Exécuter une tâche sur plusieurs modèles en parallèle"""
        tasks = []
        
        for model in models:
            if model.id in self.connectors:
                connector = self.connectors[model.id]
                tasks.append(self._execute_on_single_model(task, model, connector))
        
        # Exécuter en parallèle avec timeout
        timeout = task.timeout_seconds
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les résultats valides
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, TaskResult):
                valid_results.append(result)
                # Mettre à jour les métriques du modèle
                models[i].update_metrics(
                    success=True,
                    response_time=result.execution_time,
                    tokens_used=result.tokens_used or 0,
                    cost=result.cost or 0.0,
                    confidence=result.confidence
                )
            else:
                # Erreur
                logger.error(f"Erreur avec le modèle {models[i].id}: {result}")
                models[i].update_metrics(success=False, response_time=timeout)
        
        return valid_results
    
    async def _execute_on_single_model(self, task: Task, model: AIModel, connector: BaseAIConnector) -> TaskResult:
        """Exécuter une tâche sur un seul modèle"""
        start_time = datetime.utcnow()
        
        try:
            # Préparer le prompt
            prompt = self._prepare_prompt_for_model(task, model)
            
            # Appeler le modèle
            response = await connector.generate(
                prompt=prompt,
                max_tokens=model.max_tokens,
                temperature=model.temperature,
                top_p=model.top_p
            )
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Créer le résultat
            result = TaskResult(
                model_id=model.id,
                content=response.content,
                confidence=response.confidence,
                execution_time=execution_time,
                tokens_used=response.tokens_used,
                cost=response.cost,
                metadata=response.metadata
            )
            
            logger.debug(f"Résultat obtenu du modèle {model.id} pour la tâche {task.id}")
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Erreur lors de l'exécution sur le modèle {model.id}: {e}")
            raise
    
    def _prepare_prompt_for_model(self, task: Task, model: AIModel) -> str:
        """Préparer le prompt pour un modèle spécifique"""
        base_prompt = f"""
Tâche: {task.title}

Description: {task.description}

Type de tâche: {task.type.value}

Instructions:
{task.payload.get('instructions', '')}

Données d'entrée:
{task.payload.get('input_data', '')}

Veuillez fournir une réponse complète et précise.
"""
        
        # Personnalisation selon le modèle
        if model.type.value == 'claude':
            base_prompt += "\n\nRépondez de manière structurée et détaillée."
        elif model.type.value == 'openai_gpt':
            base_prompt += "\n\nSoyez créatif et informatif dans votre réponse."
        
        return base_prompt.strip()
    
    async def _health_monitor(self) -> None:
        """Moniteur de santé des modèles"""
        logger.info("Moniteur de santé démarré")
        
        while self.is_running:
            try:
                for model in self.models.values():
                    old_status = model.status
                    is_healthy = model.health_check()
                    
                    if model.status != old_status:
                        logger.info(f"Changement de statut pour {model.id}: {old_status} -> {model.status}")
                        self._trigger_event('model_status_changed', model=model)
                
                # Attendre avant la prochaine vérification
                await asyncio.sleep(30)  # Vérification toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur dans le moniteur de santé: {e}")
                await asyncio.sleep(5)
    
    async def _metrics_collector(self) -> None:
        """Collecteur de métriques"""
        logger.info("Collecteur de métriques démarré")
        
        while self.is_running:
            try:
                # Collecter les métriques système
                self.metrics.collect_system_metrics()
                
                # Collecter les métriques des modèles
                for model in self.models.values():
                    self.metrics.collect_model_metrics(model)
                
                # Collecter les métriques des tâches
                self.metrics.collect_task_metrics(len(self.active_tasks))
                
                # Attendre avant la prochaine collecte
                await asyncio.sleep(60)  # Collecte toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur dans le collecteur de métriques: {e}")
                await asyncio.sleep(10)
    
    async def _wait_for_task_completion(self, task_id: UUID) -> None:
        """Attendre qu'une tâche se termine"""
        while task_id in self.active_tasks:
            await asyncio.sleep(0.1)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtenir le statut du système"""
        return {
            'is_running': self.is_running,
            'active_tasks': len(self.active_tasks),
            'registered_models': len(self.models),
            'available_models': len([m for m in self.models.values() if m.is_available]),
            'queue_size': self.task_queue.qsize(),
            'models_status': {
                model_id: {
                    'status': model.status.value,
                    'is_available': model.is_available,
                    'success_rate': model.metrics.success_rate,
                    'efficiency_score': model.efficiency_score
                }
                for model_id, model in self.models.items()
            }
        }

