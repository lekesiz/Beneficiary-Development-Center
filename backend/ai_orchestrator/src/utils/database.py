"""
Gestionnaire de base de données simplifié pour la démonstration
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from ..models.task import Task
from .config import Config


class DatabaseManager:
    """
    Gestionnaire de base de données simplifié utilisant des fichiers JSON
    Pour une implémentation production, utiliser SQLAlchemy avec PostgreSQL/MySQL
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.data_dir = "data"
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        
        # Créer le dossier de données
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialiser le fichier de tâches s'il n'existe pas
        if not os.path.exists(self.tasks_file):
            self._save_json(self.tasks_file, [])
    
    async def save_task(self, task: Task) -> None:
        """Sauvegarder une tâche"""
        tasks = self._load_tasks()
        
        # Chercher si la tâche existe déjà
        task_dict = task.dict()
        task_dict['id'] = str(task.id)  # Convertir UUID en string
        
        existing_index = None
        for i, existing_task in enumerate(tasks):
            if existing_task.get('id') == task_dict['id']:
                existing_index = i
                break
        
        if existing_index is not None:
            # Mettre à jour la tâche existante
            tasks[existing_index] = task_dict
        else:
            # Ajouter une nouvelle tâche
            tasks.append(task_dict)
        
        self._save_json(self.tasks_file, tasks)
    
    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Récupérer une tâche par son ID"""
        tasks = self._load_tasks()
        
        for task_data in tasks:
            if task_data.get('id') == str(task_id):
                # Reconvertir en objet Task
                return self._dict_to_task(task_data)
        
        return None
    
    async def get_tasks(
        self, 
        filters: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Task]:
        """Récupérer une liste de tâches avec filtres"""
        tasks = self._load_tasks()
        
        # Appliquer les filtres
        filtered_tasks = []
        for task_data in tasks:
            if self._matches_filters(task_data, filters):
                filtered_tasks.append(self._dict_to_task(task_data))
        
        # Trier par date de création (plus récent en premier)
        filtered_tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Appliquer pagination
        start = offset
        end = offset + limit
        
        return filtered_tasks[start:end]
    
    async def delete_task(self, task_id: UUID) -> bool:
        """Supprimer une tâche"""
        tasks = self._load_tasks()
        
        for i, task_data in enumerate(tasks):
            if task_data.get('id') == str(task_id):
                del tasks[i]
                self._save_json(self.tasks_file, tasks)
                return True
        
        return False
    
    async def get_task_statistics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Obtenir les statistiques des tâches"""
        tasks = self._load_tasks()
        
        # Filtrer par date
        filtered_tasks = []
        for task_data in tasks:
            created_at = datetime.fromisoformat(task_data.get('created_at', ''))
            if start_date <= created_at <= end_date:
                filtered_tasks.append(task_data)
        
        if not filtered_tasks:
            return {}
        
        # Calculer les statistiques
        total_tasks = len(filtered_tasks)
        completed_tasks = len([t for t in filtered_tasks if t.get('status') == 'completed'])
        failed_tasks = len([t for t in filtered_tasks if t.get('status') == 'failed'])
        cancelled_tasks = len([t for t in filtered_tasks if t.get('status') == 'cancelled'])
        
        success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculer le temps d'exécution moyen
        execution_times = []
        for task_data in filtered_tasks:
            if task_data.get('started_at') and task_data.get('completed_at'):
                start = datetime.fromisoformat(task_data['started_at'])
                end = datetime.fromisoformat(task_data['completed_at'])
                execution_times.append((end - start).total_seconds())
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        # Statistiques par type
        tasks_by_type = {}
        for task_data in filtered_tasks:
            task_type = task_data.get('type', 'unknown')
            tasks_by_type[task_type] = tasks_by_type.get(task_type, 0) + 1
        
        # Statistiques par priorité
        tasks_by_priority = {}
        for task_data in filtered_tasks:
            priority = task_data.get('priority', 'unknown')
            tasks_by_priority[priority] = tasks_by_priority.get(priority, 0) + 1
        
        # Statistiques par statut
        tasks_by_status = {}
        for task_data in filtered_tasks:
            status = task_data.get('status', 'unknown')
            tasks_by_status[status] = tasks_by_status.get(status, 0) + 1
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'cancelled_tasks': cancelled_tasks,
            'success_rate': success_rate,
            'average_execution_time': avg_execution_time,
            'tasks_by_type': tasks_by_type,
            'tasks_by_priority': tasks_by_priority,
            'tasks_by_status': tasks_by_status,
            'busiest_hours': {},  # À implémenter si nécessaire
            'model_usage': {}     # À implémenter si nécessaire
        }
    
    async def cleanup_old_tasks(self, cutoff_date: datetime) -> int:
        """Nettoyer les anciennes tâches"""
        tasks = self._load_tasks()
        
        initial_count = len(tasks)
        
        # Filtrer les tâches à garder
        tasks_to_keep = []
        for task_data in tasks:
            created_at = datetime.fromisoformat(task_data.get('created_at', ''))
            status = task_data.get('status', '')
            
            # Garder les tâches récentes ou non terminées
            if created_at >= cutoff_date or status not in ['completed', 'failed', 'cancelled']:
                tasks_to_keep.append(task_data)
        
        # Sauvegarder les tâches restantes
        self._save_json(self.tasks_file, tasks_to_keep)
        
        return initial_count - len(tasks_to_keep)
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """Charger les tâches depuis le fichier JSON"""
        return self._load_json(self.tasks_file, [])
    
    def _load_json(self, file_path: str, default: Any = None) -> Any:
        """Charger un fichier JSON"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de {file_path}: {e}")
        
        return default if default is not None else {}
    
    def _save_json(self, file_path: str, data: Any) -> None:
        """Sauvegarder des données en JSON"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {file_path}: {e}")
    
    def _dict_to_task(self, task_data: Dict[str, Any]) -> Task:
        """Convertir un dictionnaire en objet Task"""
        # Convertir l'ID string en UUID
        task_data = task_data.copy()
        task_data['id'] = UUID(task_data['id'])
        
        # Convertir les dates string en datetime
        for date_field in ['created_at', 'updated_at', 'started_at', 'completed_at']:
            if task_data.get(date_field):
                task_data[date_field] = datetime.fromisoformat(task_data[date_field])
        
        return Task(**task_data)
    
    def _matches_filters(self, task_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Vérifier si une tâche correspond aux filtres"""
        for key, value in filters.items():
            if key == 'start_date':
                created_at = datetime.fromisoformat(task_data.get('created_at', ''))
                if created_at < value:
                    return False
            elif key == 'end_date':
                created_at = datetime.fromisoformat(task_data.get('created_at', ''))
                if created_at > value:
                    return False
            else:
                if task_data.get(key) != value:
                    return False
        
        return True

