#!/bin/bash
# Script pour configurer les clés API

echo "🔧 Configuration des clés API pour l'orchestrateur d'IA"
echo "======================================================"

# Demander les clés API
echo -n "Entrez votre clé API OpenAI (sk-...): "
read OPENAI_KEY

echo -n "Entrez votre clé API Google Gemini (AIza...): "
read GOOGLE_KEY

# Vérifier que les clés ne sont pas vides
if [ -z "$OPENAI_KEY" ]; then
    echo "❌ Clé API OpenAI manquante"
    exit 1
fi

if [ -z "$GOOGLE_KEY" ]; then
    echo "❌ Clé API Google manquante"
    exit 1
fi

# Créer le fichier .env
cat > .env << EOF
# Clés API pour l'orchestrateur d'IA
OPENAI_API_KEY=$OPENAI_KEY
GOOGLE_API_KEY=$GOOGLE_KEY

# Configuration par défaut
ORCHESTRATOR_LOG_LEVEL=INFO
ORCHESTRATOR_MAX_MODELS=5
ORCHESTRATOR_TIMEOUT=300
EOF

echo "✅ Fichier .env créé avec succès!"
echo "📝 Pour charger les variables d'environnement:"
echo "   source .env"
echo ""
echo "🚀 Pour tester les clés API:"
echo "   python test_api_keys.py"
echo ""
echo "🎯 Pour lancer l'orchestrateur:"
echo "   python main.py" 