"""
Gestionnaire de configuration
"""

import os
from typing import Any, Dict, Optional
import yaml
import json


class Config:
    """
    Gestionnaire de configuration pour le système d'orchestration
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_data = {}
        self._load_default_config()
        
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
        
        # Charger les variables d'environnement
        self._load_env_variables()
    
    def _load_default_config(self):
        """Charger la configuration par défaut"""
        self.config_data = {
            'orchestrator': {
                'max_models_per_task': 3,
                'min_models_per_task': 1,
                'default_timeout': 300,
                'max_retries': 3
            },
            'decision_engine': {
                'min_consensus_score': 0.7,
                'min_confidence_threshold': 0.5,
                'similarity_threshold': 0.6,
                'max_discrepancies': 3
            },
            'task_manager': {
                'cache_size': 1000,
                'cleanup_days': 90
            },
            'logging': {
                'level': 'INFO',
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}',
                'rotation': '1 day',
                'retention': '30 days'
            },
            'database': {
                'type': 'sqlite',
                'path': 'data/orchestrator.db'
            }
        }
    
    def _load_config_file(self, config_file: str):
        """Charger un fichier de configuration"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    file_config = yaml.safe_load(f)
                elif config_file.endswith('.json'):
                    file_config = json.load(f)
                else:
                    raise ValueError(f"Format de fichier non supporté: {config_file}")
            
            # Fusionner avec la configuration par défaut
            self._merge_config(self.config_data, file_config)
            
        except Exception as e:
            print(f"Erreur lors du chargement du fichier de configuration {config_file}: {e}")
    
    def _load_env_variables(self):
        """Charger les variables d'environnement"""
        env_mappings = {
            'ORCHESTRATOR_LOG_LEVEL': 'logging.level',
            'ORCHESTRATOR_MAX_MODELS': 'orchestrator.max_models_per_task',
            'ORCHESTRATOR_TIMEOUT': 'orchestrator.default_timeout',
            'DATABASE_PATH': 'database.path'
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_value(config_path, value)
    
    def _merge_config(self, base: Dict, override: Dict):
        """Fusionner deux dictionnaires de configuration"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _set_nested_value(self, path: str, value: Any):
        """Définir une valeur dans un chemin imbriqué"""
        keys = path.split('.')
        current = self.config_data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Conversion automatique des types
        if isinstance(current.get(keys[-1]), int):
            try:
                value = int(value)
            except ValueError:
                pass
        elif isinstance(current.get(keys[-1]), float):
            try:
                value = float(value)
            except ValueError:
                pass
        elif isinstance(current.get(keys[-1]), bool):
            value = value.lower() in ('true', '1', 'yes', 'on')
        
        current[keys[-1]] = value
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Obtenir une valeur de configuration
        
        Args:
            path: Chemin vers la valeur (ex: 'orchestrator.max_models_per_task')
            default: Valeur par défaut si non trouvée
            
        Returns:
            La valeur de configuration ou la valeur par défaut
        """
        keys = path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any):
        """
        Définir une valeur de configuration
        
        Args:
            path: Chemin vers la valeur
            value: Nouvelle valeur
        """
        self._set_nested_value(path, value)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Obtenir une section complète de configuration
        
        Args:
            section: Nom de la section
            
        Returns:
            Dictionnaire de la section ou dictionnaire vide
        """
        return self.config_data.get(section, {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Retourner toute la configuration sous forme de dictionnaire"""
        return self.config_data.copy()
    
    def save_to_file(self, file_path: str, format: str = 'yaml'):
        """
        Sauvegarder la configuration dans un fichier
        
        Args:
            file_path: Chemin du fichier
            format: Format ('yaml' ou 'json')
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
            elif format.lower() == 'json':
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Format non supporté: {format}")
    
    def validate(self) -> bool:
        """
        Valider la configuration
        
        Returns:
            True si la configuration est valide
        """
        required_sections = ['orchestrator', 'decision_engine', 'task_manager']
        
        for section in required_sections:
            if section not in self.config_data:
                print(f"Section manquante dans la configuration: {section}")
                return False
        
        # Validations spécifiques
        if self.get('orchestrator.max_models_per_task', 0) <= 0:
            print("orchestrator.max_models_per_task doit être > 0")
            return False
        
        if not (0.0 <= self.get('decision_engine.min_consensus_score', 0.5) <= 1.0):
            print("decision_engine.min_consensus_score doit être entre 0.0 et 1.0")
            return False
        
        return True

