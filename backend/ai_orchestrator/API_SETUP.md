# 🔑 Configuration des Clés API

Ce guide vous explique comment configurer les clés API pour utiliser les modèles d'IA externes.

## 📋 Prérequis

### 1. Clé API OpenAI
- Allez sur [OpenAI Platform](https://platform.openai.com/api-keys)
- Créez un compte ou connectez-vous
- Générez une nouvelle clé API
- Format: `sk-...`

### 2. Clé API Google Gemini
- Allez sur [Google AI Studio](https://makersuite.google.com/app/apikey)
- Connectez-vous avec votre compte Google
- Créez une nouvelle clé API
- Format: `AIza...`

## 🚀 Configuration Rapide

### Option 1: Script Automatique (Recommandé)

```bash
# Lancer le script de configuration
./setup_api_keys.sh

# Suivre les instructions à l'écran
# Entrez vos clés API quand demandé
```

### Option 2: Configuration Manuelle

```bash
# Créer le fichier .env
cat > .env << EOF
OPENAI_API_KEY=sk-votre_clé_openai_ici
GOOGLE_API_KEY=AIza_votre_clé_gemini_ici
EOF

# Charger les variables
source .env
```

### Option 3: Variables d'Environnement Système

```bash
# macOS/Linux
export OPENAI_API_KEY="sk-votre_clé_openai_ici"
export GOOGLE_API_KEY="AIza_votre_clé_gemini_ici"

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-votre_clé_openai_ici"
$env:GOOGLE_API_KEY="AIza_votre_clé_gemini_ici"
```

## ✅ Test de Configuration

```bash
# Tester les clés API
python test_api_keys.py
```

Résultat attendu:
```
🚀 Test des clés API...
==================================================
🔍 Test de la clé API OpenAI...
✅ OpenAI fonctionne: Bonjour! Comment puis-je vous aider aujourd'hui?...

🔍 Test de la clé API Gemini...
✅ Gemini fonctionne: Bonjour! Je suis ravi de vous aider...

==================================================
🎉 Toutes les clés API fonctionnent!
```

## 🎯 Lancement du Système

```bash
# Lancer l'orchestrateur avec tous les modèles
python main.py
```

Le système détectera automatiquement:
- ✅ **OpenAI GPT-4** (si clé configurée)
- ✅ **Google Gemini 1.5 Flash** (si clé configurée)
- ✅ **Ollama modèles locaux** (automatique)
- ✅ **Modèle de démonstration** (fallback)

## 🔧 Modèles Disponibles

### OpenAI
- **GPT-4** - Modèle principal
- **GPT-3.5-turbo** - Modèle rapide
- **GPT-4-turbo** - Modèle équilibré

### Google Gemini
- **Gemini 1.5 Flash** - Modèle principal
- **Gemini 1.5 Pro** - Modèle avancé
- **Gemini 1.0 Pro** - Modèle stable

### Ollama (Local)
- **Qwen 2.5 72B** - Modèle le plus puissant
- **CodeLlama 34B** - Spécialisé code
- **DeepSeek Coder** - Spécialisé code
- **Llama 3.2** - Modèle généraliste

## 🛡️ Sécurité

### Bonnes Pratiques
- ✅ Ne jamais commiter les clés API dans Git
- ✅ Utiliser des variables d'environnement
- ✅ Limiter les permissions des clés API
- ✅ Surveiller l'utilisation des clés

### Fichier .env
```bash
# Le fichier .env est automatiquement ignoré par Git
# Contenu sécurisé:
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

## 🔍 Dépannage

### Erreur: "Clé API non configurée"
```bash
# Vérifier que les variables sont définies
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY

# Recharger les variables
source .env
```

### Erreur: "Impossible de se connecter"
```bash
# Vérifier la validité des clés
python test_api_keys.py

# Vérifier la connectivité internet
curl -I https://api.openai.com
curl -I https://generativelanguage.googleapis.com
```

### Erreur: "Rate limit exceeded"
```bash
# Attendre quelques minutes
# Ou utiliser des modèles locaux (Ollama)
```

## 📊 Coûts

### OpenAI
- **GPT-4**: ~$0.03/1K tokens input, ~$0.06/1K tokens output
- **GPT-3.5-turbo**: ~$0.001/1K tokens input, ~$0.002/1K tokens output

### Google Gemini
- **Gemini 1.5 Flash**: ~$0.00025/1K tokens input, ~$0.0005/1K tokens output
- **Gemini 1.5 Pro**: ~$0.0035/1K tokens input, ~$0.0105/1K tokens output

### Ollama (Local)
- **Coût**: $0 (gratuit)
- **Ressources**: CPU/GPU local

## 🎉 Résultat

Une fois configuré, votre orchestrateur aura accès à:

```
========================================
STATUT DU SYSTÈME
========================================
En fonctionnement: True ✅
Modèles enregistrés: 15+ ✅
Modèles disponibles: 15+ ✅

--- Modèles Externes ---
gpt-4: ✅ OpenAI GPT-4
gemini-1.5-flash: ✅ Google Gemini

--- Modèles Locaux ---
ollama-qwen2.5:72b: ✅ Qwen 2.5 (44.2GB)
ollama-codellama:34b: ✅ CodeLlama (17.7GB)
... (12 autres modèles Ollama)

--- Modèle de Démonstration ---
demo-model: ✅ Simulation
========================================
```

Votre système d'orchestration d'IA est maintenant prêt pour la production! 🚀 