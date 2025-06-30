"""
Gestionnaire de tâches
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
import json

from loguru import logger

from ..models.task import Task, TaskStatus, TaskType, Priority
from ..utils.config import Config
from ..utils.database import DatabaseManager


class TaskManager:
    """
    Gestionnaire des tâches
    
    Responsabilités:
    - Persistance des tâches
    - Recherche et filtrage des tâches
    - Gestion de l'historique
    - Statistiques et rapports
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.db = DatabaseManager(config)
        self.task_cache: Dict[UUID, Task] = {}
        self.cache_size = config.get('task_manager.cache_size', 1000)
        
        logger.info("TaskManager initialisé")
    
    async def save_task(self, task: Task) -> None:
        """Sauvegarder une tâche"""
        try:
            # Mettre à jour le cache
            self.task_cache[task.id] = task
            self._manage_cache_size()
            
            # Sauvegarder en base
            await self.db.save_task(task)
            
            logger.debug(f"Tâche {task.id} sauvegardée")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la tâche {task.id}: {e}")
            raise
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Récupérer une tâche par son ID"""
        # Vérifier le cache d'abord
        if task_id in self.task_cache:
            return self.task_cache[task_id]
        
        # Chercher en base
        try:
            task = await self.db.get_task(task_id)
            if task:
                self.task_cache[task_id] = task
            return task
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la tâche {task_id}: {e}")
            return None
    
    async def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        priority: Optional[Priority] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Task]:
        """Récupérer une liste de tâches avec filtres"""
        try:
            filters = {}
            if status:
                filters['status'] = status
            if task_type:
                filters['type'] = task_type
            if priority:
                filters['priority'] = priority
            if created_by:
                filters['created_by'] = created_by
            if start_date:
                filters['start_date'] = start_date
            if end_date:
                filters['end_date'] = end_date
            
            tasks = await self.db.get_tasks(filters, limit, offset)
            
            # Mettre à jour le cache
            for task in tasks:
                self.task_cache[task.id] = task
            
            return tasks
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des tâches: {e}")
            return []
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Supprimer une tâche"""
        try:
            # Supprimer du cache
            if task_id in self.task_cache:
                del self.task_cache[task_id]
            
            # Supprimer de la base
            result = await self.db.delete_task(task_id)
            
            if result:
                logger.info(f"Tâche {task_id} supprimée")
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la tâche {task_id}: {e}")
            return False
    
    async def get_task_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtenir les statistiques des tâches"""
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            stats = await self.db.get_task_statistics(start_date, end_date)
            
            return {
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'total_tasks': stats.get('total_tasks', 0),
                'completed_tasks': stats.get('completed_tasks', 0),
                'failed_tasks': stats.get('failed_tasks', 0),
                'cancelled_tasks': stats.get('cancelled_tasks', 0),
                'success_rate': stats.get('success_rate', 0.0),
                'average_execution_time': stats.get('average_execution_time', 0.0),
                'tasks_by_type': stats.get('tasks_by_type', {}),
                'tasks_by_priority': stats.get('tasks_by_priority', {}),
                'tasks_by_status': stats.get('tasks_by_status', {}),
                'busiest_hours': stats.get('busiest_hours', {}),
                'model_usage': stats.get('model_usage', {})
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {}
    
    async def cleanup_old_tasks(self, days_to_keep: int = 90) -> int:
        """Nettoyer les anciennes tâches"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Supprimer les tâches anciennes terminées
            deleted_count = await self.db.cleanup_old_tasks(cutoff_date)
            
            # Nettoyer le cache
            to_remove = []
            for task_id, task in self.task_cache.items():
                if task.created_at < cutoff_date and task.is_completed:
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self.task_cache[task_id]
            
            logger.info(f"{deleted_count} anciennes tâches supprimées")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")
            return 0
    
    async def get_active_tasks(self) -> List[Task]:
        """Récupérer toutes les tâches actives"""
        return await self.get_tasks(
            status=TaskStatus.IN_PROGRESS
        )
    
    async def get_pending_tasks(self) -> List[Task]:
        """Récupérer toutes les tâches en attente"""
        return await self.get_tasks(
            status=TaskStatus.PENDING
        )
    
    async def get_failed_tasks(self, limit: int = 50) -> List[Task]:
        """Récupérer les tâches échouées récentes"""
        return await self.get_tasks(
            status=TaskStatus.FAILED,
            limit=limit
        )
    
    async def retry_failed_task(self, task_id: UUID) -> bool:
        """Relancer une tâche échouée"""
        try:
            task = await self.get_task(task_id)
            if not task:
                logger.error(f"Tâche {task_id} non trouvée")
                return False
            
            if task.status != TaskStatus.FAILED:
                logger.error(f"La tâche {task_id} n'est pas en échec")
                return False
            
            if not task.can_retry():
                logger.error(f"La tâche {task_id} ne peut plus être relancée")
                return False
            
            # Préparer le retry
            task.prepare_retry()
            await self.save_task(task)
            
            logger.info(f"Tâche {task_id} préparée pour retry")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du retry de la tâche {task_id}: {e}")
            return False
    
    async def bulk_update_tasks(
        self,
        task_ids: List[UUID],
        updates: Dict[str, Any]
    ) -> int:
        """Mettre à jour plusieurs tâches en lot"""
        try:
            updated_count = 0
            
            for task_id in task_ids:
                task = await self.get_task(task_id)
                if task:
                    # Appliquer les mises à jour
                    for field, value in updates.items():
                        if hasattr(task, field):
                            setattr(task, field, value)
                    
                    task.updated_at = datetime.utcnow()
                    await self.save_task(task)
                    updated_count += 1
            
            logger.info(f"{updated_count} tâches mises à jour")
            return updated_count
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour en lot: {e}")
            return 0
    
    async def export_tasks(
        self,
        format: str = 'json',
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """Exporter les tâches dans un format donné"""
        try:
            # Récupérer les tâches avec filtres
            tasks = await self.get_tasks(**(filters or {}))
            
            if format.lower() == 'json':
                return json.dumps([task.dict() for task in tasks], indent=2, default=str)
            elif format.lower() == 'csv':
                # Implémentation CSV basique
                import csv
                import io
                
                output = io.StringIO()
                if tasks:
                    writer = csv.DictWriter(output, fieldnames=tasks[0].dict().keys())
                    writer.writeheader()
                    for task in tasks:
                        writer.writerow(task.dict())
                
                return output.getvalue()
            else:
                raise ValueError(f"Format non supporté: {format}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            return ""
    
    def _manage_cache_size(self) -> None:
        """Gérer la taille du cache"""
        if len(self.task_cache) > self.cache_size:
            # Supprimer les tâches les plus anciennes
            sorted_tasks = sorted(
                self.task_cache.items(),
                key=lambda x: x[1].updated_at
            )
            
            to_remove = len(self.task_cache) - self.cache_size + 100  # Marge
            for i in range(to_remove):
                task_id, _ = sorted_tasks[i]
                del self.task_cache[task_id]
    
    async def get_task_history(self, task_id: UUID) -> List[Dict[str, Any]]:
        """Récupérer l'historique d'une tâche"""
        task = await self.get_task(task_id)
        if task:
            return task.execution_log
        return []
    
    async def search_tasks(self, query: str, limit: int = 50) -> List[Task]:
        """Rechercher des tâches par texte"""
        try:
            # Recherche simple dans le titre et la description
            all_tasks = await self.get_tasks(limit=1000)  # Limite raisonnable
            
            matching_tasks = []
            query_lower = query.lower()
            
            for task in all_tasks:
                if (query_lower in task.title.lower() or 
                    query_lower in task.description.lower()):
                    matching_tasks.append(task)
                    
                    if len(matching_tasks) >= limit:
                        break
            
            return matching_tasks
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []

