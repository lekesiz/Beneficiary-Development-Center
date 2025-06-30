#!/usr/bin/env python3
"""
Test script pour vérifier les clés API
"""

import os
import sys
import asyncio

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.connectors.openai_connector import OpenAIConnector
from src.connectors.gemini_connector import GeminiConnector


async def test_openai():
    """Tester la clé API OpenAI"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'demo-key':
        print("❌ Clé API OpenAI non configurée")
        return False
    
    print("🔍 Test de la clé API OpenAI...")
    
    try:
        config = {
            'api_key': api_key,
            'model_name': 'gpt-4',
            'rate_limit_rpm': 500,
            'rate_limit_tpm': 150000
        }
        
        connector = OpenAIConnector("test-gpt-4", config)
        
        if await connector.connect():
            response = await connector.generate(
                prompt="Dis-moi bonjour en français",
                max_tokens=50
            )
            print(f"✅ OpenAI fonctionne: {response.content[:100]}...")
            await connector.disconnect()
            return True
        else:
            print("❌ Impossible de se connecter à OpenAI")
            return False
            
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return False


async def test_gemini():
    """Tester la clé API Gemini"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'demo-key':
        print("❌ Clé API Gemini non configurée")
        return False
    
    print("🔍 Test de la clé API Gemini...")
    
    try:
        config = {
            'api_key': api_key,
            'model_name': 'gemini-1.5-flash',
            'rate_limit_rpm': 300,
            'rate_limit_tpm': 100000
        }
        
        connector = GeminiConnector("test-gemini", config)
        
        if await connector.connect():
            response = await connector.generate(
                prompt="Dis-moi bonjour en français",
                max_tokens=50
            )
            print(f"✅ Gemini fonctionne: {response.content[:100]}...")
            await connector.disconnect()
            return True
        else:
            print("❌ Impossible de se connecter à Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Gemini: {e}")
        return False


async def main():
    """Test principal"""
    print("🚀 Test des clés API...")
    print("=" * 50)
    
    openai_ok = await test_openai()
    print()
    gemini_ok = await test_gemini()
    
    print("=" * 50)
    if openai_ok and gemini_ok:
        print("🎉 Toutes les clés API fonctionnent!")
    elif openai_ok:
        print("✅ OpenAI fonctionne, Gemini échoue")
    elif gemini_ok:
        print("✅ Gemini fonctionne, OpenAI échoue")
    else:
        print("❌ Aucune clé API ne fonctionne")
    
    print("\n📝 Pour configurer les clés API:")
    print("export OPENAI_API_KEY='votre_clé_openai'")
    print("export GOOGLE_API_KEY='votre_clé_gemini'")


if __name__ == "__main__":
    asyncio.run(main()) 