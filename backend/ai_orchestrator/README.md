# 🤖 Système d'Orchestration d'IA Avancé

Un système d'orchestration intelligent qui coordonne plusieurs modèles d'IA pour obtenir des résultats optimaux grâce à la validation croisée et au consensus.

## 🎯 Fonctionnalités Principales

### ✨ Orchestration Intelligente
- **Coordination Multi-Modèles** : Intégration de Claude, GPT-4, Gemini et modèles personnalisés
- **Validation Croisée** : Comparaison automatique des résultats entre modèles
- **Consensus Intelligent** : Sélection du meilleur résultat basée sur la confiance et la cohérence
- **Failover Automatique** : Basculement vers d'autres modèles en cas de défaillance

### 🔧 Architecture Robuste
- **Modularité** : Composants indépendants et interchangeables
- **Extensibilité** : Ajout facile de nouveaux modèles d'IA
- **Résilience** : Gestion d'erreurs avancée et retry automatique
- **Scalabilité** : Support pour traitement parallèle et haute charge

### 📊 Monitoring & Analytics
- **Métriques en Temps Réel** : Performance, coûts, taux de succès
- **Logging Avancé** : Traçabilité complète des décisions
- **Alertes Intelligentes** : Notifications automatiques des problèmes
- **Tableaux de Bord** : Visualisation des performances

### 🛡️ Sécurité & Fiabilité
- **Rate Limiting** : Respect des limites d'API
- **Validation des Entrées** : Vérification de sécurité des prompts
- **Audit Trail** : Journal complet des actions
- **Gestion des Coûts** : Suivi et optimisation des dépenses

## 🚀 Installation Rapide

### Prérequis
- Python 3.11+
- Clés API pour les services d'IA (optionnel pour la démo)

### Installation
```bash
# Cloner le projet
git clone <repository-url>
cd ai_orchestrator

# Installer les dépendances
pip install -r requirements.txt

# Configuration (optionnel)
export ANTHROPIC_API_KEY="votre_clé_claude"
export OPENAI_API_KEY="votre_clé_openai"

# Lancer la démonstration
python main.py
```

## 📖 Guide d'Utilisation

### Démarrage Rapide

```python
from src.orchestrator.engine import OrchestratorEngine
from src.models.task import Task, TaskType, Priority

# Initialiser l'orchestrateur
engine = OrchestratorEngine(config)

# Créer une tâche
task = Task(
    type=TaskType.ANALYSIS,
    priority=Priority.HIGH,
    title="Analyser un document",
    description="Analyser le contenu et extraire les points clés",
    payload={"input_data": "Votre texte ici..."},
    created_by="utilisateur"
)

# Soumettre la tâche
task_id = await engine.submit_task(task)

# Récupérer le résultat
result = await engine.get_task_status(task_id)
print(result.final_result)
```

### Configuration des Modèles

```python
from src.models.ai_model import AIModel, ModelType, Capability
from src.connectors.claude_connector import ClaudeConnector

# Configurer un modèle
model = AIModel(
    id="claude-sonnet",
    name="Claude 3 Sonnet",
    type=ModelType.CLAUDE,
    capabilities=[
        Capability.TEXT_GENERATION,
        Capability.ANALYSIS,
        Capability.CODE_GENERATION
    ]
)

# Créer le connecteur
connector = ClaudeConnector("claude-sonnet", {
    "api_key": "votre_clé",
    "model_name": "claude-3-sonnet-20240229"
})

# Enregistrer dans l'orchestrateur
engine.register_model(model)
engine.register_connector("claude-sonnet", connector)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Utilisateur                    │
├─────────────────────────────────────────────────────────────┤
│                     API REST / CLI                         │
├─────────────────────────────────────────────────────────────┤
│                  Moteur d'Orchestration                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Task Manager│ │Decision Eng.│ │   Workflow Engine   │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                   Connecteurs d'IA                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │
│  │ Claude  │ │ OpenAI  │ │ Gemini  │ │ Modèles Offline │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│              Couche de Données & Monitoring                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │  Database   │ │   Metrics   │ │      Logging        │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Structure du Projet

```
ai_orchestrator/
├── src/
│   ├── orchestrator/          # Moteur principal
│   │   ├── engine.py         # Orchestrateur principal
│   │   ├── task_manager.py   # Gestion des tâches
│   │   └── decision_engine.py # Validation croisée
│   ├── connectors/           # Connecteurs d'IA
│   │   ├── base.py          # Interface commune
│   │   ├── claude_connector.py
│   │   ├── openai_connector.py
│   │   └── demo_connector.py
│   ├── models/              # Modèles de données
│   │   ├── task.py         # Modèles de tâches
│   │   ├── ai_model.py     # Modèles d'IA
│   │   └── user.py         # Modèles utilisateur
│   └── utils/              # Utilitaires
│       ├── config.py       # Configuration
│       ├── metrics.py      # Métriques
│       └── text_analysis.py # Analyse de texte
├── tests/                  # Tests unitaires
├── docs/                   # Documentation
├── config/                 # Fichiers de configuration
├── main.py                # Point d'entrée principal
└── requirements.txt       # Dépendances
```

## 🔧 Configuration

### Variables d'Environnement

```bash
# Clés API
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Configuration système
ORCHESTRATOR_LOG_LEVEL=INFO
ORCHESTRATOR_MAX_MODELS=3
ORCHESTRATOR_TIMEOUT=300
DATABASE_PATH=data/orchestrator.db
```

### Fichier de Configuration (config.yaml)

```yaml
orchestrator:
  max_models_per_task: 3
  min_models_per_task: 1
  default_timeout: 300

decision_engine:
  min_consensus_score: 0.7
  similarity_threshold: 0.6

logging:
  level: INFO
  format: "{time} | {level} | {message}"
```

## 📊 Exemples d'Usage

### Analyse de Texte
```python
task = Task(
    type=TaskType.ANALYSIS,
    title="Analyse littéraire",
    description="Analyser le style et les thèmes",
    payload={
        "input_data": "Texte à analyser...",
        "instructions": "Identifier les figures de style"
    }
)
```

### Génération de Code
```python
task = Task(
    type=TaskType.CODE_GENERATION,
    title="Algorithme de tri",
    description="Implémenter quicksort en Python",
    payload={
        "language": "Python",
        "requirements": ["Commentaires", "Tests unitaires"]
    }
)
```

### Écriture Créative
```python
task = Task(
    type=TaskType.CREATIVE_WRITING,
    title="Histoire courte",
    description="Science-fiction optimiste",
    payload={
        "style": "Science-fiction",
        "length": "500 mots",
        "theme": "IA et collaboration"
    }
)
```

## 📈 Métriques et Monitoring

### Métriques Système
- **Performance** : Latence, débit, taux de succès
- **Ressources** : CPU, mémoire, réseau
- **Coûts** : Tokens utilisés, coût par requête
- **Qualité** : Scores de confiance, consensus

### Alertes Automatiques
- Taux d'erreur élevé (>10%)
- Latence excessive (>30s)
- Coûts anormaux
- Modèles indisponibles

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/

# Tests d'intégration
pytest tests/integration/

# Tests de performance
pytest tests/performance/

# Coverage
pytest --cov=src tests/
```

## 🚀 Déploiement

### Docker
```bash
# Build
docker build -t ai-orchestrator .

# Run
docker run -p 8000:8000 ai-orchestrator
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Production
- Utiliser un reverse proxy (nginx)
- Configurer SSL/TLS
- Mettre en place monitoring (Prometheus/Grafana)
- Sauvegardes automatiques

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📝 Roadmap

### Version 2.0
- [ ] Interface web React complète
- [ ] Support pour plus de modèles d'IA
- [ ] Workflows visuels
- [ ] API GraphQL
- [ ] Intégration Kubernetes native

### Version 2.1
- [ ] Auto-scaling intelligent
- [ ] ML pour optimisation des modèles
- [ ] Support multi-tenant
- [ ] Marketplace de connecteurs

## 🐛 Problèmes Connus

- Les modèles offline nécessitent une configuration manuelle
- Rate limiting basique (à améliorer)
- Interface web en développement

## 📞 Support

- **Documentation** : [docs/](docs/)
- **Issues** : GitHub Issues
- **Discussions** : GitHub Discussions
- **Email** : support@ai-orchestrator.com

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- Anthropic pour Claude
- OpenAI pour GPT-4
- Google pour Gemini
- La communauté open source

---

**Développé avec ❤️ pour l'avenir de l'IA collaborative**

