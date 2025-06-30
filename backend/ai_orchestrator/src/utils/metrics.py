"""
Collecteur de métriques pour le système d'orchestration
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field

from ..models.ai_model import AIModel


@dataclass
class SystemMetrics:
    """Métriques système"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    disk_percent: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0


@dataclass
class TaskMetrics:
    """Métriques des tâches"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    active_tasks: int = 0
    completed_tasks_last_hour: int = 0
    failed_tasks_last_hour: int = 0
    average_execution_time: float = 0.0
    queue_size: int = 0


class MetricsCollector:
    """
    Collecteur de métriques pour le monitoring du système
    """
    
    def __init__(self):
        self.system_metrics_history: List[SystemMetrics] = []
        self.task_metrics_history: List[TaskMetrics] = []
        self.model_metrics_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Limites de stockage
        self.max_history_size = 1000
        
        # Métriques réseau de base
        self._last_network_stats = psutil.net_io_counters()
        self._last_network_time = time.time()
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collecter les métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Mémoire
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Réseau
            current_network = psutil.net_io_counters()
            current_time = time.time()
            
            time_delta = current_time - self._last_network_time
            if time_delta > 0:
                network_sent_mb = (current_network.bytes_sent - self._last_network_stats.bytes_sent) / (1024 * 1024) / time_delta
                network_recv_mb = (current_network.bytes_recv - self._last_network_stats.bytes_recv) / (1024 * 1024) / time_delta
            else:
                network_sent_mb = 0.0
                network_recv_mb = 0.0
            
            self._last_network_stats = current_network
            self._last_network_time = current_time
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_percent=disk_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb
            )
            
            # Ajouter à l'historique
            self.system_metrics_history.append(metrics)
            self._trim_history(self.system_metrics_history)
            
            return metrics
            
        except Exception as e:
            print(f"Erreur lors de la collecte des métriques système: {e}")
            return SystemMetrics()
    
    def collect_task_metrics(self, active_tasks: int) -> TaskMetrics:
        """Collecter les métriques des tâches"""
        try:
            # Pour cette implémentation simplifiée, on utilise des valeurs de base
            metrics = TaskMetrics(
                active_tasks=active_tasks,
                completed_tasks_last_hour=0,  # À implémenter avec une vraie base de données
                failed_tasks_last_hour=0,     # À implémenter avec une vraie base de données
                average_execution_time=0.0,   # À calculer à partir de l'historique
                queue_size=0                  # À obtenir de l'orchestrateur
            )
            
            # Ajouter à l'historique
            self.task_metrics_history.append(metrics)
            self._trim_history(self.task_metrics_history)
            
            return metrics
            
        except Exception as e:
            print(f"Erreur lors de la collecte des métriques de tâches: {e}")
            return TaskMetrics()
    
    def collect_model_metrics(self, model: AIModel) -> Dict[str, Any]:
        """Collecter les métriques d'un modèle"""
        try:
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'model_id': model.id,
                'status': model.status.value,
                'is_available': model.is_available,
                'total_requests': model.metrics.total_requests,
                'successful_requests': model.metrics.successful_requests,
                'failed_requests': model.metrics.failed_requests,
                'success_rate': model.metrics.success_rate,
                'average_response_time': model.metrics.average_response_time,
                'total_tokens_used': model.metrics.total_tokens_used,
                'total_cost': model.metrics.total_cost,
                'efficiency_score': model.efficiency_score
            }
            
            # Ajouter à l'historique du modèle
            if model.id not in self.model_metrics_history:
                self.model_metrics_history[model.id] = []
            
            self.model_metrics_history[model.id].append(metrics)
            self._trim_history(self.model_metrics_history[model.id])
            
            return metrics
            
        except Exception as e:
            print(f"Erreur lors de la collecte des métriques du modèle {model.id}: {e}")
            return {}
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé des métriques système"""
        if not self.system_metrics_history:
            return {}
        
        recent_metrics = self.system_metrics_history[-10:]  # 10 dernières mesures
        
        return {
            'current': {
                'cpu_percent': recent_metrics[-1].cpu_percent,
                'memory_percent': recent_metrics[-1].memory_percent,
                'disk_percent': recent_metrics[-1].disk_percent
            },
            'average_last_10': {
                'cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                'memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                'network_sent_mb': sum(m.network_sent_mb for m in recent_metrics) / len(recent_metrics),
                'network_recv_mb': sum(m.network_recv_mb for m in recent_metrics) / len(recent_metrics)
            },
            'peak': {
                'cpu_percent': max(m.cpu_percent for m in recent_metrics),
                'memory_percent': max(m.memory_percent for m in recent_metrics)
            }
        }
    
    def get_model_summary(self, model_id: str) -> Dict[str, Any]:
        """Obtenir un résumé des métriques d'un modèle"""
        if model_id not in self.model_metrics_history or not self.model_metrics_history[model_id]:
            return {}
        
        recent_metrics = self.model_metrics_history[model_id][-10:]  # 10 dernières mesures
        latest = recent_metrics[-1]
        
        return {
            'current': {
                'status': latest['status'],
                'is_available': latest['is_available'],
                'total_requests': latest['total_requests'],
                'success_rate': latest['success_rate'],
                'efficiency_score': latest['efficiency_score']
            },
            'trends': {
                'requests_growth': self._calculate_growth_rate([m['total_requests'] for m in recent_metrics]),
                'success_rate_trend': self._calculate_trend([m['success_rate'] for m in recent_metrics]),
                'response_time_trend': self._calculate_trend([m['average_response_time'] for m in recent_metrics])
            }
        }
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Obtenir les alertes de performance"""
        alerts = []
        
        # Alertes système
        if self.system_metrics_history:
            latest_system = self.system_metrics_history[-1]
            
            if latest_system.cpu_percent > 80:
                alerts.append({
                    'type': 'system',
                    'level': 'warning',
                    'message': f'CPU élevé: {latest_system.cpu_percent:.1f}%'
                })
            
            if latest_system.memory_percent > 85:
                alerts.append({
                    'type': 'system',
                    'level': 'warning',
                    'message': f'Mémoire élevée: {latest_system.memory_percent:.1f}%'
                })
            
            if latest_system.disk_percent > 90:
                alerts.append({
                    'type': 'system',
                    'level': 'critical',
                    'message': f'Disque plein: {latest_system.disk_percent:.1f}%'
                })
        
        # Alertes modèles
        for model_id, metrics_list in self.model_metrics_history.items():
            if metrics_list:
                latest_model = metrics_list[-1]
                
                if latest_model['success_rate'] < 70:
                    alerts.append({
                        'type': 'model',
                        'level': 'warning',
                        'message': f'Taux de succès faible pour {model_id}: {latest_model["success_rate"]:.1f}%'
                    })
                
                if latest_model['average_response_time'] > 30:
                    alerts.append({
                        'type': 'model',
                        'level': 'warning',
                        'message': f'Temps de réponse élevé pour {model_id}: {latest_model["average_response_time"]:.1f}s'
                    })
        
        return alerts
    
    def _trim_history(self, history_list: List) -> None:
        """Limiter la taille de l'historique"""
        if len(history_list) > self.max_history_size:
            # Garder seulement les plus récents
            del history_list[:-self.max_history_size]
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculer le taux de croissance"""
        if len(values) < 2:
            return 0.0
        
        start_value = values[0]
        end_value = values[-1]
        
        if start_value == 0:
            return 0.0
        
        return ((end_value - start_value) / start_value) * 100
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculer la tendance (up, down, stable)"""
        if len(values) < 3:
            return 'stable'
        
        # Calculer la pente moyenne
        slopes = []
        for i in range(1, len(values)):
            slope = values[i] - values[i-1]
            slopes.append(slope)
        
        avg_slope = sum(slopes) / len(slopes)
        
        if avg_slope > 0.1:
            return 'up'
        elif avg_slope < -0.1:
            return 'down'
        else:
            return 'stable'
    
    def export_metrics(self, format: str = 'json') -> str:
        """Exporter les métriques"""
        data = {
            'system_metrics': [
                {
                    'timestamp': m.timestamp.isoformat(),
                    'cpu_percent': m.cpu_percent,
                    'memory_percent': m.memory_percent,
                    'disk_percent': m.disk_percent
                }
                for m in self.system_metrics_history
            ],
            'model_metrics': self.model_metrics_history
        }
        
        if format.lower() == 'json':
            import json
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Format non supporté: {format}")
    
    def clear_history(self) -> None:
        """Vider l'historique des métriques"""
        self.system_metrics_history.clear()
        self.task_metrics_history.clear()
        self.model_metrics_history.clear()

