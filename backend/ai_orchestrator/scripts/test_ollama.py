#!/usr/bin/env python3
"""
Test script pour la découverte Ollama
"""

import os
import sys
import asyncio

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.ollama_discovery import OllamaDiscoveryService


async def test_ollama_discovery():
    """Tester la découverte des modèles Ollama"""
    print("🔍 Test de découverte des modèles Ollama...")
    
    try:
        # Créer le service de découverte
        discovery_service = OllamaDiscoveryService()
        
        # Découvrir les modèles
        models = await discovery_service.discover_models()
        
        print(f"✅ {len(models)} modèles découverts:")
        
        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3)
            print(f"  - {name} ({size_gb:.1f}GB)")
        
        return len(models) > 0
        
    except Exception as e:
        print(f"❌ Erreur lors de la découverte: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_ollama_discovery())
    if success:
        print("🎉 Test de découverte Ollama réussi!")
    else:
        print("⚠️  Test de découverte Ollama échoué") 